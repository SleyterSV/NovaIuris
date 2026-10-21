"""Case-scoped preparation of a persisted legal result for browser printing."""
from io import BytesIO
import re

from flask import Blueprint, current_app, g, jsonify, request, send_file

from ..services.document_output import prepare_document
from ..services.case_pdf import render_case_pdf
from ..services.runtime_security import authenticated_user_id, case_ownership
from ..utils.api_response import api_error


export_bp = Blueprint('export', __name__)
TASK_ID = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')


def _scoped_case_result():
    data = request.get_json(silent=True)
    if (not isinstance(data, dict) or set(data) != {'case_id', 'task_id', 'tool'}
            or data.get('tool') != 'case' or not isinstance(data.get('case_id'), str)
            or not isinstance(data.get('task_id'), str)
            or not TASK_ID.fullmatch(data['task_id'])):
        return None, api_error('INVALID_REQUEST', 'Solicite un caso y una tarea válidos.', g.request_id, 400)

    case_id, task_id = data['case_id'], data['task_id']
    owner_id = authenticated_user_id()
    if not case_ownership().owned(case_id, owner_id, create=False):
        return None, api_error('CASE_NOT_FOUND', 'No se encontró el caso.', g.request_id, 404)

    repository = current_app.extensions.get('task_repository')
    if repository is None:
        return None, api_error('SERVICE_UNAVAILABLE', 'La exportación no está disponible.', g.request_id, 503)
    task = repository.load_scoped(owner_id, case_id, task_id)
    metadata = (task.get('metadata') or {}) if task else {}
    if (not task or metadata.get('tool') != 'case'
            or metadata.get('owner_id') != owner_id or metadata.get('case_id') != case_id):
        return None, api_error('TASK_NOT_FOUND', 'No se encontró la tarea.', g.request_id, 404)
    if task.get('status') != 'completed':
        return None, api_error('TASK_NOT_READY', 'La tarea aún no está completada.', g.request_id, 409)
    result = task.get('result')
    if (not isinstance(result, dict) or result.get('success') is not True
            or result.get('case_id') != case_id):
        return None, api_error('TASK_NOT_READY', 'El resultado canónico no está disponible.', g.request_id, 409)
    return result, None


@export_bp.route('/prepare', methods=['POST'])
def prepare_export():
    result, error = _scoped_case_result()
    if error:
        return error
    try:
        document = prepare_document(result['case_id'], result, 'case')
    except (ValueError, TypeError, KeyError):
        current_app.logger.warning('export_canonical_result_invalid request_id=%s', g.request_id)
        return api_error('TASK_NOT_READY', 'El resultado canónico no está disponible.', g.request_id, 409)
    return jsonify(success=True, document=document)


@export_bp.route('/pdf', methods=['POST'])
def generar_pdf():
    result, error = _scoped_case_result()
    if error:
        return error
    try:
        pdf = render_case_pdf(result)
    except (ValueError, TypeError, KeyError):
        return api_error('TASK_NOT_READY', 'El informe no está disponible para exportación.', g.request_id, 409)
    except Exception:
        current_app.logger.exception('case_pdf_export_failed request_id=%s', g.request_id)
        return api_error('EXPORT_NOT_AVAILABLE', 'No fue posible preparar el PDF.', g.request_id, 503)
    return send_file(BytesIO(pdf), mimetype='application/pdf', as_attachment=True,
                     download_name='informe-juridico-novacase.pdf')
