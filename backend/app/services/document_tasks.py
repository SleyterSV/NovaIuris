"""Process-local document ingestion tasks with case-scoped status polling."""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from threading import Lock, Thread
from time import time
from uuid import uuid4
import shutil
import os
import tempfile
import re


STAGING_PREFIX = "nova-document-task-"
STAGING_NAME = re.compile(r"^" + re.escape(STAGING_PREFIX) + r"[A-Za-z0-9_-]+$")


def cleanup_abandoned_staging(temp_root=None, max_age_seconds=24 * 60 * 60, now=None):
    """Remove only old, real NovaIuris task directories from the temp root."""
    root = Path(temp_root or tempfile.gettempdir())
    try:
        root = root.resolve(strict=True)
        cutoff = (time() if now is None else now) - max(60, int(max_age_seconds))
        removed = 0
        with os.scandir(root) as entries:
            for entry in entries:
                if not STAGING_NAME.fullmatch(entry.name):
                    continue
                try:
                    if not entry.is_dir(follow_symlinks=False):
                        continue
                    if entry.stat(follow_symlinks=False).st_mtime >= cutoff:
                        continue
                    shutil.rmtree(Path(entry.path))
                    removed += 1
                except OSError:
                    # Cleanup is best effort and must never prevent app startup.
                    continue
        return removed
    except OSError:
        return 0


class DocumentTaskManager:
    def __init__(self, staging_max_age_seconds=24 * 60 * 60, repository=None):
        self._lock = Lock()
        self._tasks = {}
        self.repository = repository
        if repository:
            self._tasks = {task['task_id']: task for task in repository.load_after_restart()}
        cleanup_abandoned_staging(max_age_seconds=staging_max_age_seconds)

    def start(self, case_id, files, ingestion_service, staging_directory, replaces_document_id=None, owner_id=None):
        if self.repository and not owner_id:
            raise ValueError('Persistent document tasks require an authenticated owner')
        task_id = str(uuid4())
        task_documents = []
        normalized_files = []
        for entry in files:
            path, filename = entry[:2]
            preparation_error = entry[2] if len(entry) > 2 else None
            document_id = str(uuid4())
            normalized_files.append((path, filename, preparation_error, document_id))
            task_documents.append({"document_id":document_id, "case_id":case_id,
                                   "filename":filename, "status":"uploaded"})
        state = {"task_id":task_id, "case_id":case_id, "owner_id":owner_id,
                 "tool":"documents", "status":"queued",
                 "stage":"uploaded", "progress":0, "progress_kind":"completed_documents",
                 "completed_documents":0, "total_documents":len(normalized_files),
                 "documents":task_documents,
                 "error":None, "created_at":time(), "updated_at":time()}
        with self._lock:
            self._cleanup_locked()
            self._tasks[task_id] = state
            if self.repository:
                self.repository.save(state)
        Thread(target=self._run, args=(task_id, case_id, normalized_files, ingestion_service, staging_directory, replaces_document_id),
               name=f"document-ingest-{task_id[:8]}", daemon=True).start()
        return task_id

    def _update(self, task_id, **changes):
        with self._lock:
            task = self._tasks.get(task_id)
            if task:
                task.update(changes, updated_at=time())
                if self.repository:
                    self.repository.save(task)

    def _run(self, task_id, case_id, files, ingestion_service, staging_directory, replaces_document_id):
        self._update(task_id, status="running", stage="validating")
        try:
            for index, entry in enumerate(files):
                path, filename, preparation_error, document_id = entry
                self._update(task_id, stage="validating", current_document=filename,
                             current_document_index=index + 1, current_units=0)
                def report(stage, completed_units):
                    self._update(task_id, stage=stage, current_units=int(completed_units or 0))
                    with self._lock:
                        task = self._tasks.get(task_id)
                        if task:
                            task["documents"][index]["status"] = stage
                try:
                    if preparation_error:
                        raise ValueError(preparation_error["message"])
                    with Path(path).open("rb") as stream:
                        manifest, duplicate = ingestion_service.ingest(case_id, filename, stream,
                            replaces_document_id=replaces_document_id, progress=report,
                            document_id=document_id)
                    outcome = {"status":manifest["status"], "duplicate":duplicate, "document":manifest}
                except Exception as error:
                    from .case_corpus import DocumentError
                    failure_document = {"document_id":document_id, "case_id":case_id,
                        "filename":filename, "status":"failed", "page_count":None,
                        "chunk_count":0, "ocr_required":False, "warnings":[]}
                    if preparation_error:
                        outcome = {**failure_document, "error":preparation_error}
                    elif isinstance(error, DocumentError):
                        outcome = {**failure_document,
                                   "error":{"code":error.code, "message":error.message}}
                    else:
                        outcome = {**failure_document,
                                   "error":{"code":"index_failed", "message":"No se pudo procesar este documento."}}
                with self._lock:
                    task = self._tasks.get(task_id)
                    if task:
                        task["documents"][index] = outcome
                        task["completed_documents"] = index + 1
                        task["progress"] = int((index + 1) * 100 / max(1, len(files)))
                        task["stage"] = "finalizing" if index + 1 == len(files) else "validating"
                        task["updated_at"] = time()
                        if self.repository:
                            self.repository.save(task)
            self._update(task_id, status="completed", stage="completed",
                         result={"case_id":case_id}, error=None)
        except Exception:
            self._update(task_id, status="failed", stage="failed",
                         error={"code":"INGESTION_FAILED", "message":"No se pudo completar la ingesta documental."})
        finally:
            shutil.rmtree(staging_directory, ignore_errors=True)

    def status(self, case_id, task_id, owner_id=None):
        with self._lock:
            task = self._tasks.get(task_id)
            if not task or task["case_id"] != case_id or (owner_id is not None and task.get('owner_id') != owner_id):
                return None
            return deepcopy(task)

    def active_count(self, owner_id):
        with self._lock:
            return sum(task.get('owner_id') == owner_id and task['status'] in {'queued', 'running'}
                       for task in self._tasks.values())

    def _cleanup_locked(self):
        cutoff = time() - 3600
        if self.repository:
            return
        terminal = {"completed", "failed", "cancelled", "interrupted"}
        for task_id in [key for key, value in self._tasks.items()
                        if value["status"] in terminal and value["updated_at"] < cutoff]:
            self._tasks.pop(task_id, None)
