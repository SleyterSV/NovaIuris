"""Single-instance SQLite task journal for controlled beta deployments."""
import json
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from time import time
from pathlib import Path


class TaskRepository:
    MAX_RESULT_BYTES = 8 * 1024 * 1024

    def __init__(self, path):
        self.path = str(path)
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        with closing(sqlite3.connect(self.path)) as db, db:
            db.executescript('''
                CREATE TABLE IF NOT EXISTS runtime_tasks (
                  task_id TEXT PRIMARY KEY, owner_id TEXT NOT NULL, case_id TEXT,
                  task_type TEXT NOT NULL, status TEXT NOT NULL, created_at TEXT NOT NULL,
                  updated_at TEXT NOT NULL, payload_json TEXT NOT NULL);
                CREATE INDEX IF NOT EXISTS ix_runtime_tasks_owner_status ON runtime_tasks(owner_id,status);
                CREATE INDEX IF NOT EXISTS ix_runtime_tasks_case ON runtime_tasks(case_id);
                CREATE INDEX IF NOT EXISTS ix_runtime_tasks_created ON runtime_tasks(created_at);
            ''')

    def save(self, task):
        payload = task.to_dict()
        raw = json.dumps(payload, ensure_ascii=False, default=str)
        if len(raw.encode('utf-8')) > self.MAX_RESULT_BYTES:
            payload['result'] = None
            payload['progress_detail'] = {}
            payload['status'] = 'failed'
            payload['error'] = {'code': 'RESULT_TOO_LARGE', 'message': 'El resultado excedió el límite de almacenamiento.'}
            raw = json.dumps(payload, ensure_ascii=False, default=str)
            task.result = None
            task.status = type(task.status).FAILED
            task.error = payload['error']
        with closing(sqlite3.connect(self.path, timeout=30)) as db, db:
            db.execute('''INSERT INTO runtime_tasks(task_id,owner_id,case_id,task_type,status,created_at,updated_at,payload_json)
                VALUES(?,?,?,?,?,?,?,?) ON CONFLICT(task_id) DO UPDATE SET
                status=excluded.status,updated_at=excluded.updated_at,payload_json=excluded.payload_json''',
                (task.task_id, task.metadata['owner_id'],
                 task.metadata.get('case_id'), task.task_type, task.status.value,
                 task.created_at.isoformat(), task.updated_at.isoformat(), raw))

    def load_all(self):
        with closing(sqlite3.connect(self.path)) as db, db:
            rows = db.execute('SELECT payload_json FROM runtime_tasks').fetchall()
        return [json.loads(row[0]) for row in rows]

    def interrupt_active(self):
        """Only call when starting the sole beta worker, before accepting requests."""
        with closing(sqlite3.connect(self.path, timeout=30)) as db, db:
            rows = db.execute("SELECT task_id,payload_json FROM runtime_tasks WHERE status IN ('pending','processing')").fetchall()
            for task_id, raw in rows:
                payload = json.loads(raw)
                payload['status'] = 'interrupted'
                payload['updated_at'] = datetime.now(timezone.utc).isoformat()
                payload['finished_at'] = payload['updated_at']
                payload['error'] = {'code': 'TASK_INTERRUPTED', 'message': 'El servidor se reinició durante la tarea. Iníciala nuevamente.'}
                db.execute('UPDATE runtime_tasks SET status=?,updated_at=?,payload_json=? WHERE task_id=?',
                           ('interrupted', payload['updated_at'], json.dumps(payload, ensure_ascii=False), task_id))


class DocumentTaskRepository:
    """Bounded document-ingestion status journal on the same persistent volume."""
    def __init__(self, path):
        self.path = str(path)
        with closing(sqlite3.connect(self.path)) as db, db:
            db.execute('''CREATE TABLE IF NOT EXISTS document_runtime_tasks (
                task_id TEXT PRIMARY KEY, owner_id TEXT NOT NULL, case_id TEXT NOT NULL,
                status TEXT NOT NULL, updated_at REAL NOT NULL, payload_json TEXT NOT NULL)''')
            db.execute('CREATE INDEX IF NOT EXISTS ix_document_runtime_tasks_owner ON document_runtime_tasks(owner_id,case_id)')

    def save(self, task):
        payload = dict(task)
        payload.pop('current_document', None)
        raw = json.dumps(payload, ensure_ascii=False, default=str)
        if len(raw.encode('utf-8')) > 1024 * 1024:
            payload['documents'] = []
            payload['status'] = 'failed'
            payload['error'] = {'code': 'RESULT_TOO_LARGE', 'message': 'El resultado excedió el límite de almacenamiento.'}
            task.update(payload)
            raw = json.dumps(payload, ensure_ascii=False, default=str)
        with closing(sqlite3.connect(self.path, timeout=30)) as db, db:
            db.execute('''INSERT INTO document_runtime_tasks(task_id,owner_id,case_id,status,updated_at,payload_json)
                VALUES(?,?,?,?,?,?) ON CONFLICT(task_id) DO UPDATE SET
                status=excluded.status,updated_at=excluded.updated_at,payload_json=excluded.payload_json''',
                (task['task_id'], task['owner_id'], task['case_id'], task['status'], task['updated_at'], raw))

    def load_after_restart(self):
        with closing(sqlite3.connect(self.path, timeout=30)) as db, db:
            rows = db.execute('SELECT task_id,payload_json FROM document_runtime_tasks').fetchall()
            states = []
            for task_id, raw in rows:
                state = json.loads(raw)
                if state['status'] in {'queued', 'running'}:
                    state['status'] = 'interrupted'
                    state['updated_at'] = time()
                    state['error'] = {'code': 'TASK_INTERRUPTED', 'message': 'El servidor se reinició durante la ingesta.'}
                    db.execute('UPDATE document_runtime_tasks SET status=?,updated_at=?,payload_json=? WHERE task_id=?',
                               ('interrupted', state['updated_at'], json.dumps(state, ensure_ascii=False), task_id))
                states.append(state)
        return states
