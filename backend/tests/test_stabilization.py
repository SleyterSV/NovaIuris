import copy
import threading
import time
import unittest
from unittest.mock import Mock, create_autospec, patch

from app import create_app
from app.config import Config
from app.services.case_service import CaseService
from app.services.graph_builder import GraphBuilderService
from app.services.novacourt_pipeline_service import NovaCourtPipelineService
from app.services.novacourt_graph_service import NovaCourtGraphService
from app.services.document_output import prepare_document
from app.utils.cancellation import CancellationToken, OperationCancelled
from app.utils.case_contract import normalize_case_result
from app.utils.novacourt_graph import NovaCourtGraphOrchestrator
from app.utils.novacourt_simulation import NovaCourtSimulationOrchestrator


def case_service():
    """Exercise the real orchestrator with only provider-facing services replaced."""
    service = CaseService.__new__(CaseService)
    fields = ['case_analyzer', 'strategy_builder', 'search_service', 'argument_service',
              'evidence_analyzer', 'risk_analyzer', 'counter_argument_service', 'report_service']
    for field in fields:
        setattr(service, field, Mock())
    service.case_analyzer.analyze_case.return_value = {
        'hechos': ['HECHO-A'], 'problemas_juridicos': ['PROBLEMA-A'], 'tipo_proceso': 'Civil',
        'pretension_principal': 'Pretensión A', 'normas_probables': ['NORMA-A']}
    service.case_analyzer.summary.return_value = {'rama': 'Civil'}
    service.case_analyzer.statistics.return_value = {'evidence': 1}
    service.strategy_builder.build_strategy.return_value = {'search_queries': ['consulta'], 'claim_strategy': 'ESTRATEGIA-A'}
    service.strategy_builder.summary.return_value = {}
    service.strategy_builder.statistics.return_value = {}
    service.search_service.search.return_value = {'documents': [{'id':'doc-A', 'tipo_documento':'Jurisprudencia', 'extracto_exacto':'FUENTE-A'}]}
    service.argument_service.generate_arguments.return_value = {'main_arguments': ['ARGUMENTO-A']}
    service.evidence_analyzer.analyze.return_value = {'documentary_evidence':['PRUEBA-A']}
    service.risk_analyzer.analyze.return_value = {'procedural_risks':['RIESGO-A'], 'risk_level':'Medio'}
    service.counter_argument_service.generate_counterarguments.return_value = {'procedural_exceptions':['EXCEPCIÓN-A']}
    service.report_service.generate_report.return_value = '# INFORME-A'
    return service


def await_task(pipeline, task_id):
    deadline = time.monotonic() + 2
    while time.monotonic() < deadline:
        task = pipeline.status(task_id)
        if task['status'] in {'completed', 'failed', 'cancelled'}:
            return task
        time.sleep(.005)
    raise AssertionError('Local task did not terminate')


class CaseTests(unittest.TestCase):
    def test_case_service_without_callback_and_internal_contract(self):
        service = case_service()
        result = service.analyze_case('Expediente A', case_id='CASE-A')
        self.assertEqual(result['case_id'], 'CASE-A')
        self.assertEqual(result['analysis']['facts'], ['HECHO-A'])
        self.assertEqual(result['evidence']['documents'], ['PRUEBA-A'])
        self.assertEqual(result['risks']['procedural'], ['RIESGO-A'])
        self.assertEqual(result['strategy']['strategy'], 'ESTRATEGIA-A')
        self.assertEqual(result['counter_arguments']['procedural'], ['EXCEPCIÓN-A'])

    def test_research_receives_actual_query_without_logging_it(self):
        service = case_service()
        service.analyze_case('EXPEDIENTE-A', case_id='CASE-A')
        self.assertEqual(service.search_service.search.call_args.kwargs['query'], 'consulta')

    def test_real_stage_callbacks(self):
        stages = []
        case_service().analyze_case('A', progress_callback=lambda *args: stages.append(args))
        completed = {stage for stage, status in stages if status == 'completed'}
        self.assertEqual(completed, {'intake','facts','strategy','research','arguments','evidence','risks','counter_arguments','report'})
        self.assertLess(stages.index(('research','completed')), stages.index(('arguments','running')))

    def test_cancellation_stops_next_stage(self):
        service, token = case_service(), CancellationToken()
        def analyze(text):
            token.cancel()
            return {'hechos': ['A']}
        service.case_analyzer.analyze_case.side_effect = analyze
        with self.assertRaises(OperationCancelled):
            service.analyze_case('A', cancellation_token=token)
        service.strategy_builder.build_strategy.assert_not_called()

    def test_contract_does_not_mutate_source(self):
        raw = {'success':True, 'case_id':'CASE-A', 'analysis':{'hechos':['A']}}
        before = copy.deepcopy(raw)
        normalized = normalize_case_result(raw)
        self.assertEqual(raw, before)
        normalized['analysis']['facts'].append('B')
        self.assertEqual(raw, before)


