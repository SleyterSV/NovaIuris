"""Canonical case endpoint and process-local case/court jobs."""
from uuid import UUID, NAMESPACE_URL, uuid4, uuid5
import re
from threading import Lock
_pipeline_lock = Lock()
from flask import Blueprint, request, jsonify, current_app, g
from ..utils.api_response import api_error
from ..utils.case_contract import normalize_case_result
from ..services.novacourt_pipeline_service import NovaCourtPipelineService
from ..services.runtime_security import owns_case, authenticated_user_id, case_ownership
from ..services.case_public_handoff import normalize_handoff_references, resolve_handoff_references
from ..services.legal_repository_v2 import LegalRepositoryV2
from ..services.case_service import CaseService

case_bp = Blueprint('case', __name__)


@case_bp.route('/cases', methods=['GET'])
def owned_cases():
    return jsonify(success=True, cases=case_ownership().list_owned(authenticated_user_id()))


@case_bp.route('/case/handoff', methods=['POST'])
def start_public_source_handoff():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return api_error('INVALID_CASE', 'Debe enviar un objeto JSON válido.', g.request_id, 400)
    mode = data.get('case_mode')
    if mode not in {'new', 'existing'} or (mode == 'new' and data.get('case_id')) or (mode == 'existing' and not data.get('case_id')):
        return api_error('INVALID_CASE', 'Seleccione un caso nuevo o uno existente.', g.request_id, 400)
    try:
        text, case_id, document_ids = input_case()
        if mode == 'new' and document_ids:
            raise ValueError('Un caso nuevo no puede reutilizar documentos de otro caso.')
        references = normalize_handoff_references(data.get('public_source_references'))
        handoff_request_id = str(UUID(str(data['handoff_request_id'])))
    except (KeyError, TypeError, ValueError) as error:
        return api_error('INVALID_CASE', str(error), g.request_id, 400)
    owner_id = authenticated_user_id()
    if mode == 'new':
        case_id = str(uuid5(NAMESPACE_URL, f'novacase-handoff:{owner_id}:{handoff_request_id}'))
    if mode == 'existing' and not case_ownership().owned(case_id, owner_id, create=False):
        return api_error('CASE_NOT_FOUND', 'No se encontró el caso.', g.request_id, 404)
    try:
        # Validate published V2 identity before scheduling any work. Analysis resolves it again.
        resolve_handoff_references(LegalRepositoryV2(), references)
    except Exception:
        return api_error('PUBLIC_SOURCE_UNAVAILABLE', 'La fuente jurídica no está disponible o no coincide con la referencia.', g.request_id, 422)
    manager = pipeline()
    if (manager.tasks.active_count(owner_id) >= current_app.config['ACTIVE_TASKS_PER_USER']
            and not manager.tasks.find_handoff(owner_id, handoff_request_id)):
        return api_error('RATE_LIMITED', 'Hay demasiadas tareas activas.', g.request_id, 429)
    if mode == 'new' and not case_ownership().owned(case_id, owner_id, create=True):
        return api_error('CASE_NOT_FOUND', 'No fue posible crear el caso.', g.request_id, 409)
    try:
        task_id = manager.start(text, case_id=case_id, tool='case', document_ids=document_ids,
                                owner_id=owner_id, public_source_references=references,
                                handoff_request_id=handoff_request_id)
    except ValueError as error:
        return api_error('CASE_MISMATCH', str(error), g.request_id, 409)
    return jsonify(success=True, task_id=task_id, case_id=case_id, tool='case'), 202

def services():
    # Load the NovaCase import graph with the app, before serving any request.
    # A long-lived worker must never lazily mix old in-memory source contracts
    # with a newer CaseService read from disk on its first /case/tasks call.
    from ..services.novacourt_graph_service import NovaCourtGraphService
    from ..services.novacourt_simulation_service import NovaCourtSimulationService
    return (current_app.config.get('CASE_SERVICE_FACTORY', CaseService)(),
            current_app.config.get('GRAPH_SERVICE_FACTORY', NovaCourtGraphService)(),
            current_app.config.get('SIMULATION_SERVICE_FACTORY', NovaCourtSimulationService)())

def pipeline():
    with _pipeline_lock:
        if 'legal_pipeline' not in current_app.extensions:
            current_app.extensions['legal_pipeline'] = NovaCourtPipelineService(
                *services(), task_manager=current_app.extensions.get('task_manager'))
    return current_app.extensions['legal_pipeline']


def public_task(data):
    payload = dict(data)
    payload.pop('owner_id', None)
    payload['metadata'] = {key: value for key, value in (payload.get('metadata') or {}).items()
                           if key != 'owner_id'}
    return payload

