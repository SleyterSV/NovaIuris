"""Case-scoped preparation of a persisted legal result for browser printing."""
from io import BytesIO
import re

from flask import Blueprint, current_app, g, jsonify, request, send_file

from ..services.document_output import prepare_document
from ..services.case_pdf import render_case_pdf
from ..services.case_docx import render_case_docx
from ..services.court_pdf import render_court_pdf
from ..services.court_docx import render_court_docx
from ..services.court_report_content import court_filename
from ..services.runtime_security import authenticated_user_id, case_ownership
from ..utils.api_response import api_error


export_bp = Blueprint('export', __name__)
TASK_ID = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')


def _scoped_result(expected_tool='case'):
    data = request.get_json(silent=True)
    tool = data.get('tool') if isinstance(data, dict) else None
    if (not isinstance(data, dict) or set(data) != {'case_id', 'task_id', 'tool'}
            or tool != expected_tool or not isinstance(data.get('case_id'), str)
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
    task = repository.load_scoped(owner_id, case_id, task_id, task_type='legal_analysis')
    metadata = (task.get('metadata') or {}) if task else {}
    if (not task or metadata.get('tool') != tool
            or metadata.get('owner_id') != owner_id or metadata.get('case_id') != case_id):
        return None, api_error('TASK_NOT_FOUND', 'No se encontró la tarea.', g.request_id, 404)
    if task.get('status') != 'completed':
        return None, api_error('TASK_NOT_READY', 'La tarea aún no está completada.', g.request_id, 409)
    result = task.get('result')
    if (not isinstance(result, dict) or result.get('success') is not True
            or result.get('case_id') != case_id):
        return None, api_error('TASK_NOT_READY', 'El resultado canónico no está disponible.', g.request_id, 409)
    if tool == 'court':
        report = result.get('court_report_document')
        simulation = result.get('simulation')
        if (not isinstance(report, dict) or report.get('document_type') != 'court_simulation'
                or report.get('case_id') != case_id or not isinstance(report.get('sections'), list)
                or not report['sections'] or not isinstance(simulation, dict)
                or simulation.get('status') != 'ready'):
            return None, api_error('TASK_NOT_READY', 'El informe de simulación no está disponible.', g.request_id, 409)
    return result, None


@export_bp.route('/prepare', methods=['POST'])
def prepare_export():
    result, error = _scoped_result()
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
    return _generate_pdf('case')


@export_bp.route('/court/pdf', methods=['POST'])
def generar_court_pdf():
    return _generate_pdf('court')


def _generate_pdf(tool):
    result, error = _scoped_result(tool)
    if error:
        return error
    try:
        pdf = render_court_pdf(result) if tool == 'court' else render_case_pdf(result)
    except (ValueError, TypeError, KeyError):
        return api_error('TASK_NOT_READY', 'El informe no está disponible para exportación.', g.request_id, 409)
    except Exception as exc:
        current_app.logger.error('case_pdf_export_failed request_id=%s error_type=%s',
                                 g.request_id, type(exc).__name__)
        return api_error('EXPORT_NOT_AVAILABLE', 'No fue posible preparar el PDF.', g.request_id, 503)
    return send_file(BytesIO(pdf), mimetype='application/pdf', as_attachment=True,
                     download_name=court_filename(result, 'pdf') if tool == 'court'
                     else 'informe-juridico-novacase.pdf')


@export_bp.route('/docx', methods=['POST'])
def generar_docx():
    return _generate_docx('case')


@export_bp.route('/court/docx', methods=['POST'])
def generar_court_docx():
    return _generate_docx('court')


def _generate_docx(tool):
    result, error = _scoped_result(tool)
    if error:
        return error
    try:
        content = render_court_docx(result) if tool == 'court' else render_case_docx(result)
    except (ValueError, TypeError, KeyError):
        return api_error('TASK_NOT_READY', 'El informe no está disponible para exportación.', g.request_id, 409)
    except Exception as exc:
        current_app.logger.error('case_docx_export_failed request_id=%s error_type=%s',
                                 g.request_id, type(exc).__name__)
        return api_error('EXPORT_NOT_AVAILABLE', 'No fue posible preparar el DOCX.', g.request_id, 503)
    return send_file(BytesIO(content),
                     mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                     as_attachment=True, download_name=court_filename(result, 'docx')
                     if tool == 'court' else 'informe-juridico-novacase.docx')
