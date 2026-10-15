"""Explicit Search to Case V2 handoff and task-local isolation."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from app import create_app
from app.config import Config
from app.models.task import TaskManager
from app.services.case_public_handoff import normalize_handoff_references, resolve_handoff_references
from app.services.novacourt_pipeline_service import NovaCourtPipelineService
from app.services.runtime_security import CaseOwnershipRepository
from tests.test_novacase_v2_integration import DOCUMENT, OTHER_DOCUMENT, UNIT, detail, hit
from tests.test_stabilization import await_task, case_service

REQUEST_ID = '44444444-4444-4444-8444-444444444444'


def reference(document_id=DOCUMENT, unit_id=UNIT):
    return {'source_scope':'public_legal', 'document_id':document_id, 'unit_id':unit_id}


class HandoffContractTests(unittest.TestCase):
    def test_normalization_deduplicates_exact_unit_and_discards_browser_metadata(self):
        value = {**reference(), 'text':'FORGED', 'official_url':'https://example.invalid'}
        self.assertEqual(normalize_handoff_references([value, value]), [reference()])
        self.assertEqual(len(normalize_handoff_references([reference(), reference(unit_id=OTHER_DOCUMENT)])), 2)
        for invalid in ([{**reference(), 'source_scope':'private_case'}],
                        [{**reference(), 'unit_id':'bad'}], [{**reference(), 'document_id':'bad'}],
                        [], [reference()] * 13):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                normalize_handoff_references(invalid)

    def test_canonical_resolution_and_mismatch_fail_closed(self):
        repo = Mock()
        repo.get_unit.return_value = detail()
        documents, sources = resolve_handoff_references(repo, [reference(), reference()])
        self.assertEqual(len(documents), 1)
        self.assertEqual(sources[0]['excerpt'], detail()['text'])
        self.assertEqual((sources[0]['document_id'], sources[0]['unit_id']), (DOCUMENT, UNIT))
        repo.get_unit.assert_called_once_with(UNIT, document_id=DOCUMENT)
        for value in (None, detail(document_id=OTHER_DOCUMENT), detail(text='X' * 24001)):
            repo.get_unit.return_value = value
            with self.subTest(value=value), self.assertRaises(ValueError):
                resolve_handoff_references(repo, [reference()])

    def test_task_local_handoff_reaches_all_case_modules_without_cross_case_leak(self):
        service = case_service()
        service.search_service.search.return_value = {'documents': []}
        pipeline = NovaCourtPipelineService(service, Mock(), Mock(), task_manager=TaskManager())
        a = pipeline.start('A' * 60, case_id='CASE-A', tool='case', owner_id='owner-a',
                           public_source_references=[reference()], handoff_request_id=REQUEST_ID)
        b = pipeline.start('B' * 60, case_id='CASE-B', tool='case', owner_id='owner-a')
        result_a, result_b = await_task(pipeline, a), await_task(pipeline, b)
        self.assertEqual((result_a['status'], result_b['status']), ('completed', 'completed'))
        self.assertEqual(result_a['metadata']['public_source_references'], [reference()])
        self.assertNotIn('public_source_references', result_b['metadata'])
        repeated = pipeline.start('A' * 60, case_id='CASE-A', tool='case', owner_id='owner-a',
                                  public_source_references=[reference()], handoff_request_id=REQUEST_ID)
        self.assertEqual(repeated, a)
        with self.assertRaisesRegex(ValueError, 'PUBLIC_HANDOFF_REQUEST_MISMATCH'):
            pipeline.start('C' * 60, case_id='CASE-A', tool='case', owner_id='owner-a',
                           public_source_references=[reference()], handoff_request_id=REQUEST_ID)
        source = result_a['final_result']['research']['sources'][0]
        self.assertEqual(source['source_scope'], 'public_legal')
        self.assertEqual(source['excerpt'], service.search_service.repository.get_unit.return_value['text'])
        self.assertFalse(result_b['final_result']['research']['sources'])
        with self.assertRaises(ValueError):
            pipeline.start('A' * 60, case_id='CASE-A', tool='court', owner_id='owner-a',
                           public_source_references=[reference()])

    def test_case_service_fails_closed_when_handoff_unit_disappears(self):
        service = case_service()
        service.search_service.search.return_value = {'documents': []}
        service.search_service.repository.get_unit.return_value = None
        with self.assertRaisesRegex(ValueError, 'PUBLIC_SOURCE_HANDOFF_UNAVAILABLE'):
            service.analyze_case('A' * 60, case_id='CASE-A', public_source_references=[reference()])
        service.search_service.search.assert_called_once()


class HandoffApiTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        path = str(Path(self.temp.name) / 'cases.sqlite3')
        class TestConfig(Config):
            TESTING = True
            APP_ENV = 'test'
            RATE_LIMIT_ENABLED = False
            CASE_CORPUS_DB_PATH = path
            TASK_DB_PATH = str(Path(path).with_name('tasks.sqlite3'))
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.ownership = CaseOwnershipRepository(path)
        self.app.extensions['case_ownership'] = self.ownership
        self.pipeline = Mock()
        self.pipeline.tasks.active_count.return_value = 0
        self.pipeline.start.return_value = 'task-a'
        self.payload = {'case_mode':'existing', 'case_id':'CASE-A', 'case_text':'A' * 60,
                        'public_source_references':[reference()], 'handoff_request_id':REQUEST_ID}

    def tearDown(self):
        self.temp.cleanup()

    def request_handoff(self, payload=None, owner='owner-a'):
        with patch('app.api.case.authenticated_user_id', return_value=owner), \
             patch('app.api.case.LegalRepositoryV2') as repository, \
             patch('app.api.case.pipeline', return_value=self.pipeline):
            repository.return_value.get_unit.return_value = detail()
            return self.client.post('/api/case/handoff', json=payload or self.payload)

    def test_owned_case_only_and_no_creation_on_invalid_source(self):
        self.ownership.owned('CASE-A', 'owner-a', create=True)
        response = self.request_handoff()
        self.assertEqual(response.status_code, 202)
        self.assertEqual(response.json['case_id'], 'CASE-A')
        self.pipeline.start.assert_called_once()
        self.assertEqual(self.pipeline.start.call_args.kwargs['public_source_references'], [reference()])
        self.pipeline.start.reset_mock()
        for owner, case_id in (('owner-b','CASE-A'), ('owner-a','CASE-B')):
            with self.subTest(owner=owner, case_id=case_id):
                response = self.request_handoff({**self.payload, 'case_id':case_id}, owner)
                self.assertEqual(response.status_code, 404)
                self.pipeline.start.assert_not_called()
        response = self.request_handoff({**self.payload, 'public_source_references':[reference(unit_id='bad')]})
        self.assertEqual(response.status_code, 400)
        self.pipeline.start.assert_not_called()

    def test_new_case_is_explicit_and_owner_list_is_filtered(self):
        self.ownership.owned('CASE-OTHER', 'owner-b', create=True)
        with patch('app.api.case.authenticated_user_id', return_value='owner-a'):
            self.assertEqual(self.client.get('/api/cases').json['cases'], [])
        response = self.request_handoff({'case_mode':'new', 'case_text':'N' * 60,
                                         'public_source_references':[reference()], 'handoff_request_id':REQUEST_ID})
        self.assertEqual(response.status_code, 202)
        self.assertTrue(self.ownership.owned(response.json['case_id'], 'owner-a'))
        retry = self.request_handoff({'case_mode':'new', 'case_text':'N' * 60,
                                      'public_source_references':[reference()], 'handoff_request_id':REQUEST_ID})
        self.assertEqual(retry.json['case_id'], response.json['case_id'])
        self.assertFalse(self.ownership.owned(response.json['case_id'], 'owner-b'))
        with patch('app.api.case.authenticated_user_id', return_value='owner-a'):
            self.assertEqual([item['case_id'] for item in self.client.get('/api/cases').json['cases']], [response.json['case_id']])
        self.assertEqual(self.request_handoff({**self.payload, 'case_mode':'new'}).status_code, 400)

    def test_unavailable_and_mismatched_sources_never_start_task(self):
        self.ownership.owned('CASE-A', 'owner-a', create=True)
        for resolved in (None, detail(document_id=OTHER_DOCUMENT)):
            with self.subTest(resolved=resolved), \
                 patch('app.api.case.authenticated_user_id', return_value='owner-a'), \
                 patch('app.api.case.LegalRepositoryV2') as repository, \
                 patch('app.api.case.pipeline', return_value=self.pipeline):
                repository.return_value.get_unit.return_value = resolved
                response = self.client.post('/api/case/handoff', json=self.payload)
                self.assertEqual(response.status_code, 422)
                self.pipeline.start.assert_not_called()


if __name__ == '__main__':
    unittest.main()
