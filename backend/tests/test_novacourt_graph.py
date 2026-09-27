import importlib.util
from pathlib import Path
import unittest


from app.utils import novacourt_graph as NOVACOURT_GRAPH


def make_orchestrator(factory, enabled=True):
    return NOVACOURT_GRAPH.NovaCourtGraphOrchestrator(
        factory,
        enabled=enabled,
        timeout=12,
        poll_interval=2,
        chunk_size=500,
        chunk_overlap=50,
        batch_size=3,
    )


class ReadyBuilder:
    def __init__(self):
        self.request = None

    def create_graph(self, name):
        return 'zep-graph-1'
    def set_ontology(self, graph_id, ontology):
        pass
    def add_text_batches(self, graph_id, chunks, batch_size, cancellation_token=None):
        self.request = {'text': '\n'.join(chunks)}
        return ['episode-1']
    def _wait_for_episodes(self, episodes, timeout=600, poll_interval=3, cancellation_token=None):
        self.request.update(timeout=timeout, poll_interval=poll_interval)
    def get_graph_data(self, graph_id, cancellation_token=None):
        return {'graph_id':graph_id, 'nodes':[{'uuid':'node-1','name':'Demandante'}],
                'edges':[{'uuid':'edge-1','source_node_uuid':'node-1','target_node_uuid':'node-1'}]}


class GraphProcessingTimeoutError(Exception):
    pass


class NovaCourtGraphTests(unittest.TestCase):
    def setUp(self):
        self.case = {
            "success": True,
            "summary": {"materia": "laboral"},
            "arguments": {"principal": "reposición"},
            "evidence": {"documento": "contrato"},
            "internal_only": "no debe indexarse",
        }

    def test_canonical_contract_is_sent_to_builder_and_returns_ready_graph(self):
        builder = ReadyBuilder()
        result = make_orchestrator(lambda: builder).build(self.case)

        self.assertEqual(result["status"], "ready")
        self.assertEqual(result["graph_id"], "zep-graph-1")
        self.assertEqual(len(result["nodes"]), 1)
        self.assertEqual(len(result["edges"]), 1)
        self.assertIn("Resumen", builder.request["text"])
        self.assertIn("Argumentos", builder.request["text"])
        self.assertNotIn("internal_only", builder.request["text"])
        self.assertEqual(builder.request["timeout"], 12)
        self.assertEqual(builder.request["poll_interval"], 2)

    def test_builder_failure_preserves_case_analysis_and_has_safe_status(self):
        def failing_factory():
            raise RuntimeError("token secreto de Zep")

        result = make_orchestrator(failing_factory).build(self.case)

        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["nodes"], [])
        self.assertNotIn("secreto", result["message"])
        self.assertEqual(self.case["arguments"], {"principal": "reposición"})

    def test_timeout_has_distinct_safe_status(self):
        class TimeoutBuilder(ReadyBuilder):
            def _wait_for_episodes(self, episodes, timeout=600, poll_interval=3, cancellation_token=None):
                raise GraphProcessingTimeoutError("internal timeout detail")

        result = make_orchestrator(TimeoutBuilder).build(self.case)

        self.assertEqual(result["status"], "timeout")
        self.assertEqual(result["graph_id"], None)
        self.assertNotIn("detail", result["message"])

    def test_disabled_graph_is_not_requested(self):
        result = make_orchestrator(ReadyBuilder, enabled=False).build(self.case)
        self.assertEqual(result["status"], "not_requested")
        self.assertEqual(result["nodes"], [])


if __name__ == "__main__":
    unittest.main()
