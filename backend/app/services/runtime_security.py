"""Validated identity and atomic, case-level ownership boundary."""
import json
import re
import sqlite3
from contextlib import closing
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

from flask import current_app, g


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
            db.execute('INSERT INTO case_owners(case_id,owner_id) VALUES(?,?)', (case_id, owner_id))
            return True


def case_ownership():
    repo = current_app.extensions.get('case_ownership')
    if repo is None:
        repo = CaseOwnershipRepository(current_app.config['CASE_CORPUS_DB_PATH'])
        current_app.extensions['case_ownership'] = repo
    return repo


def owns_case(case_id, create=False):
    if current_app.config.get('APP_ENV', 'development') != 'production':
        create = True
    return case_ownership().owned(case_id, authenticated_user_id(), create=create)
