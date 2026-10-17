"""NC-4: persisted, scoped NovaCase results and exports."""
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from flask import g, request

from app import create_app
from app.config import Config
from app.models.task import TaskManager, TaskStatus
from app.services.case_corpus import CaseCorpusRepository, DocumentIngestionService
from app.services.novacourt_pipeline_service import NovaCourtPipelineService
from app.services.runtime_security import CaseOwnershipRepository
from app.services.task_repository import TaskRepository


class Embeddings:
    def generate_embeddings(self, texts):
        return [[0.1, 0.2, 0.3] for _ in texts]


class NovaCaseNC4Tests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        task_db, corpus_db = root / 'tasks.sqlite3', root / 'corpus.sqlite3'

        class TestConfig(Config):
            TESTING = True
            RATE_LIMIT_ENABLED = False
            TASK_PERSISTENCE_ENABLED = True
            TASK_DB_PATH = str(task_db)
            CASE_CORPUS_DB_PATH = str(corpus_db)

        self.app = create_app(TestConfig)

        @self.app.before_request
        def test_principal():
            g.authenticated_user_id = request.headers.get('X-Test-Owner', 'owner-a')

        self.client = self.app.test_client()
        self.owners = CaseOwnershipRepository(corpus_db)
        self.assertTrue(self.owners.owned('CASE-A', 'owner-a', create=True))
        self.assertTrue(self.owners.owned('CASE-B', 'owner-b', create=True))
        self.tasks = self.app.extensions['task_manager']
        self.task_id = self.tasks.create_task('legal_analysis',
            {'owner_id': 'owner-a', 'case_id': 'CASE-A', 'tool': 'case',
             'knowledge_version': 'v2', 'document_ids': []})
        self.result = {'success': True, 'case_id': 'CASE-A', 'case': 'Caso A',
                       'report': 'Informe canónico', 'citations': [], 'sources': []}

    def tearDown(self):
        self.temp.cleanup()

    def request_export(self, case_id='CASE-A', task_id=None, owner='owner-a', **extra):
        return self.client.post('/api/export/prepare', json={
            'case_id': case_id, 'task_id': task_id or self.task_id, 'tool': 'case', **extra},
            headers={'X-Test-Owner': owner})

    def test_restart_scoped_export_and_isolation(self):
        waiting = self.request_export()
        self.assertEqual(waiting.status_code, 409)
        self.assertEqual(waiting.json['error']['code'], 'TASK_NOT_READY')
        self.tasks.update_task(self.task_id, status=TaskStatus.PROCESSING,
                               progress_detail={'current_stage': 'report', 'partial_result': self.result})
        self.tasks.complete_task(self.task_id, self.result)

        repository = TaskRepository(self.app.config['TASK_DB_PATH'])
        restored_manager = TaskManager(repository)
        self.app.extensions['task_repository'] = repository
        self.app.extensions['task_manager'] = restored_manager
        self.app.extensions['legal_pipeline'] = NovaCourtPipelineService(None, None, None, restored_manager)
        restored = restored_manager.get_task(self.task_id)
        self.assertEqual(restored.status, TaskStatus.COMPLETED)
        self.assertEqual(restored.result, self.result)
        self.assertEqual(restored.metadata['knowledge_version'], 'v2')
        self.assertNotIn('partial_result', restored.progress_detail)
        self.assertEqual(repository.load_scoped('owner-a', 'CASE-A', self.task_id)['result'], self.result)
        self.assertIsNone(repository.load_scoped('owner-b', 'CASE-A', self.task_id))
        self.assertIsNone(repository.load_scoped('owner-a', 'CASE-B', self.task_id))

        status = self.client.get(f'/api/tasks/{self.task_id}?case_id=CASE-A')
        self.assertEqual(status.status_code, 200)
        self.assertEqual(status.json['final_result'], self.result)
        exported = self.request_export()
        self.assertEqual(exported.status_code, 200)
        self.assertIn('Informe canónico', str(exported.json['document']))
        self.assertEqual(self.request_export(case_id='CASE-B').status_code, 404)
        self.assertEqual(self.request_export(owner='owner-b').status_code, 404)
        self.assertEqual(self.client.get(f'/api/tasks/{self.task_id}?case_id=CASE-A',
            headers={'X-Test-Owner': 'owner-b'}).status_code, 404)

        other_id = restored_manager.create_task('legal_analysis',
            {'owner_id': 'owner-a', 'case_id': 'CASE-A', 'tool': 'case', 'knowledge_version': 'v2'})
        restored_manager.update_task(other_id, status=TaskStatus.PROCESSING)
        restored_manager.complete_task(other_id, {**self.result, 'report': 'Segundo informe'})
        self.assertIn('Informe canónico', str(self.request_export().json['document']))
        self.assertIn('Segundo informe', str(self.request_export(task_id=other_id).json['document']))
        self.assertEqual(self.request_export(task_id='00000000-0000-4000-8000-000000000000').status_code, 404)
        forged = self.request_export(result={'success': True, 'case_id': 'CASE-A', 'report': 'FALSIFICADO'})
        self.assertEqual(forged.status_code, 400)
        self.assertNotIn('FALSIFICADO', forged.get_data(as_text=True))
        malformed_id = restored_manager.create_task('legal_analysis',
            {'owner_id': 'owner-a', 'case_id': 'CASE-A', 'tool': 'case'})
        restored_manager.update_task(malformed_id, status=TaskStatus.PROCESSING)
        restored_manager.complete_task(malformed_id, {**self.result,
            'metadata': {'case_id': 'CASE-B', 'internal': 'SECRET_DSN'}})
        invalid = self.request_export(task_id=malformed_id)
        self.assertEqual(invalid.status_code, 409)
        self.assertEqual(invalid.json['error']['code'], 'TASK_NOT_READY')
        self.assertNotIn('SECRET_DSN', invalid.get_data(as_text=True))

    def test_private_document_persists_with_case_and_upload_rejects_other_owner(self):
        repository = CaseCorpusRepository(self.app.config['CASE_CORPUS_DB_PATH'])
        ingest = DocumentIngestionService(repository, Embeddings(), max_file_size=100000,
            max_total_size=200000, max_files=20, max_uncompressed=100000,
            chunk_tokens=20, chunk_overlap=2, batch_size=4, ocr_min_chars=10)
        manifest, duplicate = ingest.ingest('CASE-A', '../evidence.txt',
            io.BytesIO(b'Private alpha evidence about the case.'))
        self.assertFalse(duplicate)
        recreated = CaseCorpusRepository(self.app.config['CASE_CORPUS_DB_PATH'])
        self.assertEqual(recreated.list_documents('CASE-A')[0]['document_id'], manifest['document_id'])
        self.assertTrue(recreated.retrieve('CASE-A', [manifest['document_id']]))
        self.assertEqual(recreated.list_documents('CASE-B'), [])
        self.app.extensions.pop('case_corpus_repository', None)
        with self.app.app_context():
            from app.services.case_service import CaseService
            with patch('app.services.case_service.SearchService'):
                service = CaseService()
            self.assertEqual(service.case_corpus_repository.list_documents('CASE-A')[0]['document_id'],
                             manifest['document_id'])
        response = self.client.post('/api/cases/CASE-A/documents',
            data={'file': (io.BytesIO(b'other evidence'), 'other.txt')},
            headers={'X-Test-Owner': 'owner-b'})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(self.owners.owned('CASE-A', 'owner-b', create=False), False)


if __name__ == '__main__':
    unittest.main()
