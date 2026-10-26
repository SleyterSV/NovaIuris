"""Upload and case-scoped retrieval metadata for private legal documents."""
import re
import tempfile
import shutil
import os
import hashlib
from io import BytesIO
from uuid import uuid4
from pathlib import Path
from flask import Blueprint, current_app, jsonify, g, request, send_file
from ..services.case_corpus import CaseCorpusRepository, DocumentError, DocumentIngestionService, safe_filename
from ..utils.api_response import api_error
from ..services.runtime_security import owns_case
from ..services.runtime_security import authenticated_user_id

documents_bp = Blueprint("case_documents", __name__)
CASE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")


def corpus_repository():
    if "case_corpus_repository" not in current_app.extensions:
        factory = current_app.config.get("CASE_CORPUS_REPOSITORY_FACTORY")
        current_app.extensions["case_corpus_repository"] = (
            factory() if factory else CaseCorpusRepository(current_app.config["CASE_CORPUS_DB_PATH"]))
        # Corpus deletion requires an explicit lifecycle operation; age alone
        # must not silently delete private source material at first request.
    return current_app.extensions["case_corpus_repository"]


def ingestion_service():
    config = current_app.config
    embedding_factory = config.get("DOCUMENT_EMBEDDING_FACTORY")
    if embedding_factory:
        embedding = embedding_factory()
    else:
        from ..services.embedding_service import EmbeddingService
        embedding = EmbeddingService()
    return DocumentIngestionService(corpus_repository(), embedding,
        max_file_size=config["CASE_DOCUMENT_MAX_FILE_BYTES"],
        max_total_size=config["CASE_DOCUMENT_MAX_CASE_BYTES"],
        max_files=config["CASE_DOCUMENT_MAX_FILES"],
        max_uncompressed=config["CASE_DOCUMENT_MAX_UNCOMPRESSED_BYTES"],
        max_pages=config["CASE_DOCUMENT_MAX_PAGES"],
        chunk_tokens=config["CASE_DOCUMENT_CHUNK_TOKENS"],
        chunk_overlap=config["CASE_DOCUMENT_CHUNK_OVERLAP"],
        chunk_max_chars=config["CASE_DOCUMENT_CHUNK_MAX_CHARS"],
        batch_size=config["CASE_DOCUMENT_EMBEDDING_BATCH_SIZE"],
        ocr_min_chars=config["CASE_DOCUMENT_OCR_MIN_PAGE_CHARACTERS"])


def application_repository():
    return current_app.extensions.get('application_repository')


def case_document_listing(case_id):
    local = corpus_repository().list_documents(case_id)
    repository = application_repository()
    if not repository:
        return local
    stored = repository.list_case_documents(authenticated_user_id(), case_id)
    if stored is None:
        return None
    by_id = {item['document_id']: item for item in local}
    listed = []
    for item in stored:
        manifest = by_id.pop(item['id'], {})
        state = item['processing_status']
        listed.append({**manifest, 'document_id':item['id'], 'case_id':case_id,
            'filename':item['original_filename'], 'display_name':Path(item['original_filename']).stem,
            'mime_type':item['mime_type'], 'size_bytes':item['size_bytes'], 'sha256':item.get('sha256'),
            'status':manifest.get('status') if state == 'ready' and manifest else state,
            'processing_status':state, 'created_at':item['created_at'], 'updated_at':item['updated_at']})
    # Retain visibility of legacy text indexes during migration; they do not contain original files.
    listed.extend(by_id.values())
    return listed


def _valid_case_id(case_id):
    return bool(CASE_ID.fullmatch(case_id)) and ".." not in case_id


