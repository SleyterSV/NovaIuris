"""Case-scoped preparation of a persisted legal result for browser printing."""
import re

from flask import Blueprint, current_app, g, jsonify, request

from ..services.document_output import prepare_document
from ..services.runtime_security import authenticated_user_id, case_ownership
from ..utils.api_response import api_error


export_bp = Blueprint('export', __name__)
TASK_ID = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')


@export_bp.route('/prepare', methods=['POST'])
def prepare_export():
    data = request.get_json(silent=True)
    if (not isinstance(data, dict) or set(data) != {'case_id', 'task_id', 'tool'}
            or data.get('tool') != 'case' or not isinstance(data.get('case_id'), str)
            or not isinstance(data.get('task_id'), str)
            or not TASK_ID.fullmatch(data['task_id'])):
        return api_error('INVALID_REQUEST', 'Solicite un caso y una tarea válidos.', g.request_id, 400)

    case_id, task_id = data['case_id'], data['task_id']
    owner_id = authenticated_user_id()
    if not case_ownership().owned(case_id, owner_id, create=False):
        return api_error('CASE_NOT_FOUND', 'No se encontró el caso.', g.request_id, 404)

    repository = current_app.extensions.get('task_repository')
    if repository is None:
        return api_error('SERVICE_UNAVAILABLE', 'La exportación no está disponible.', g.request_id, 503)
    task = repository.load_scoped(owner_id, case_id, task_id)
    metadata = (task.get('metadata') or {}) if task else {}
    if (not task or metadata.get('tool') != 'case'
            or metadata.get('owner_id') != owner_id or metadata.get('case_id') != case_id):
        return api_error('TASK_NOT_FOUND', 'No se encontró la tarea.', g.request_id, 404)
    if task.get('status') != 'completed':
        return api_error('TASK_NOT_READY', 'La tarea aún no está completada.', g.request_id, 409)
    result = task.get('result')
    if (not isinstance(result, dict) or result.get('success') is not True
            or result.get('case_id') != case_id):
        return api_error('TASK_NOT_READY', 'El resultado canónico no está disponible.', g.request_id, 409)
    try:
        document = prepare_document(case_id, result, 'case')
    except (ValueError, TypeError, KeyError):
        current_app.logger.warning('export_canonical_result_invalid request_id=%s', g.request_id)
        return api_error('TASK_NOT_READY', 'El resultado canónico no está disponible.', g.request_id, 409)
    return jsonify(success=True, document=document)


@export_bp.route('/pdf', methods=['POST'])
def generar_pdf():
    return api_error('EXPORT_NOT_AVAILABLE', 'La exportación PDF no está disponible.', g.request_id, 501)
