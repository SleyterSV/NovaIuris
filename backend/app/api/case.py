"""Canonical case endpoint and process-local case/court jobs."""
from uuid import uuid4
import re
from threading import Lock
_pipeline_lock = Lock()
from flask import Blueprint, request, jsonify, current_app, g
from ..utils.api_response import api_error
from ..utils.case_contract import normalize_case_result
from ..services.novacourt_pipeline_service import NovaCourtPipelineService
from ..services.runtime_security import owns_case, authenticated_user_id

case_bp = Blueprint('case', __name__)

def services():
    from ..services.case_service import CaseService
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
    data = pipeline().status(task_id)
    case_id = request.args.get('case_id')
    if not data or not case_id or data['case_id'] != case_id or not owns_case(case_id) or data.get('owner_id') != authenticated_user_id():
        return api_error('TASK_NOT_FOUND', 'No se encontró la tarea.', g.request_id, 404)
    return jsonify(success=True, **public_task(data))

@case_bp.route('/tasks/<task_id>/cancel', methods=['POST'])
def cancel_task(task_id):
    manager = pipeline()
    data = manager.status(task_id)
    payload = request.get_json(silent=True)
    case_id = payload.get('case_id') if isinstance(payload, dict) else None
    if not data or not case_id or data['case_id'] != case_id or not owns_case(case_id) or data.get('owner_id') != authenticated_user_id():
        return api_error('TASK_NOT_FOUND', 'No se encontró la tarea.', g.request_id, 404)
    manager.tasks.cancel_task(task_id)
    return jsonify(success=True, **public_task(manager.status(task_id)))
