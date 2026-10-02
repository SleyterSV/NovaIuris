import tempfile
import io
import time
import unittest
from pathlib import Path
from unittest.mock import Mock

from app import create_app
from app.config import Config


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
            TESTING = True
            SECRET_KEY = 's' * 48
            DEBUG = False
            SUPABASE_URL = 'https://example.supabase.co'
            SUPABASE_PUBLISHABLE_KEY = 'test-publishable'
            SUPABASE_KEY = 'test-backend'
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

    def test_legacy_cors_and_headers(self):
        for path in ('/api/simulation/court/simulate', '/api/graph/data/old',
                     '/api/report/generate', '/api/export/pdf', '/api/search'):
            response = self.client.post(path, json={'caso': 'x'})
            self.assertEqual(response.status_code, 410)
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

    def test_real_document_task_and_chunk_are_owner_scoped(self):
        path = '/api/cases/CASE-A/documents'
        response = self.client.post(path, headers=self.headers('a-token'),
            data={'file': (io.BytesIO(b'Synthetic evidence for a private legal case.'), 'synthetic.txt')},
            content_type='multipart/form-data')
        self.assertEqual(response.status_code, 202)
        task_path = f"/api/cases/CASE-A/document-tasks/{response.json['task_id']}"
        self.assertEqual(self.client.get(task_path, headers=self.headers('b-token')).status_code, 404)
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            task = self.client.get(task_path, headers=self.headers('a-token')).json
            if task['status'] in {'completed', 'failed'}:
                break
            time.sleep(0.01)
        self.assertEqual(task['status'], 'completed')
        document_id = task['documents'][0]['document']['document_id']
        self.assertEqual(self.client.get(f'{path}/{document_id}', headers=self.headers('b-token')).status_code, 404)
        self.assertEqual(self.client.get(f'{path}/{document_id}', headers=self.headers('a-token')).status_code, 200)


if __name__ == '__main__':
    unittest.main()