class PipelineTests(unittest.TestCase):
    def pipeline(self, graph_status='ready', simulation_status='ready'):
        graph = Mock(spec=NovaCourtGraphService)
        graph.build_for_case.return_value = {'status':graph_status, 'nodes':[], 'edges':[]}
        simulation = Mock()
        simulation.simulate_for_case.return_value = {'status':simulation_status, 'prosecutor':{'content':'FISCAL-A'}}
        return NovaCourtPipelineService(case_service(), graph, simulation)

    def test_pipeline_ready_and_partial_failures(self):
        for graph, simulation in [('ready','ready'),('failed','ready'),('ready','failed'),('failed','failed')]:
            with self.subTest(graph=graph, simulation=simulation):
                pipeline = self.pipeline(graph, simulation)
                task = await_task(pipeline, pipeline.start('Expediente A', 'CASE-A'))
                self.assertEqual(task['status'], 'completed')
                self.assertEqual(task['final_result']['report'], '# INFORME-A')
                self.assertEqual(task['final_result']['graph']['status'], graph)
                self.assertEqual(task['final_result']['simulation']['status'], simulation)

    def test_thrown_secondary_errors_preserve_case(self):
        pipeline = self.pipeline()
        pipeline.graph_service.build_for_case.side_effect = RuntimeError('private provider detail')
        task = await_task(pipeline, pipeline.start('A','CASE-A'))
        self.assertEqual(task['status'], 'completed')
        self.assertEqual(task['final_result']['graph']['status'], 'failed')
        self.assertNotIn('private', str(task))

    def test_case_failure_stops_secondary_work(self):
        pipeline = self.pipeline()
        pipeline.case_service.case_analyzer.validate_analysis.return_value = False
        task = await_task(pipeline, pipeline.start('A','CASE-A'))
        self.assertEqual(task['status'], 'failed')
        pipeline.graph_service.build_for_case.assert_not_called()

    def test_case_isolation_with_concurrent_tasks(self):
        pipeline = self.pipeline()
        a, b = pipeline.start('EXPEDIENTE-A','CASE-A'), pipeline.start('EXPEDIENTE-B','CASE-B')
        result_a, result_b = await_task(pipeline,a), await_task(pipeline,b)
        self.assertEqual(result_a['final_result']['case'], 'EXPEDIENTE-A')
        self.assertEqual(result_b['final_result']['case'], 'EXPEDIENTE-B')
        self.assertEqual(result_a['case_id'], 'CASE-A')
        self.assertEqual(result_b['case_id'], 'CASE-B')


class AdapterTests(unittest.TestCase):
    def builder(self):
        builder = create_autospec(GraphBuilderService, instance=True, spec_set=True)
        builder.create_graph.return_value = 'graph-A'
        builder.add_text_batches.return_value = ['episode-A']
        builder.get_graph_data.return_value = {'graph_id':'graph-A', 'nodes':[{'uuid':'A'}], 'edges':[]}
        return builder

    def orchestrator(self, builder):
        return NovaCourtGraphOrchestrator(lambda:builder, enabled=True, timeout=1,
            poll_interval=1, chunk_size=500, chunk_overlap=50, batch_size=3)

    def test_graph_uses_actual_builder_interface(self):
        builder = self.builder()
        result = self.orchestrator(builder).build({'analysis':{'hechos':['A']}})
        self.assertEqual(result['status'], 'ready')
        self.assertEqual(result['node_count'], 1)
        builder.create_graph.assert_called_once()
        builder.set_ontology.assert_called_once()
        builder.add_text_batches.assert_called_once()
        builder._wait_for_episodes.assert_called_once()
        builder.get_graph_data.assert_called_once()
        self.assertFalse(hasattr(builder, 'build_graph_sync'))

    def test_graph_cancellation_prevents_next_operation(self):
        builder, token = self.builder(), CancellationToken()
        def create(name):
            token.cancel()
            return 'graph-A'
        builder.create_graph.side_effect = create
        with self.assertRaises(OperationCancelled):
            self.orchestrator(builder).build({'analysis':{'hechos':['A']}}, cancellation_token=token)
        builder.set_ontology.assert_not_called()

    def test_simulation_timeout_stops_later_calls(self):
        next_operation, finished = Mock(), threading.Event()
        class SlowSimulator:
            def simulate_case(self, context, cancellation_token=None):
                try:
                    time.sleep(.04)  # Represents an already started remote call.
                    cancellation_token.check()
                    next_operation()
                finally:
                    finished.set()
        adapter = NovaCourtSimulationOrchestrator(SlowSimulator, enabled=True, timeout=.005)
        result = adapter.simulate({'strategy':{'claim_strategy':'A'}}, 'CASE-A')
        self.assertEqual(result['status'], 'timeout')
        self.assertTrue(finished.wait(1))
        next_operation.assert_not_called()