@documents_bp.route("/cases/<case_id>/documents", methods=["POST"])
def upload_documents(case_id):
    if not owns_case(case_id, create=True):
        return api_error('CASE_NOT_FOUND', 'No se encontró el caso.', g.request_id, 404)
    existing_manager = current_app.extensions.get('document_task_manager')
    if existing_manager and existing_manager.active_count(authenticated_user_id()) >= current_app.config['ACTIVE_TASKS_PER_USER']:
        return api_error('RATE_LIMITED', 'Hay demasiadas tareas activas.', g.request_id, 429)
    if not _valid_case_id(case_id):
        return api_error("INVALID_CASE_ID", "El identificador de caso no es válido.", g.request_id, 400)
    files = request.files.getlist("files") or ([request.files["file"]] if "file" in request.files else [])
    files = [item for item in files if item and item.filename]
    if not files:
        return api_error("EMPTY_UPLOAD", "Selecciona al menos un archivo.", g.request_id, 400)
    if len(files) > current_app.config["CASE_DOCUMENT_MAX_FILES"]:
        return api_error("TOO_MANY_FILES", "Hay demasiados archivos en una sola solicitud.", g.request_id, 400)
    replacement_id = request.form.get("replaces_document_id")
    if replacement_id and len(files) != 1:
        return api_error("INVALID_REPLACEMENT", "Reemplaza un documento por solicitud.", g.request_id, 400)
    staging_directory = tempfile.mkdtemp(prefix="nova-document-task-")
    staged = []
    repository = application_repository()
    if current_app.config.get('APP_ENV') == 'production' and not repository:
        shutil.rmtree(staging_directory, ignore_errors=True)
        return api_error('PERSISTENCE_UNAVAILABLE', 'El almacenamiento privado no está disponible.', g.request_id, 503)
    created_document_ids = []
    try:
        staged_bytes = 0
        for uploaded in files:
            filename = safe_filename(uploaded.filename)
            extension = Path(filename).suffix.lower()
            stream = uploaded.stream
            stream.seek(0, os.SEEK_END)
            file_size = stream.tell()
            stream.seek(0)
            if file_size == 0:
                staged.append((None, filename, {"code":"empty_document", "message":"El archivo está vacío."}))
                continue
            if file_size > current_app.config["CASE_DOCUMENT_MAX_FILE_BYTES"]:
                staged.append((None, filename, {"code":"file_too_large", "message":"El archivo supera el límite configurado."}))
                continue
            if staged_bytes + file_size > current_app.config["CASE_DOCUMENT_MAX_CASE_BYTES"]:
                staged.append((None, filename, {"code":"case_too_large", "message":"La suma de archivos de esta solicitud supera el límite configurado."}))
                continue
            path = Path(staging_directory) / f"{len(staged)}-{uuid4().hex}{extension}"
            with path.open("wb") as target:
                shutil.copyfileobj(stream, target, length=1024 * 1024)
            document_id = None
            if extension not in DocumentIngestionService.SUPPORTED:
                staged.append((None, filename, {"code":"unsupported_format", "message":"Formatos compatibles: PDF, DOCX y TXT."}))
                path.unlink(missing_ok=True)
                continue
            if repository:
                digest = hashlib.sha256()
                with path.open('rb') as source:
                    for block in iter(lambda: source.read(1024 * 1024), b''):
                        digest.update(block)
                existing = corpus_repository().find_hash(case_id, digest.hexdigest())
                if existing:
                    document_id = existing['document_id']
                stored_document = (repository.get_case_document(authenticated_user_id(), case_id, document_id)
                                   if document_id else None)
                if not stored_document:
                    if not document_id:
                        document_id = str(uuid4())
                    mime_type = {'.pdf':'application/pdf', '.docx':'application/vnd.openxmlformats-officedocument.wordprocessingml.document', '.txt':'text/plain'}[extension]
                    with path.open('rb') as source:
                        repository.store_case_document(authenticated_user_id(), case_id, document_id,
                            filename, mime_type, file_size, digest.hexdigest(), source)
                    created_document_ids.append(document_id)
            staged.append((path, filename, None, document_id))
            staged_bytes += file_size
        service = ingestion_service()
        manager = current_app.extensions.get("document_task_manager")
        if manager is None:
            factory = current_app.config.get("DOCUMENT_TASK_MANAGER_FACTORY")
            from ..services.document_tasks import DocumentTaskManager
            manager = current_app.extensions["document_task_manager"] = (
                factory() if factory else DocumentTaskManager(
                    current_app.config["DOCUMENT_STAGING_MAX_AGE_SECONDS"],
                    repository=current_app.extensions.get('document_task_repository')
                )
            )
        if repository:
            manager.document_result_callback = repository.update_case_document_status
        task_id = manager.start(case_id, staged, service, staging_directory, replacement_id,
                                owner_id=authenticated_user_id())
        return jsonify(success=True, case_id=case_id, task_id=task_id, status="queued",
                       total_documents=len(staged)), 202
    except DocumentError as error:
        if repository:
            for document_id in created_document_ids:
                try:
                    repository.delete_case_document(authenticated_user_id(), case_id, document_id)
                except Exception:
                    current_app.logger.warning("document_storage_compensation_failed case_id=%s document_id=%s",
                                               case_id, document_id)
        shutil.rmtree(staging_directory, ignore_errors=True)
        return api_error(error.code.upper(), error.message, g.request_id, 400)
    except Exception as error:
        current_app.logger.warning("document_task_start_failed case_id=%s error_type=%s",
                                   case_id, type(error).__name__)
        if repository:
            for document_id in created_document_ids:
                try:
                    repository.delete_case_document(authenticated_user_id(), case_id, document_id)
                except Exception:
                    current_app.logger.warning("document_storage_compensation_failed case_id=%s document_id=%s",
                                               case_id, document_id)
        shutil.rmtree(staging_directory, ignore_errors=True)
        return api_error("INGESTION_FAILED", "No se pudo iniciar la ingesta documental.", g.request_id, 500)


@documents_bp.route("/cases/<case_id>/document-tasks/<task_id>", methods=["GET"])
def document_task_status(case_id, task_id):
    if not owns_case(case_id):
        return api_error('CASE_NOT_FOUND', 'No se encontró el caso.', g.request_id, 404)
    if not _valid_case_id(case_id):
        return api_error("INVALID_CASE_ID", "El identificador de caso no es válido.", g.request_id, 400)
    manager = current_app.extensions.get("document_task_manager")
    task = manager.status(case_id, task_id, authenticated_user_id()) if manager else None
    if task is None:
        return api_error("TASK_NOT_FOUND", "No se encontró la tarea documental de este caso.", g.request_id, 404)
    task.pop('owner_id', None)
    return jsonify(success=True, **task)


