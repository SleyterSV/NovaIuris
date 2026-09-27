"""Upload and case-scoped retrieval metadata for private legal documents."""
import re
import tempfile
import shutil
import os
from uuid import uuid4
from pathlib import Path
from flask import Blueprint, current_app, jsonify, g, request
from ..services.case_corpus import CaseCorpusRepository, DocumentError, DocumentIngestionService, safe_filename
from ..utils.api_response import api_error

documents_bp = Blueprint("case_documents", __name__)
CASE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")


def corpus_repository():
    if "case_corpus_repository" not in current_app.extensions:
        factory = current_app.config.get("CASE_CORPUS_REPOSITORY_FACTORY")
        current_app.extensions["case_corpus_repository"] = (
            factory() if factory else CaseCorpusRepository(current_app.config["CASE_CORPUS_DB_PATH"]))
        current_app.extensions["case_corpus_repository"].purge_expired(
            current_app.config["CASE_CORPUS_RETENTION_DAYS"])
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


def _valid_case_id(case_id):
    return bool(CASE_ID.fullmatch(case_id)) and ".." not in case_id


@documents_bp.route("/cases/<case_id>/documents", methods=["POST"])
def upload_documents(case_id):
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
            staged.append((path, filename))
            staged_bytes += file_size
        service = ingestion_service()
        manager = current_app.extensions.get("document_task_manager")
        if manager is None:
            factory = current_app.config.get("DOCUMENT_TASK_MANAGER_FACTORY")
            from ..services.document_tasks import DocumentTaskManager
            manager = current_app.extensions["document_task_manager"] = (
                factory() if factory else DocumentTaskManager(
                    current_app.config["DOCUMENT_STAGING_MAX_AGE_SECONDS"]
                )
            )
        task_id = manager.start(case_id, staged, service, staging_directory, replacement_id)
        return jsonify(success=True, case_id=case_id, task_id=task_id, status="queued",
                       total_documents=len(staged)), 202
    except DocumentError as error:
        shutil.rmtree(staging_directory, ignore_errors=True)
        return api_error(error.code.upper(), error.message, g.request_id, 400)
    except Exception as error:
        current_app.logger.warning("document_task_start_failed case_id=%s error_type=%s",
                                   case_id, type(error).__name__)
        shutil.rmtree(staging_directory, ignore_errors=True)
        return api_error("INGESTION_FAILED", "No se pudo iniciar la ingesta documental.", g.request_id, 500)


@documents_bp.route("/cases/<case_id>/document-tasks/<task_id>", methods=["GET"])
def document_task_status(case_id, task_id):
    if not _valid_case_id(case_id):
        return api_error("INVALID_CASE_ID", "El identificador de caso no es válido.", g.request_id, 400)
    manager = current_app.extensions.get("document_task_manager")
    task = manager.status(case_id, task_id) if manager else None
    if task is None:
        return api_error("TASK_NOT_FOUND", "No se encontró la tarea documental de este caso.", g.request_id, 404)
    return jsonify(success=True, **task)


@documents_bp.route("/cases/<case_id>/documents", methods=["GET"])
def list_documents(case_id):
    if not _valid_case_id(case_id):
        return api_error("INVALID_CASE_ID", "El identificador de caso no es válido.", g.request_id, 400)
    return jsonify(success=True, case_id=case_id, documents=corpus_repository().list_documents(case_id))


@documents_bp.route("/cases/<case_id>/documents/<document_id>/chunks/<chunk_id>", methods=["GET"])
def get_document_chunk(case_id, document_id, chunk_id):
    if not _valid_case_id(case_id):
        return api_error("INVALID_CASE_ID", "El identificador de caso no es válido.", g.request_id, 400)
    chunk = corpus_repository().get_chunk(case_id, document_id, chunk_id)
    if chunk is None:
        return api_error("CHUNK_NOT_FOUND", "No se encontró el fragmento en este caso.", g.request_id, 404)
    return jsonify(success=True, chunk=chunk)


@documents_bp.route("/cases/<case_id>/documents/<document_id>", methods=["GET"])
def get_document(case_id, document_id):
    if not _valid_case_id(case_id):
        return api_error("INVALID_CASE_ID", "El identificador de caso no es válido.", g.request_id, 400)
    manifest = next((doc for doc in corpus_repository().list_documents(case_id)
                     if doc["document_id"] == document_id), None)
    if manifest is None:
        return api_error("DOCUMENT_NOT_FOUND", "No se encontró el documento en este caso.", g.request_id, 404)
    return jsonify(success=True, document=manifest)


@documents_bp.route("/cases/<case_id>/documents/<document_id>", methods=["DELETE"])
def delete_document(case_id, document_id):
    if not _valid_case_id(case_id):
        return api_error("INVALID_CASE_ID", "El identificador de caso no es válido.", g.request_id, 400)
    deleted = corpus_repository().delete_document(case_id, document_id)
    if not deleted:
        return api_error("DOCUMENT_NOT_FOUND", "No se encontró el documento en este caso.", g.request_id, 404)
    return jsonify(success=True, case_id=case_id, document_id=document_id)
