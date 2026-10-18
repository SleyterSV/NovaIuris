import unittest
import re
from copy import deepcopy
from types import SimpleNamespace
from unittest.mock import patch
from zep_cloud.external_clients.ontology import entity_model_to_api_schema, edge_model_to_api_schema
from zep_cloud.types import EntityType, EdgeType, EpisodeData

from app.utils.novacourt_graph import (
    ENTITY_TYPES, NovaCourtGraphOrchestrator, provider_ontology,
    validate_provider_ontology,
)
from app.services.novacourt_pipeline_service import humanize_court_references
from app.services.novacourt_context import prepare_court_context
from app.services.graph_builder import (GraphBuilderService, GraphProcessingTimeoutError,
                                        safe_zep_validation_details)
from zep_cloud import BadRequestError
from zep_cloud.types.api_error import ApiError


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
        self.assertTrue(all(re.fullmatch(r'[A-Z][a-z][A-Za-z0-9]*', item['name'])
                            for item in ontology['entity_types']))
        self.assertTrue(all(re.fullmatch(r'[A-Z]+(?:_[A-Z]+)*', item['name'])
                            for item in ontology['edge_types']))
        self.assertTrue(all(pair['source'] in {item['name'] for item in ontology['entity_types']}
                            and pair['target'] in {item['name'] for item in ontology['entity_types']}
                            for edge in ontology['edge_types'] for pair in edge['source_targets']))

    def test_provider_projection_is_deterministic_and_keeps_canonical_nodes(self):
        nodes = [{'entity_type': kind, 'node_id': f'NODE-{index}'}
                 for index, kind in enumerate(ENTITY_TYPES)]
        before = deepcopy(nodes)
        self.assertEqual(provider_ontology(nodes), provider_ontology(list(reversed(nodes))))
        self.assertEqual(nodes, before)
        self.assertLessEqual(len(provider_ontology(nodes)['edge_types']), 10)

    def test_local_ontology_validation_rejects_limits_duplicates_orphans_and_fields(self):
        base = {'entity_types': [{'name': 'Case'}, {'name': 'Fact'}],
                'edge_types': [{'name': 'ASSERTS', 'source_targets':
                                [{'source': 'Case', 'target': 'Fact'}]}]}
        self.assertEqual(validate_provider_ontology(deepcopy(base)), base)
        variants = [
            ({'entity_types': [{'name': f'Type{i}'} for i in range(11)], 'edge_types': []},
             'COURT_ONTOLOGY_ENTITY_LIMIT'),
            ({**base, 'edge_types': [{'name': f'EDGE_{i}', 'source_targets':
                                     [{'source': 'Case', 'target': 'Fact'}]} for i in range(11)]},
             'COURT_ONTOLOGY_EDGE_LIMIT'),
            ({**base, 'entity_types': [{'name': 'Case'}, {'name': 'Case'}]},
             'COURT_ONTOLOGY_DUPLICATE_ENTITY'),
            ({**base, 'edge_types': base['edge_types'] * 2},
             'COURT_ONTOLOGY_DUPLICATE_EDGE'),
            ({**base, 'edge_types': [{'name': 'ASSERTS', 'source_targets':
                                     [{'source': 'Unknown', 'target': 'Fact'}]}]},
             'COURT_ONTOLOGY_ORPHAN_TARGET'),
            ({**base, 'edge_types': [{'name': 'ASSERTS', 'source_targets':
                                     [{'source': 'Case', 'target': 'Unknown'}]}]},
             'COURT_ONTOLOGY_ORPHAN_TARGET'),
            ({**base, 'entity_types': [{'name': 'Case', 'attributes': [{'name': 'uuid'}]},
                                      {'name': 'Fact'}]}, 'COURT_ONTOLOGY_RESERVED_FIELD'),
            ({**base, 'entity_types': [{'name': 'Case', 'attributes':
                                        [{'name': f'field_{i}'} for i in range(11)]},
                                      {'name': 'Fact'}]}, 'COURT_ONTOLOGY_FIELD_LIMIT'),
            ({**base, 'entity_types': [{'name': 'CASE'}, {'name': 'Fact'}]},
             'COURT_ONTOLOGY_INVALID_NAME'),
            ({**base, 'edge_types': [{'name': 'Asserts', 'source_targets':
                                     [{'source': 'Case', 'target': 'Fact'}]}]},
             'COURT_ONTOLOGY_INVALID_NAME'),
        ]
        for ontology, code in variants:
            with self.subTest(code=code), self.assertRaisesRegex(ValueError, code):
                validate_provider_ontology(ontology)

    def test_invalid_projection_never_calls_provider(self):
        builder = FakeBuilder()
        with patch('app.utils.novacourt_graph.provider_ontology',
                   side_effect=ValueError('COURT_ONTOLOGY_INVALID_NAME')):
            graph = orchestrator(builder).build({'case_id': 'CASE-A',
                'facts': [{'fact_id': 'FACT-1', 'text': 'Aviso', 'status': 'alleged'}]})
        self.assertEqual(graph['status'], 'failed')
        self.assertIsNone(graph['graph_id'])
        self.assertIsNone(builder.ontology)

    def test_zep_bad_request_diagnostics_never_include_raw_body(self):
        error = BadRequestError(body=ApiError(message=(
            'Invalid edge_types[0].source_targets[0].source: secret-private-case-text')),
            headers={'Authorization': 'secret-key'})
        details = safe_zep_validation_details(error)
        self.assertEqual(details['http_status'], 400)
        self.assertTrue(any(field.startswith('edge_types') for field in details['validation_fields']))
        self.assertNotIn('secret', str(details))

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
