import unittest
from copy import deepcopy
from types import SimpleNamespace
from zep_cloud.external_clients.ontology import entity_model_to_api_schema, edge_model_to_api_schema
from zep_cloud.types import EntityType, EdgeType, EpisodeData

from app.utils.novacourt_graph import (
    ENTITY_TYPES, NovaCourtGraphOrchestrator, provider_ontology,
)
from app.services.novacourt_pipeline_service import humanize_court_references
from app.services.novacourt_context import prepare_court_context
from app.services.graph_builder import GraphBuilderService, GraphProcessingTimeoutError


def orchestrator(builder):
    return NovaCourtGraphOrchestrator(lambda: builder, enabled=True, timeout=2,
        poll_interval=0.01, chunk_size=500, chunk_overlap=50, batch_size=3,
        settle_seconds=0)


class FakeBuilder:
    def __init__(self, error=None, empty=False):
        self.error = error
        self.empty = empty
        self.ontology = None
        self.episodes = []

    def create_graph(self, name):
        return 'synthetic-graph'

    def set_ontology(self, graph_id, ontology):
        self.ontology = ontology
        if self.error:
            raise self.error

    def add_text_batches(self, graph_id, chunks, batch_size, cancellation_token=None):
        self.episodes = chunks
        return [f'episode-{index}' for index in range(len(chunks))]

    def _wait_for_episodes(self, episodes, **kwargs):
        return None

    def get_graph_data(self, graph_id, cancellation_token=None):
        if self.empty:
            return {'nodes': [], 'edges': []}
        return {'nodes': [{'name': 'Caso'}], 'edges': [{'name': 'ASSERTS'}]}


class CourtSmokeHotfixTests(unittest.TestCase):
    def test_provider_ontology_respects_installed_plan_limit(self):
        nodes = [{'entity_type': kind} for kind in ENTITY_TYPES]
        original = deepcopy(nodes)
        ontology = provider_ontology(nodes)
        self.assertEqual(len(ontology['entity_types']), 10)
        self.assertEqual(nodes, original)
        self.assertTrue(all(pair['source'] in {item['name'] for item in ontology['entity_types']}
                            and pair['target'] in {item['name'] for item in ontology['entity_types']}
                            for edge in ontology['edge_types'] for pair in edge['source_targets']))

    def test_installed_sdk_serializes_selected_ontology_and_episode(self):
        calls = []
        builder = GraphBuilderService.__new__(GraphBuilderService)
        builder.client = SimpleNamespace(graph=SimpleNamespace(
            set_ontology=lambda **kwargs: calls.append(kwargs)))
        builder.set_ontology('synthetic-graph', provider_ontology(
            [{'entity_type': kind} for kind in ENTITY_TYPES]))
        request = calls[0]
        self.assertEqual(request['graph_ids'], ['synthetic-graph'])
        self.assertLessEqual(len(request['entities']), 10)
        for name, model in request['entities'].items():
            self.assertEqual(EntityType(**entity_model_to_api_schema(model, name)).name, name)
        for name, (model, targets) in request['edges'].items():
            self.assertEqual(EdgeType(**{**edge_model_to_api_schema(model, name),
                                         'source_targets': [target.dict() for target in targets]}).name, name)
        self.assertEqual(EpisodeData(data='{"title":"Caso"}', type='text').type, 'text')

    def test_bad_request_at_ontology_is_not_timeout_or_episode_failure(self):
        BadRequestError = type('BadRequestError', (Exception,), {})
        builder = FakeBuilder(error=BadRequestError('sensitive provider response'))
        graph = orchestrator(builder).build({
            'case_id': 'CASE-A', 'summary': {'materia': 'Laboral'},
            'facts': [{'fact_id': 'FACT-1', 'text': 'Memorando', 'status': 'alleged'}],
        })
        self.assertEqual(graph['status'], 'failed')
        self.assertEqual(graph['stage'], 'set_ontology')
        self.assertEqual(builder.episodes, [])
        self.assertNotIn('sensitive', str(graph))

    def test_episode_ingestion_and_final_snapshot(self):
        builder = FakeBuilder()
        graph = orchestrator(builder).build({
            'case_id': 'CASE-A', 'summary': {'materia': 'Laboral'},
            'facts': [{'fact_id': 'FACT-1', 'text': 'Memorando', 'status': 'alleged'}],
        })
        self.assertEqual(graph['status'], 'ready')
        self.assertTrue(builder.episodes)
        self.assertLessEqual(len(builder.ontology['entity_types']), 10)

    def test_provider_empty_graph_never_reports_ready(self):
        builder = FakeBuilder(empty=True)
        graph = orchestrator(builder).build({'case_id': 'CASE-A',
            'facts': [{'fact_id': 'FACT-1', 'text': 'Aviso', 'status': 'alleged'}]})
        self.assertEqual(graph['status'], 'empty')
        self.assertTrue(builder.episodes)

    def test_batch_bad_request_and_timeout_are_distinct(self):
        class FailingBatch(FakeBuilder):
            def __init__(self, error):
                super().__init__()
                self.batch_error = error

            def add_text_batches(self, *args, **kwargs):
                raise self.batch_error

        case = {'case_id': 'CASE-A',
                'facts': [{'fact_id': 'FACT-1', 'text': 'Aviso', 'status': 'alleged'}]}
        BadRequestError = type('BadRequestError', (Exception,), {})
        rejected = orchestrator(FailingBatch(BadRequestError('private text'))).build(case)
        timed_out = orchestrator(FailingBatch(GraphProcessingTimeoutError('timeout'))).build(case)
        self.assertEqual((rejected['status'], rejected['stage']), ('failed', 'send_batch'))
        self.assertEqual((timed_out['status'], timed_out['stage']), ('timeout', 'send_batch'))
        self.assertNotIn('private text', str(rejected))

    def test_fact_and_source_ids_become_human_references(self):
        fact = {'fact_id': 'FACT-abc', 'text': 'Memorando comunicó la no renovación',
                'status': 'supported', 'source_ids': ['SRC-abcdef']}
        source = {'source_id': 'SRC-abcdef', 'source_scope': 'private_case',
                  'case_id': 'CASE-A', 'title': 'Memorando'}
        text = humanize_court_references('[FACT-abc, SRC-abcdef]', [fact], [source])
        self.assertIn('Memorando comunicó', text)
        self.assertNotIn('FACT-', text)
        self.assertIn('[SRC-abcdef]', text)
        self.assertEqual(humanize_court_references('FACT-other', [fact], [source]), 'hecho no verificable')

    def test_court_context_preserves_inherited_process_type(self):
        case = {'case_id': 'CASE-A', 'summary': {'proceso': 'Vía laboral ordinaria'},
                'document_ids': [], 'sources': [], 'facts': []}
        court = prepare_court_context(case, owner_id='owner-a', case_id='CASE-A')
        self.assertEqual(court['summary']['proceso'], 'Vía laboral ordinaria')
        self.assertEqual(case['summary']['proceso'], 'Vía laboral ordinaria')


if __name__ == '__main__':
    unittest.main()
