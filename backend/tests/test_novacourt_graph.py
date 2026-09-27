import importlib.util
from pathlib import Path
import unittest


MODULE_PATH = Path(__file__).parents[1] / "app" / "utils" / "novacourt_graph.py"
SPEC = importlib.util.spec_from_file_location("novacourt_graph", MODULE_PATH)
NOVACOURT_GRAPH = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(NOVACOURT_GRAPH)


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

    def build_graph_sync(self, **kwargs):
        self.request = kwargs
        return {
            "graph_id": "zep-graph-1",
            "nodes": [{"uuid": "node-1", "name": "Demandante"}],
            "edges": [{"uuid": "edge-1", "source_node_uuid": "node-1", "target_node_uuid": "node-1"}],
        }


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
        class TimeoutBuilder:
            def build_graph_sync(self, **kwargs):
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