@documents_bp.route("/cases/<case_id>/documents", methods=["GET"])
def list_documents(case_id):
    if not owns_case(case_id):
        return api_error('CASE_NOT_FOUND', 'No se encontró el caso.', g.request_id, 404)
    if not _valid_case_id(case_id):
        return api_error("INVALID_CASE_ID", "El identificador de caso no es válido.", g.request_id, 400)
    try:
        documents = case_document_listing(case_id)
    except Exception as error:
        current_app.logger.warning('document_list_failed case_id=%s error_type=%s', case_id, type(error).__name__)
        return api_error('DOCUMENTS_UNAVAILABLE', 'No fue posible cargar los documentos del caso.', g.request_id, 503)
    if documents is None:
        return api_error('CASE_NOT_FOUND', 'No se encontró el caso.', g.request_id, 404)
    return jsonify(success=True, case_id=case_id, documents=documents)


@documents_bp.route("/cases/<case_id>/documents/<document_id>/chunks/<chunk_id>", methods=["GET"])
def get_document_chunk(case_id, document_id, chunk_id):
    if not owns_case(case_id):
        return api_error('CASE_NOT_FOUND', 'No se encontró el caso.', g.request_id, 404)
    if not _valid_case_id(case_id):
        return api_error("INVALID_CASE_ID", "El identificador de caso no es válido.", g.request_id, 400)
    chunk = corpus_repository().get_chunk(case_id, document_id, chunk_id)
    if chunk is None:
        return api_error("CHUNK_NOT_FOUND", "No se encontró el fragmento en este caso.", g.request_id, 404)
    return jsonify(success=True, chunk=chunk)


@documents_bp.route("/cases/<case_id>/documents/<document_id>", methods=["GET"])
def get_document(case_id, document_id):
    if not owns_case(case_id):
        return api_error('CASE_NOT_FOUND', 'No se encontró el caso.', g.request_id, 404)
    if not _valid_case_id(case_id):
        return api_error("INVALID_CASE_ID", "El identificador de caso no es válido.", g.request_id, 400)
    manifest = next((doc for doc in case_document_listing(case_id) or []
                     if doc["document_id"] == document_id), None)
    if manifest is None:
        return api_error("DOCUMENT_NOT_FOUND", "No se encontró el documento en este caso.", g.request_id, 404)
    return jsonify(success=True, document=manifest)


@documents_bp.route("/cases/<case_id>/documents/<document_id>/file", methods=["GET"])
def download_document(case_id, document_id):
    if not owns_case(case_id):
        return api_error('CASE_NOT_FOUND', 'No se encontró el caso.', g.request_id, 404)
    if not _valid_case_id(case_id):
        return api_error("INVALID_CASE_ID", "El identificador de caso no es válido.", g.request_id, 400)
    repository = application_repository()
    if not repository:
        return api_error('DOCUMENT_NOT_FOUND', 'El documento no está disponible para descarga.', g.request_id, 404)
    try:
        downloaded = repository.download_case_document(authenticated_user_id(), case_id, document_id)
    except Exception as error:
        current_app.logger.warning('document_download_failed case_id=%s error_type=%s', case_id, type(error).__name__)
        return api_error('DOCUMENT_UNAVAILABLE', 'No fue posible descargar el documento.', g.request_id, 503)
    if not downloaded:
        return api_error('DOCUMENT_NOT_FOUND', 'No se encontró el documento en este caso.', g.request_id, 404)
    metadata, content = downloaded
    response = send_file(BytesIO(content), mimetype=metadata['mime_type'], as_attachment=True,
                         download_name=metadata['original_filename'], conditional=False)
    response.headers['Cache-Control'] = 'private, no-store'
    return response


@documents_bp.route("/cases/<case_id>/documents/<document_id>", methods=["DELETE"])
def delete_document(case_id, document_id):
    if not owns_case(case_id):
        return api_error('CASE_NOT_FOUND', 'No se encontró el caso.', g.request_id, 404)
    if not _valid_case_id(case_id):
        return api_error("INVALID_CASE_ID", "El identificador de caso no es válido.", g.request_id, 400)
    repository = application_repository()
    try:
        remote_document = repository.get_case_document(authenticated_user_id(), case_id, document_id) if repository else None
        if repository and remote_document:
            repository.delete_case_document(authenticated_user_id(), case_id, document_id)
        deleted = corpus_repository().delete_document(case_id, document_id)
    except Exception as error:
        current_app.logger.warning('document_delete_failed case_id=%s error_type=%s', case_id, type(error).__name__)
        return api_error('DOCUMENT_DELETE_FAILED', 'No fue posible eliminar el documento.', g.request_id, 503)
    deleted = deleted or bool(remote_document)
    if not deleted:
        return api_error("DOCUMENT_NOT_FOUND", "No se encontró el documento en este caso.", g.request_id, 404)
    return jsonify(success=True, case_id=case_id, document_id=document_id)