class ApiTests(unittest.TestCase):
    def setUp(self):
        class TestConfig(Config):
            TESTING = True
            RATE_LIMIT_ENABLED = False
            CASE_SERVICE_FACTORY = staticmethod(case_service)
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()

    def test_app_routes_and_synchronous_case(self):
        routes = {rule.rule for rule in self.app.url_map.iter_rules()}
        self.assertTrue({'/api/case','/api/case/tasks','/api/novacourt/analyze',
            '/api/tasks/<task_id>','/api/tasks/<task_id>/cancel','/api/graph/data/<graph_id>',
            '/api/export/prepare','/health'} <= routes)
        response = self.client.post('/api/case',json={'case':'A'*60,'case_id':'CASE-A'})
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.json['analysis']['facts'],['HECHO-A'])

    def test_public_error_has_no_internal_details(self):
        def broken():
            raise RuntimeError('PRIVATE_SQL_AND_SECRET')
        self.app.config['CASE_SERVICE_FACTORY'] = broken
        response = self.client.post('/api/case',json={'case':'A'*60})
        self.assertEqual(response.status_code,500)
        self.assertNotIn('PRIVATE', response.get_data(as_text=True))
        self.assertIn('request_id',response.json['error'])
        self.assertNotIn('traceback',response.json)

    def test_export_is_deterministic_and_isolated(self):
        a = case_service().analyze_case('EXPEDIENTE-A',case_id='CASE-A')
        b = case_service().analyze_case('EXPEDIENTE-B',case_id='CASE-B')
        for tool in ['case','court']:
            document = prepare_document('CASE-A',a,tool)
            self.assertNotIn('EXPEDIENTE-B',str(document))
            self.assertEqual(document['metadata']['additional_ai_tokens'],0)
            with self.assertRaises(ValueError):
                prepare_document('CASE-A',b,tool)
        response = self.client.post('/api/export/prepare',json={'case_id':'CASE-A','result':b,'tool':'case'})
        self.assertEqual(response.status_code,400)
        with patch('subprocess.run') as subprocess_run:
            self.assertEqual(self.client.post('/api/export/pdf',json={}).status_code,501)
            subprocess_run.assert_not_called()


class CooperativeBoundaryTests(unittest.TestCase):
    def test_real_langgraph_stops_before_next_model(self):
        from app.services.langgraph_engine import build_tribunal_graph
        token = CancellationToken()
        def first_call(messages):
            token.cancel()
            return Mock(content='POSITION')
        model = Mock()
        model.invoke.side_effect = first_call
        with patch('app.services.langgraph_engine.get_llm', return_value=model):
            with self.assertRaises(OperationCancelled):
                build_tribunal_graph().invoke({'caso':'CASE-A','dossier_rag':'EVIDENCE','mensajes':[]},
                    config={'configurable':{'cancellation_token':token}})
        self.assertEqual(model.invoke.call_count, 1)

    def test_cancelled_pagination_does_not_fetch(self):
        from app.utils.zep_paging import _obtener_pagina_con_reintentos
        token = CancellationToken()
        token.cancel()
        api = Mock()
        with self.assertRaises(OperationCancelled):
            _obtener_pagina_con_reintentos(api, cancellation_token=token)
        api.assert_not_called()

    def test_strategy_is_not_simulator_output(self):
        from app.utils.novacourt_simulation import normalize_simulator_output
        self.assertEqual(normalize_simulator_output({'strategy':'PRIVATE-A'})['status'], 'failed')
