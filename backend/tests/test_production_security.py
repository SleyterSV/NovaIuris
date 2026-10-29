import tempfile
import io
import time
import unittest
from pathlib import Path
from unittest.mock import Mock

from app import create_app
from app.config import Config
from app.models.task import TaskStatus
from app.services.runtime_security import case_ownership, owns_case
from flask import g
from unittest.mock import patch


class FakeEmbeddings:
    def generate_embeddings(self, texts):
        return [[0.1, 0.2] for _ in texts]

    def generate_embedding(self, text, cancellation_token=None):
        return [0.1, 0.2]


class ProductionSecurityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        class TestConfig(Config):
            APP_ENV = 'production'
            LEGAL_KNOWLEDGE_VERSION = 'v2'
            MYKE_LEGAL_DATABASE_URL = 'configured-for-test-without-connection'
            OPENAI_EMBEDDING_MODEL = 'text-embedding-3-small'
            TESTING = True
            SECRET_KEY = 's' * 48
            DEBUG = False
            SUPABASE_URL = 'https://example.supabase.co'
            SUPABASE_PUBLISHABLE_KEY = 'test-publishable'
            SUPABASE_KEY = 'test-backend'
            APP_SUPABASE_SERVICE_ROLE_KEY = 'test-service-role'
            EMBEDDING_API_KEY = 'test-embedding'
            LLM_API_KEY = 'test-private'
            ZEP_API_KEY = 'test-private'
            CORS_ALLOWED_ORIGINS = ['https://beta.example.test']
            CASE_CORPUS_DB_PATH = str(root / 'case.sqlite3')
            TASK_DB_PATH = str(root / 'tasks.sqlite3')
            AUTH_VERIFIER = staticmethod(lambda token, config: {'a-token': 'user-a', 'b-token': 'user-b'}.get(token))
            CASE_SERVICE_FACTORY = staticmethod(lambda: Mock())
            GRAPH_SERVICE_FACTORY = staticmethod(lambda: Mock())
            SIMULATION_SERVICE_FACTORY = staticmethod(lambda: Mock())
            DOCUMENT_EMBEDDING_FACTORY = staticmethod(FakeEmbeddings)
        self.config = TestConfig
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()

    def tearDown(self):
        self.temp.cleanup()

    def headers(self, token):
        return {'Authorization': 'Bearer ' + token}

    def test_auth_idor_and_document_boundary(self):
        path = '/api/cases/CASE-A/documents'
        self.assertEqual(self.client.get(path).status_code, 401)
        self.assertEqual(self.client.post(path, headers=self.headers('a-token')).status_code, 400)
        self.assertEqual(self.client.get(path, headers=self.headers('a-token')).status_code, 200)
        self.assertEqual(self.client.get(path, headers=self.headers('b-token')).status_code, 404)
        with self.app.app_context():
            manager = self.app.extensions['task_manager']
            task_id = manager.create_task('search', {'owner_id': 'user-a'})
        status = f'/api/search/tasks/{task_id}'
        self.assertEqual(self.client.get(status, headers=self.headers('b-token')).status_code, 404)
        self.assertEqual(self.client.post(status + '/cancel', headers=self.headers('b-token')).status_code, 404)
        self.assertEqual(self.client.get(status, headers=self.headers('a-token')).status_code, 200)
        court_task = manager.create_task('legal_analysis', {'owner_id': 'user-a',
            'case_id': 'CASE-A', 'tool': 'case', 'document_ids': []})
        court_status = f'/api/tasks/{court_task}?case_id=CASE-A'
        self.assertEqual(self.client.get(court_status, headers=self.headers('b-token')).status_code, 404)
        self.assertEqual(self.client.post(f'/api/tasks/{court_task}/cancel',
            headers=self.headers('b-token'), json={'case_id': 'CASE-A'}).status_code, 404)
        self.assertEqual(self.client.get(court_status, headers=self.headers('a-token')).status_code, 200)
        # A caller cannot reuse A's case task even if they know both IDs.
        attempt = self.client.post('/api/novacourt/analyze', headers=self.headers('b-token'),
            json={'case_text': 'x' * 60, 'case_id': 'CASE-A', 'reuse_task_id': court_task,
                  'owner_id': 'user-a', 'user_id': 'user-a'})
        self.assertEqual(attempt.status_code, 404)
        self.assertEqual(self.client.get('/api/cases/CASE-B/documents', headers=self.headers('b-token')).status_code, 404)

    def test_case_mutations_use_verified_identity_and_hide_other_users_cases(self):
        case_id = '00000000-0000-4000-8000-0000000000a1'
        repository = Mock()
        created_id = '00000000-0000-4000-8000-0000000000a2'
        repository.create_case.return_value = {'id':created_id,'title':'Nuevo caso','status':'active'}
        def update_case(user_id, requested_case_id, patch):
            if user_id != 'user-a' or requested_case_id != case_id:
                return None
            return {'id':case_id,'title':patch.get('title','Caso A'),
                    'status':patch.get('status','active'),
                    'archived_at':patch.get('archived_at')}
        repository.update_case.side_effect = update_case
        self.app.extensions['application_repository'] = repository

        created = self.client.post('/api/cases', headers=self.headers('a-token'),
                                   json={'title':'Nuevo caso','description':'Contexto'})
        self.assertEqual(created.status_code, 201)
        repository.create_case.assert_called_once_with('user-a','Nuevo caso','Contexto')
        forged_owner = self.client.post('/api/cases', headers=self.headers('a-token'),
                                        json={'title':'Falso','created_by':'user-b','workspace_id':'workspace-b'})
        self.assertEqual(forged_owner.status_code, 400)

        denied = self.client.patch(f'/api/cases/{case_id}', headers=self.headers('b-token'),
                                   json={'title':'Intento ajeno'})
        self.assertEqual(denied.status_code, 404)
        repository.update_case.assert_called_once_with('user-b', case_id, {'title':'Intento ajeno'})

        repository.update_case.reset_mock()
        denied_archive = self.client.patch(f'/api/cases/{case_id}', headers=self.headers('b-token'),
                                           json={'status':'archived'})
        self.assertEqual(denied_archive.status_code, 404)
        repository.update_case.assert_called_once_with('user-b', case_id, {
            'status':'archived','archived_at':unittest.mock.ANY})

        repository.update_case.reset_mock()
        denied_restore = self.client.patch(f'/api/cases/{case_id}', headers=self.headers('b-token'),
                                           json={'status':'active'})
        self.assertEqual(denied_restore.status_code, 404)
        repository.update_case.assert_called_once_with('user-b', case_id, {
            'status':'active','archived_at':None})

        repository.update_case.reset_mock()
        renamed = self.client.patch(f'/api/cases/{case_id}', headers=self.headers('a-token'),
                                    json={'title':'Caso A renombrado'})
        self.assertEqual(renamed.status_code, 200)
        self.assertEqual(renamed.json['case']['title'], 'Caso A renombrado')
        repository.update_case.assert_called_once_with('user-a', case_id, {'title':'Caso A renombrado'})

        repository.update_case.reset_mock()
        archived = self.client.patch(f'/api/cases/{case_id}', headers=self.headers('a-token'),
                                     json={'status':'archived'})
        self.assertEqual(archived.status_code, 200)
        self.assertEqual(archived.json['case']['status'], 'archived')

        repository.update_case.reset_mock()
        restored = self.client.patch(f'/api/cases/{case_id}', headers=self.headers('a-token'),
                                     json={'status':'active'})
        self.assertEqual(restored.status_code, 200)
        self.assertIsNone(restored.json['case']['archived_at'])

        delete = self.client.delete(f'/api/cases/{case_id}', headers=self.headers('a-token'))
        self.assertEqual(delete.status_code, 405)

    def test_legacy_cors_and_headers(self):
        for path in ('/api/simulation/court/simulate', '/api/graph/data/old',
                     '/api/report/generate', '/api/search'):
            response = self.client.post(path, json={'caso': 'x'})
            self.assertEqual(response.status_code, 410)
        pdf_without_scope = self.client.post('/api/export/pdf', headers=self.headers('a-token'), json={})
        self.assertEqual(pdf_without_scope.status_code, 400)
        self.assertEqual(pdf_without_scope.json['error']['code'], 'INVALID_REQUEST')
        self.assertEqual(response.headers['X-Content-Type-Options'], 'nosniff')
        allowed = self.client.options('/api/case', headers={'Origin': 'https://beta.example.test',
                                                            'Access-Control-Request-Method': 'POST'})
        self.assertEqual(allowed.headers.get('Access-Control-Allow-Origin'), 'https://beta.example.test')
        denied = self.client.options('/api/case', headers={'Origin': 'https://other.example.test',
                                                           'Access-Control-Request-Method': 'POST'})
        self.assertNotIn('Access-Control-Allow-Origin', denied.headers)

    def test_production_configuration_fails_closed(self):
        class Unsafe(self.config):
            CORS_ALLOWED_ORIGINS = ['*']
        with self.assertRaises(RuntimeError):
            create_app(Unsafe)
        class Excessive(self.config):
            CASE_RESEARCH_MAX_QUERIES = 999999
        with self.assertRaises(RuntimeError):
            create_app(Excessive)
        class InternalVolume(self.config):
            TASK_DB_PATH = str(Path(__file__).resolve().parents[1] / 'uploads' / 'test-tasks.sqlite3')
        with self.assertRaises(RuntimeError):
            create_app(InternalVolume)
        class LegacyKnowledge(self.config):
            LEGAL_KNOWLEDGE_VERSION = 'v1'
        with self.assertRaises(RuntimeError):
            create_app(LegacyKnowledge)
        class NoLegalDatabase(self.config):
            MYKE_LEGAL_DATABASE_URL = None
        with self.assertRaises(RuntimeError):
            create_app(NoLegalDatabase)
        class NoTaskPersistence(self.config):
            TASK_PERSISTENCE_ENABLED = False
        with self.assertRaises(RuntimeError):
            create_app(NoTaskPersistence)
        class LocalIdentityInProduction(self.config):
            LOCAL_DEV_AUTH_ENABLED = True
        with self.assertRaises(RuntimeError):
            create_app(LocalIdentityInProduction)

    def test_staging_uses_production_security_guards_and_persisted_ownership(self):
        class Staging(self.config):
            APP_ENV = 'staging'
        class MissingStagingCredential(Staging):
            SUPABASE_PUBLISHABLE_KEY = None
        with self.assertRaisesRegex(RuntimeError, 'runtime configuration incomplete'):
            create_app(MissingStagingCredential)

        app = create_app(Staging)
        client = app.test_client()
        self.assertEqual(client.get('/api/cases').status_code, 401)
        self.assertEqual(client.post('/api/search', headers=self.headers('a-token'),
                                     json={'query':'test'}).status_code, 410)

        repository = Mock()
        repository.get_case.return_value = None
        app.extensions['application_repository'] = repository
        with app.test_request_context('/api/cases/CASE-A'):
            g.authenticated_user_id = 'user-a'
            with patch('app.services.runtime_security.case_ownership') as local_ownership:
                self.assertFalse(owns_case('CASE-A'))
                local_ownership.assert_not_called()
        repository.get_case.assert_called_once_with('user-a', 'CASE-A')

        class UnsafeStaging(Staging):
            CORS_ALLOWED_ORIGINS = ['*']
        with self.assertRaisesRegex(RuntimeError, 'CORS origins'):
            create_app(UnsafeStaging)

    def test_staging_readiness_fails_closed_on_dependency_failure(self):
        class Staging(self.config):
            APP_ENV = 'staging'
        with patch('app._check_strict_runtime_dependencies', side_effect=TimeoutError):
            response = create_app(Staging).test_client().get('/ready')
        self.assertEqual(response.status_code, 503)
        self.assertFalse(response.json['success'])
        self.assertEqual(response.json['error']['code'], 'REQUEST_FAILED')
        self.assertNotIn('Timeout', response.get_data(as_text=True))

    def test_development_identity_requires_explicit_flag_and_bearer_is_validated(self):
        class EmptyApplicationRepository:
            def list_cases(self, user_id):
                self.user_id = user_id
                return []
            def record_task(self, task):
                return None

        repository = EmptyApplicationRepository()
        class DevelopmentConfig(self.config):
            APP_ENV = 'development'
            TESTING = False
            LOCAL_DEV_AUTH_ENABLED = False
            APPLICATION_REPOSITORY = repository
            APP_SUPABASE_SERVICE_ROLE_KEY = None
        app = create_app(DevelopmentConfig)
        client = app.test_client()
        self.assertEqual(client.get('/api/cases').status_code, 401)
        self.assertEqual(client.get('/api/cases', headers=self.headers('a-token')).status_code, 200)
        self.assertEqual(repository.user_id, 'user-a')
        class ExplicitLocalDevelopment(DevelopmentConfig):
            LOCAL_DEV_AUTH_ENABLED = True
            APPLICATION_REPOSITORY = None
        local_client = create_app(ExplicitLocalDevelopment).test_client()
        self.assertEqual(local_client.get('/api/cases').status_code, 200)
        self.assertEqual(local_client.get('/api/cases', headers=self.headers('bad-token')).status_code, 401)
        created = local_client.post('/api/cases', json={'title':'Caso local de prueba'})
        self.assertEqual(created.status_code, 201)
        self.assertTrue(created.json['case']['id'])
        self.assertEqual(local_client.get('/api/cases').json['cases'][0]['title'], 'Caso local de prueba')
        self.assertEqual(local_client.patch(f"/api/cases/{created.json['case']['id']}",
                                            json={'status':'archived'}).json['case']['status'], 'archived')

    def test_active_task_limit(self):
        manager = self.app.extensions['task_manager']
        for _ in range(self.app.config['ACTIVE_TASKS_PER_USER']):
            manager.create_task('search', {'owner_id': 'user-a'})
        response = self.client.post('/api/search/tasks', headers=self.headers('a-token'),
                                    json={'query': 'prueba'})
        self.assertEqual(response.status_code, 429)
        self.assertEqual(response.json['error']['code'], 'RATE_LIMITED')

    def test_upload_request_limit(self):
        class Tiny(self.config):
            MAX_CONTENT_LENGTH = 32
        client = create_app(Tiny).test_client()
        response = client.post('/api/cases/CASE-A/documents', headers=self.headers('a-token'),
                               data={'file': (io.BytesIO(b'x' * 100), 'synthetic.txt')})
        self.assertEqual(response.status_code, 413)

    def test_production_export_requires_owner_case_task_and_persisted_result(self):
        self.assertEqual(self.client.post('/api/case', headers=self.headers('a-token'),
            json={'case_text': 'x' * 60, 'case_id': 'CASE-A'}).status_code, 410)
        self.assertEqual(self.client.post('/api/export/prepare',
            json={'case_id': 'CASE-A', 'task_id': '00000000-0000-4000-8000-000000000000',
                  'tool': 'case'}).status_code, 401)
        with self.app.app_context():
            self.assertTrue(case_ownership().owned('CASE-A', 'user-a', create=True))
        manager = self.app.extensions['task_manager']
        task_id = manager.create_task('legal_analysis', {'owner_id': 'user-a',
            'case_id': 'CASE-A', 'tool': 'case', 'knowledge_version': 'v2'})
        manager.update_task(task_id, status=TaskStatus.PROCESSING)
        manager.complete_task(task_id, {'success': True, 'case_id': 'CASE-A',
                                        'report': 'Informe persistido'})
        payload = {'case_id': 'CASE-A', 'task_id': task_id, 'tool': 'case'}
        authorized = self.client.post('/api/export/prepare', headers=self.headers('a-token'),
                                      json=payload)
        self.assertEqual(authorized.status_code, 200)
        self.assertIn('Informe persistido', str(authorized.json['document']))
        self.assertEqual(self.client.post('/api/export/prepare', headers=self.headers('b-token'),
            json=payload).status_code, 404)
        self.assertEqual(self.client.post('/api/export/prepare', headers=self.headers('a-token'),
            json={**payload, 'result': {'success': True}}).status_code, 400)

    def test_missing_durable_document_repository_fails_closed_before_queue(self):
        path = '/api/cases/CASE-A/documents'
        class MissingPersistenceConfig(self.config):
            APP_ENV = 'development'
            TESTING = False
            APPLICATION_REPOSITORY = None
            APP_SUPABASE_SERVICE_ROLE_KEY = None
        app = create_app(MissingPersistenceConfig)
        client = app.test_client()
        with app.app_context():
            case_ownership().owned('CASE-A', 'user-a', create=True)
        manager = Mock()
        manager.active_count.return_value = 0
        app.extensions['document_task_manager'] = manager
        response = client.post(path, headers=self.headers('a-token'),
            data={'file': (io.BytesIO(b'Synthetic evidence for a private legal case.'), 'synthetic.txt')},
            content_type='multipart/form-data')
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json['error']['code'], 'PERSISTENCE_UNAVAILABLE')
        manager.start.assert_not_called()
        self.assertEqual(client.get(path, headers=self.headers('a-token')).status_code, 503)

    def test_configured_private_storage_is_document_upload_and_download_authority(self):
        class PrivateRepository:
            def __init__(self): self.documents = {}; self.objects = {}
            def get_case(self, user_id, case_id):
                return {'id':case_id, 'workspace_id':'workspace-a'} if user_id == 'user-a' and case_id == 'CASE-A' else None
            def store_case_document(self, user_id, case_id, document_id, filename, mime_type, size, sha, content):
                row = {'id':document_id, 'workspace_id':'workspace-a', 'case_id':case_id,
                    'uploaded_by':user_id, 'storage_bucket':'case-documents',
                    'storage_path':f'workspaces/workspace-a/cases/{case_id}/{document_id}/{filename}',
                    'original_filename':filename, 'mime_type':mime_type, 'size_bytes':size,
                    'sha256':sha, 'processing_status':'processing'}
                self.documents[document_id] = row; self.objects[document_id] = content.read()
                return row
            def get_case_document(self, user_id, case_id, document_id):
                row = self.documents.get(document_id)
                return row if row and row['case_id'] == case_id and row['uploaded_by'] == user_id else None
            def update_case_document_status(self, user_id, case_id, document_id, status, replaces_document_id=None):
                row = self.get_case_document(user_id, case_id, document_id)
                if row: row['processing_status'] = status
                return row
            def download_case_document(self, user_id, case_id, document_id):
                row = self.get_case_document(user_id, case_id, document_id)
                return (row, self.objects[document_id]) if row else None
            def delete_case_document(self, user_id, case_id, document_id):
                row = self.get_case_document(user_id, case_id, document_id)
                if not row: return False
                self.documents.pop(document_id); self.objects.pop(document_id, None); return True
            def record_task(self, task): pass
        repository = PrivateRepository()
        class PrivateDocumentConfig(self.config):
            APPLICATION_REPOSITORY = repository
        app = create_app(PrivateDocumentConfig)
        with app.app_context():
            case_ownership().owned('CASE-A', 'user-a', create=True)
        client = app.test_client()
        response = client.post('/api/cases/CASE-A/documents', headers=self.headers('a-token'),
            data={'file':(io.BytesIO(b'Private original with enough readable text.'), 'evidence.txt')},
            content_type='multipart/form-data')
        self.assertEqual(response.status_code, 202)
        task_path = f"/api/cases/CASE-A/document-tasks/{response.json['task_id']}"
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            task = client.get(task_path, headers=self.headers('a-token')).json
            if task['status'] in {'completed', 'failed'}: break
            time.sleep(0.01)
        self.assertEqual(task['status'], 'completed')
        document_id = task['documents'][0]['document']['document_id']
        self.assertTrue(repository.documents[document_id]['storage_path'].startswith('workspaces/workspace-a/cases/CASE-A/'))
        download = client.get(f'/api/cases/CASE-A/documents/{document_id}/file', headers=self.headers('a-token'))
        self.assertEqual(download.status_code, 200)
        self.assertEqual(download.data, b'Private original with enough readable text.')
        self.assertEqual(client.get(f'/api/cases/CASE-A/documents/{document_id}/file',
            headers=self.headers('b-token')).status_code, 404)


if __name__ == '__main__':
    unittest.main()
