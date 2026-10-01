"""Deterministic Court performance and race contracts; no provider calls."""
import time
import unittest
from threading import Barrier
from unittest.mock import Mock, patch

from app.services.novacourt_pipeline_service import NovaCourtPipelineService
from app.utils.novacourt_simulation import build_simulation_context
from tests.test_novacourt_professional import FakeCase, FakeGraph, FakeSimulation
from tests.test_stabilization import await_task


class DelayedGraph(FakeGraph):
    def build_for_case(self, case_result, cancellation_token=None, snapshot_callback=None):
        snapshot_callback({"status": "building", "case_id": case_result["case_id"],
                           "version": 1, "nodes": [], "edges": []})
        snapshot_callback({"status": "building", "case_id": case_result["case_id"],
                           "version": 1, "nodes": [], "edges": []})
        time.sleep(0.04)
        return super().build_for_case(case_result, cancellation_token, snapshot_callback)


class DelayedSimulation(FakeSimulation):
    def simulate_for_case(self, case_result, case_text, cancellation_token=None):
        time.sleep(0.04)
        return super().simulate_for_case(case_result, case_text, cancellation_token)


class CourtPerformanceTests(unittest.TestCase):
    def test_parallel_branches_and_structural_contract(self):
        case = FakeCase()
        pipeline = NovaCourtPipelineService(case, DelayedGraph(), DelayedSimulation())
        start = time.perf_counter()
        task = await_task(pipeline, pipeline.start("Relato", "CASE-A"))
        elapsed = time.perf_counter() - start
        result = task["final_result"]
        self.assertLess(elapsed, 0.075)
        self.assertEqual(result["court_status"], "completed")
        self.assertTrue({"facts", "issues", "graph", "simulation", "court_report_document",
                         "warnings", "metadata", "case_id"} <= result.keys())
        self.assertEqual(result["graph"]["case_id"], result["simulation"]["case_id"])
        self.assertEqual(case.calls, 1)

    def test_isolated_branch_failures(self):
        for graph_status, sim_status in (("failed", "ready"), ("ready", "failed"), ("failed", "failed")):
            with self.subTest(graph=graph_status, simulation=sim_status):
                pipeline = NovaCourtPipelineService(FakeCase(), FakeGraph(graph_status), FakeSimulation(sim_status))
                result = await_task(pipeline, pipeline.start("Relato", "CASE-A"))["final_result"]
                self.assertEqual(result["court_status"], "partial")
                self.assertEqual(result["graph"]["status"], graph_status)
                self.assertEqual(result["simulation"]["status"], sim_status)
                self.assertTrue(result["facts"])

    def test_reuse_and_case_isolation(self):
        case = FakeCase()
        pipeline = NovaCourtPipelineService(case, FakeGraph(), FakeSimulation())
        prior = pipeline.start("A", "CASE-A", tool="case")
        await_task(pipeline, prior)
        case.analyze_case = Mock(side_effect=AssertionError("CaseService repeated"))
        reused = await_task(pipeline, pipeline.start("A", "CASE-A", reuse_task_id=prior))["final_result"]
        self.assertTrue(reused["metadata"]["case_reused"])
        self.assertEqual(reused["case_id"], "CASE-A")

    def test_context_has_unique_grounded_sources_and_no_graph_duplication(self):
        source = {"source_id": "SRC-PRIVATE01", "source_scope": "case", "case_id": "CASE-A",
                  "title": "Documento", "excerpt": "Prueba material"}
        case = {"case_id": "CASE-A", "facts": [{"text": "Hecho esencial"}],
                "issues": [{"text": "Cuestión esencial"}], "evidence": {"text": "Prueba material"},
                "sources": [source], "sources_used": [source],
                "graph": {"status": "ready", "nodes": [{"title": "Duplicado del grafo"}]}}
        context = build_simulation_context(case, "relato extenso")
        self.assertIn("Hecho esencial", context)
        self.assertIn("Cuestión esencial", context)
        self.assertIn("SRC-PRIVATE01", context)
        self.assertNotIn("Duplicado del grafo", context)
        self.assertEqual(context.count("[SRC-PRIVATE01]"), 1)
        case["case_id"] = "CASE-B"
        self.assertNotIn("SRC-PRIVATE01", build_simulation_context(case, "relato extenso"))

    def test_snapshot_and_simulation_updates_do_not_clobber_each_other(self):
        barrier = Barrier(2)
        class Graph(DelayedGraph):
            def build_for_case(self, result, cancellation_token=None, snapshot_callback=None):
                barrier.wait(timeout=1)
                return super().build_for_case(result, cancellation_token, snapshot_callback)
        class Simulation(DelayedSimulation):
            def simulate_for_case(self, result, text, cancellation_token=None):
                barrier.wait(timeout=1)
                return super().simulate_for_case(result, text, cancellation_token)
        pipeline = NovaCourtPipelineService(FakeCase(), Graph(), Simulation())
        result = await_task(pipeline, pipeline.start("Relato", "CASE-A"))["final_result"]
        self.assertEqual(result["graph"]["status"], "ready")
        self.assertEqual(result["simulation"]["status"], "ready")
        self.assertIn("court_total_duration_ms", result["metadata"])

    def test_cancel_during_parallel_branches_skips_citations(self):
        pipeline = NovaCourtPipelineService(FakeCase(), DelayedGraph(), DelayedSimulation())
        with patch("app.services.novacourt_pipeline_service.resolve_citations") as citations:
            task_id = pipeline.start("Relato", "CASE-A")
            time.sleep(0.01)
            pipeline.tasks.cancel_task(task_id)
            task = await_task(pipeline, task_id)
            self.assertEqual(task["status"], "cancelled")
            citations.assert_not_called()


if __name__ == "__main__":
    unittest.main()
