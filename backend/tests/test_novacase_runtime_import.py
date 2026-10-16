"""Guard NovaCase's first-request imports and the real task creation route."""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app import create_app
from app.config import Config
from app.services.runtime_security import CaseOwnershipRepository


class NovaCaseRuntimeImportTests(unittest.TestCase):
    def test_case_import_graph_is_healthy_before_first_request(self):
        code = """import importlib, sys
modules = ('app.api.case', 'app.services.case_service', 'app.services.case_execution',
           'app.services.case_professional', 'app.services.case_report_service',
           'app.services.source_contracts')
importlib.import_module('app.api.case')
assert 'app.services.case_service' in sys.modules, 'CASE_SERVICE_LAZY_IMPORT'
for name in modules:
    importlib.import_module(name)
from app.services.case_execution import resolve_public_v2_hits
from app.services.source_contracts import normalize_public_legal_v2_source
assert callable(resolve_public_v2_hits) and callable(normalize_public_legal_v2_source)
"""
        completed = subprocess.run([sys.executable, '-c', code], capture_output=True, text=True, timeout=30)
        self.assertEqual(completed.returncode, 0, completed.stderr)

    def test_real_case_tasks_route_creates_owned_v2_task_without_import_error(self):
        with tempfile.TemporaryDirectory() as directory:
            case_db = str(Path(directory) / 'case.sqlite3')
            task_db = str(Path(directory) / 'tasks.sqlite3')
            class TestConfig(Config):
                TESTING = True
                APP_ENV = 'test'
                RATE_LIMIT_ENABLED = False
                CASE_CORPUS_DB_PATH = case_db
                TASK_DB_PATH = task_db
            app = create_app(TestConfig)
            # Construct the real CaseService and pipeline; only the read-only V2
            # connection and asynchronous work are replaced. No provider call.
            with patch('app.services.search_service.LegalRepositoryV2'), \
                 patch('app.services.novacourt_pipeline_service.NovaCourtPipelineService._run'):
                response = app.test_client().post('/api/case/tasks', json={
                    'case_text': 'Hechos comprobables para una consulta jurídica de prueba controlada.',
                    'case_id': 'HOTFIX-CASE-A', 'document_ids': []})
                self.assertEqual(response.status_code, 202, response.get_json())
                self.assertTrue(response.json['success'])
                self.assertEqual(response.json['case_id'], 'HOTFIX-CASE-A')
                self.assertTrue(response.json['task_id'])
                pipeline = app.extensions['legal_pipeline']
                self.assertEqual(pipeline.case_service.search_service.knowledge_version, 'v2')
                task = pipeline.tasks.get_task(response.json['task_id'])
                self.assertEqual(task.metadata['case_id'], 'HOTFIX-CASE-A')
                self.assertEqual(task.metadata['owner_id'], 'local-development-user')
                self.assertTrue(CaseOwnershipRepository(case_db).owned(
                    'HOTFIX-CASE-A', 'local-development-user', create=False))
                status = app.test_client().get(
                    f"/api/tasks/{response.json['task_id']}?case_id=HOTFIX-CASE-A")
                self.assertEqual(status.status_code, 200)
                self.assertEqual(status.json['task_id'], response.json['task_id'])


if __name__ == '__main__':
    unittest.main()