def input_case():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        raise ValueError('Debe enviar un objeto JSON válido.')
    text = data.get('case_text') or data.get('case')
    if not isinstance(text, str) or not 50 <= len(text.strip()) <= 50000:
        raise ValueError('El caso debe contener entre 50 y 50.000 caracteres.')
    case_id = data.get('case_id') or str(uuid4())
    if not isinstance(case_id, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}", case_id) or ".." in case_id:
        raise ValueError('El identificador de caso no es válido.')
    document_ids = data.get('document_ids') or []
    maximum = current_app.config.get('CASE_DOCUMENT_MAX_FILES', 20)
    if not isinstance(document_ids, list) or len(document_ids) > maximum or any(
        not isinstance(item, str) or not item.strip() or len(item) > 128 for item in document_ids
    ):
        raise ValueError('La lista de documentos del caso no es válida.')
    if len(set(document_ids)) != len(document_ids):
        raise ValueError('La lista de documentos contiene identificadores repetidos.')
    return text.strip(), case_id, document_ids

@case_bp.route('/case', methods=['POST'])
def analyze_case():
    if current_app.config.get('APP_ENV') == 'production':
        return api_error('LEGACY_DISABLED', 'Use tareas persistentes para analizar casos.', g.request_id, 410)
    try:
        text, case_id, _ = input_case()
    except ValueError as error:
        return api_error('INVALID_CASE', str(error), g.request_id, 400)
    if not owns_case(case_id, create=True):
        return api_error('CASE_NOT_FOUND', 'No se encontró el caso.', g.request_id, 404)
    service, _, _ = services()
    result = normalize_case_result(service.analyze_case(text, case_id=case_id))
    if not result.get('success'):
        return api_error('CASE_FAILED', 'No fue posible completar el análisis jurídico.', g.request_id, 422)
    if result.get('case_id') != case_id:
        raise ValueError('Case identity mismatch')
    return jsonify(result)

@case_bp.route('/case/tasks', methods=['POST'])
@case_bp.route('/novacourt/analyze', methods=['POST'])
def start_analysis():
    try:
        text, case_id, document_ids = input_case()
    except ValueError as error:
        return api_error('INVALID_CASE', str(error), g.request_id, 400)
    if not owns_case(case_id, create=True):
        return api_error('CASE_NOT_FOUND', 'No se encontró el caso.', g.request_id, 404)
    tool = 'court' if request.path.endswith('/novacourt/analyze') else 'case'
    manager = pipeline()
    if manager.tasks.active_count(authenticated_user_id()) >= current_app.config['ACTIVE_TASKS_PER_USER']:
        return api_error('RATE_LIMITED', 'Hay demasiadas tareas activas.', g.request_id, 429)
    reuse_task_id = (request.get_json(silent=True) or {}).get('reuse_task_id')
    if reuse_task_id is not None and (tool != 'court' or not isinstance(reuse_task_id, str) or
                                      not re.fullmatch(r'[a-f0-9-]{36}', reuse_task_id)):
        return api_error('INVALID_CASE', 'La referencia al análisis previo no es válida.', g.request_id, 400)
    try:
        task_id = manager.start(text, case_id=case_id, tool=tool, document_ids=document_ids,
                                owner_id=authenticated_user_id(),
                                reuse_task_id=reuse_task_id)
    except ValueError as error:
        return api_error('CASE_MISMATCH', str(error), g.request_id, 409)
    return jsonify(success=True, task_id=task_id, case_id=case_id, tool=tool), 202

@case_bp.route('/tasks/<task_id>', methods=['GET'])
@case_bp.route('/novacourt/results/<task_id>', methods=['GET'])
def task_status(task_id):
    case_id = request.args.get('case_id')
    court_only = request.path.startswith('/api/novacourt/results/')
    data = (pipeline().scoped_status(authenticated_user_id(), case_id, task_id,
                                    tool='court' if court_only else None)
            if case_id and owns_case(case_id) else None)
    if not data:
        return api_error('TASK_NOT_FOUND', 'No se encontró la tarea.', g.request_id, 404)
    return jsonify(success=True, **public_task(data))

@case_bp.route('/tasks/<task_id>/cancel', methods=['POST'])
def cancel_task(task_id):
    manager = pipeline()
    payload = request.get_json(silent=True)
    case_id = payload.get('case_id') if isinstance(payload, dict) else None
    data = (manager.scoped_status(authenticated_user_id(), case_id, task_id)
            if case_id and owns_case(case_id) else None)
    if not data:
        return api_error('TASK_NOT_FOUND', 'No se encontró la tarea.', g.request_id, 404)
    manager.tasks.cancel_task(task_id)
    return jsonify(success=True, **public_task(manager.status(task_id)))
