"""Validated identity and atomic, case-level ownership boundary."""
import json
import re
import sqlite3
from contextlib import closing
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

from flask import current_app, g
from ..config import STRICT_DEPLOYMENT_ENVIRONMENTS


def verify_supabase_user(token, config):
    """Ask Supabase Auth to validate the bearer token; never decode unverified claims."""
    url = config['SUPABASE_URL'].rstrip('/') + '/auth/v1/user'
    request = Request(url, headers={'apikey': config['SUPABASE_PUBLISHABLE_KEY'],
                                    'Authorization': 'Bearer ' + token})
    try:
        with urlopen(request, timeout=config.get('AUTH_TIMEOUT_SECONDS', 5)) as response:
            data = json.load(response)
    except (HTTPError, URLError, TimeoutError, ValueError):
        return None
    user_id = data.get('id') if isinstance(data, dict) else None
    return user_id if isinstance(user_id, str) and user_id else None


def authenticated_user_id():
    return g.authenticated_user_id


class CaseOwnershipRepository:
    """Local persistent registry. Unclaimed preexisting corpus data stays inaccessible."""
    def __init__(self, path):
        self.path = str(path)
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        with closing(sqlite3.connect(self.path)) as db, db:
            db.execute('CREATE TABLE IF NOT EXISTS case_owners (case_id TEXT PRIMARY KEY, owner_id TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)')
            db.execute('CREATE INDEX IF NOT EXISTS ix_case_owners_owner ON case_owners(owner_id)')
            columns = {row[1] for row in db.execute('PRAGMA table_info(case_owners)')}
            for name, declaration in (('title', 'TEXT'), ('status', "TEXT NOT NULL DEFAULT 'active'"),
                                      ('updated_at', 'TEXT'), ('archived_at', 'TEXT')):
                if name not in columns:
                    db.execute(f'ALTER TABLE case_owners ADD COLUMN {name} {declaration}')
            db.execute('UPDATE case_owners SET updated_at=created_at WHERE updated_at IS NULL')

    def owned(self, case_id, owner_id, create=False):
        if not isinstance(case_id, str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]{0,127}', case_id) or '..' in case_id or not owner_id:
            return False
        with closing(sqlite3.connect(self.path, timeout=30)) as db, db:
            db.execute('BEGIN IMMEDIATE')
            row = db.execute('SELECT owner_id FROM case_owners WHERE case_id=?', (case_id,)).fetchone()
            if row:
                return row[0] == owner_id
            if not create:
                return False
            # A previous release may have stored documents without an owner. Never
            # permit a caller who guesses that case ID to claim those records.
            tables = db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='case_documents'").fetchone()
            if tables and db.execute('SELECT 1 FROM case_documents WHERE case_id=? LIMIT 1', (case_id,)).fetchone():
                return False
            db.execute('INSERT INTO case_owners(case_id,owner_id,updated_at) VALUES(?,?,CURRENT_TIMESTAMP)', (case_id, owner_id))
            return True

    def list_owned(self, owner_id):
        if not owner_id:
            return []
        with closing(sqlite3.connect(self.path, timeout=30)) as db:
            return [{'case_id': row[0], 'created_at': row[1], 'updated_at': row[2],
                     'title': row[3] or 'Caso jurídico', 'status': row[4], 'archived_at':row[5]} for row in db.execute(
                'SELECT case_id, created_at, updated_at, title, status, archived_at FROM case_owners WHERE owner_id=? ORDER BY updated_at DESC, case_id DESC',
                (owner_id,)).fetchall()]

    def create_case(self, owner_id, title):
        from uuid import uuid4
        case_id = str(uuid4())
        with closing(sqlite3.connect(self.path, timeout=30)) as db, db:
            db.execute('INSERT INTO case_owners(case_id,owner_id,title,updated_at) VALUES(?,?,?,CURRENT_TIMESTAMP)',
                       (case_id, owner_id, title.strip()))
            row = db.execute('SELECT case_id,title,status,created_at,updated_at FROM case_owners WHERE case_id=?',
                             (case_id,)).fetchone()
        return {'id':row[0], 'title':row[1], 'status':row[2], 'created_at':row[3], 'updated_at':row[4]}

    def update_case(self, owner_id, case_id, patch):
        allowed = {key:value for key,value in patch.items() if key in {'title','status','archived_at'}}
        if not allowed:
            return None
        assignments = ','.join(f'{key}=?' for key in allowed)
        values = list(allowed.values())
        with closing(sqlite3.connect(self.path, timeout=30)) as db, db:
            changed = db.execute(f'UPDATE case_owners SET {assignments},updated_at=CURRENT_TIMESTAMP WHERE case_id=? AND owner_id=?',
                                 (*values, case_id, owner_id)).rowcount
            if not changed:
                return None
            row = db.execute('SELECT case_id,title,status,created_at,updated_at,archived_at FROM case_owners WHERE case_id=? AND owner_id=?',
                             (case_id,owner_id)).fetchone()
        return {'id':row[0], 'title':row[1], 'status':row[2], 'created_at':row[3], 'updated_at':row[4], 'archived_at':row[5]}


def case_ownership():
    repo = current_app.extensions.get('case_ownership')
    if repo is None:
        repo = CaseOwnershipRepository(current_app.config['CASE_CORPUS_DB_PATH'])
        current_app.extensions['case_ownership'] = repo
    return repo


def owns_case(case_id, create=False):
    repository = current_app.extensions.get('application_repository')
    if repository and current_app.config.get('APP_ENV') in STRICT_DEPLOYMENT_ENVIRONMENTS:
        record = repository.get_case(authenticated_user_id(), case_id)
        if not record:
            return False
    return case_ownership().owned(case_id, authenticated_user_id(), create=create)
