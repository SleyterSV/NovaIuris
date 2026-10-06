"""Provider-free regressions for Court deadlines and partial results."""
import time
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from app.services.case_professional import build_report_document
from app.services.case_report_service import CaseReportService
from app.services.langgraph_engine import invoke_court_llm
from app.services.novacourt_pipeline_service import NovaCourtPipelineService
from app.services.graph_builder import GraphProcessingTimeoutError
from app.utils.cancellation import CancellationToken, OperationCancelled
from app.utils.novacourt_graph import NovaCourtGraphOrchestrator
from tests.test_novacourt_professional import FakeCase, FakeGraph, FakeSimulation
from tests.test_stabilization import await_task


CASE = {"success": True, "case_id": "CASE-A", "facts": [{"fact_id": "F-1", "text": "Hecho"}],
        "issues": [{"issue_id": "I-1", "text": "Cuestión"}]}


class Builder:
    def __init__(self, polls=0, empty_fetches=0, failure=None):
        self.polls, self.empty_fetches, self.failure = polls, empty_fetches, failure
        self.poll_count = 0
        self.fetch_count = 0
    def create_graph(self, name): return "G-1"
    def set_ontology(self, graph_id, ontology): pass
    def add_text_batches(self, graph_id, chunks, batch_size, cancellation_token=None):
        self.sent = len(chunks)
        return [f"E-{i}" for i in range(len(chunks))]
    def _wait_for_episodes(self, ids, timeout, poll_interval, cancellation_token=None):
        if self.failure:
            raise self.failure
        for _ in range(self.polls):
            cancellation_token.check()
            time.sleep(0.002)
            self.poll_count += 1
        self.last_poll_count = self.poll_count
    def get_graph_data(self, graph_id, cancellation_token=None):
        self.fetch_count += 1
        if self.fetch_count <= self.empty_fetches:
            return {"nodes": [], "edges": []}
        return {"nodes": [{"uuid": "N-1"}], "edges": [{"uuid": "R-1"}]}


def graph(builder, timeout=.2, settle=.02):
    return NovaCourtGraphOrchestrator(lambda: builder, enabled=True, timeout=timeout,
        poll_interval=.002, chunk_size=500, chunk_overlap=50, batch_size=3,
        settle_seconds=settle).build(CASE)


class RateError(Exception):
    def __init__(self, status, retry_after=None):
        self.status_code = status
        self.response = SimpleNamespace(headers={"Retry-After": retry_after} if retry_after else {})


class RuntimeFailureTests(unittest.TestCase):
    def test_deadline_before_citations_keeps_case_and_graph_without_unverified_decision(self):
        expired = {"value": False}
        class DeadlineToken(CancellationToken):
            def check(self):
                if expired["value"]:
                    raise OperationCancelled("deadline")
                return super().check()
        pipeline = NovaCourtPipelineService(FakeCase(), FakeGraph(), FakeSimulation())
        original_update = pipeline.tasks.update_task
        def update_task(*args, **kwargs):
            original_update(*args, **kwargs)
            detail = kwargs.get("progress_detail") or {}
            if detail.get("current_stage") == "court_citations" and detail["stages"][-1]["status"] == "running":
                expired["value"] = True
        with patch("app.services.novacourt_pipeline_service.CancellationToken", DeadlineToken), \
             patch.object(pipeline.tasks, "update_task", side_effect=update_task), \
             patch("app.services.novacourt_pipeline_service.resolve_citations") as resolve:
            task = await_task(pipeline, pipeline.start("Caso", "CASE-A"))
        resolve.assert_not_called()
        result = task["final_result"]
        self.assertEqual(task["status"], "completed")
        self.assertEqual(result["court_status"], "partial")
        self.assertEqual(result["facts"][0]["fact_id"], "FACT-1")
        self.assertEqual(result["graph"]["status"], "ready")
        self.assertEqual(result["simulation"]["status"], "timeout")
        self.assertEqual(result["simulation"]["judge"], {})
        self.assertEqual(result["court_report_document"]["sections"], [])

    def test_old_report_valueerror_reproduced(self):
        candidate = "## Hechos\n" + "Análisis sustantivo. " * 12
        self.assertFalse(CaseReportService.validate_report(candidate))
        with self.assertRaisesRegex(ValueError, "Report structure invalid"):
            if not CaseReportService.validate_report(candidate):
                raise ValueError("Report structure invalid")

    def test_tolerant_report_assembly(self):
        doc = build_report_document("Análisis sustantivo sin encabezados.", "CASE-A", [], [])
        self.assertEqual(len(doc["sections"]), 1)
        self.assertIn("Análisis", doc["sections"][0]["content"])

    def test_required_content_missing_yields_empty_partial_document(self):
        self.assertEqual(build_report_document("", "CASE-A", [], [])["sections"], [])

    def test_graph_slow_success(self):
        builder = Builder(polls=5)
        self.assertEqual(graph(builder)["status"], "ready")
        self.assertGreater(builder.poll_count, 2)

    def test_graph_real_timeout(self):
        result = graph(Builder(failure=GraphProcessingTimeoutError("late")))
        self.assertEqual(result["status"], "timeout")
        self.assertEqual(result["error"]["code"], "GRAPH_TIMEOUT")

    def test_graph_temporary_empty(self):
        builder = Builder(empty_fetches=2)
        self.assertEqual(graph(builder)["status"], "ready")
        self.assertEqual(builder.fetch_count, 3)

    def test_graph_final_empty(self):
        builder = Builder(empty_fetches=999)
        result = graph(builder, settle=.005)
        self.assertEqual(result["status"], "empty")
        self.assertEqual(result["metadata"]["empty_reason"], "provider_completed_empty")

    def test_graph_provider_failure_stage(self):
        result = graph(Builder(failure=RuntimeError("secret")))
        self.assertEqual(result["metadata"]["failed_stage"], "poll_batch")
        self.assertNotIn("secret", str(result))

    def test_graph_success_has_nodes_and_edges(self):
        result = graph(Builder())
        self.assertGreater(result["node_count"], 0)
        self.assertGreater(result["edge_count"], 0)

    def _llm(self, outcomes, token=None):
        calls = []
        class FakeLLM:
            def invoke(self, messages):
                calls.append(1)
                value = outcomes.pop(0)
                if isinstance(value, Exception): raise value
                return SimpleNamespace(content=value)
        config = {"configurable": {"cancellation_token": token or CancellationToken()}}
        with patch("app.services.langgraph_engine.get_llm", return_value=FakeLLM()), \
             patch("app.services.langgraph_engine.Config.NOVACOURT_RETRY_MAX_DELAY_SECONDS", .001):
            try:
                result = invoke_court_llm("prompt", config, "position_a")
            except Exception as error:
                return error, len(calls)
        return result, len(calls)

    def test_429_then_success(self):
        result, calls = self._llm([RateError(429, "0.001"), "ok"])
        self.assertEqual((result.content, calls), ("ok", 2))

    def test_429_exhausted(self):
        error, calls = self._llm([RateError(429)] * 3)
        self.assertEqual((error.novacourt_reason, error.novacourt_retry_count, calls),
                         ("rate_limited", 2, 3))

    def test_400_no_retry(self):
        error, calls = self._llm([RateError(400)])
        self.assertEqual(calls, 1)

    def test_cancel_before_retry(self):
        token = CancellationToken()
        class CancelError(RateError): pass
        error = CancelError(429)
        with patch("app.services.langgraph_engine.time.sleep", side_effect=lambda _: token.cancel()), \
             patch("app.services.langgraph_engine.get_llm") as llm, \
             patch("app.services.langgraph_engine.Config.NOVACOURT_RETRY_MAX_DELAY_SECONDS", .001):
            llm.return_value.invoke.side_effect = error
            with self.assertRaises(OperationCancelled):
                invoke_court_llm("prompt", {"configurable": {"cancellation_token": token}}, "judge")
            self.assertEqual(llm.return_value.invoke.call_count, 1)

    def _pipeline(self, graph_delay=0, simulation_delay=0, graph_status="ready", simulation_status="ready"):
        class SlowGraph(FakeGraph):
            def build_for_case(self, *args, **kwargs):
                time.sleep(graph_delay)
                return super().build_for_case(*args, **kwargs)
        class SlowSimulation(FakeSimulation):
            def simulate_for_case(self, *args, **kwargs):
                time.sleep(simulation_delay)
                return super().simulate_for_case(*args, **kwargs)
        pipeline = NovaCourtPipelineService(FakeCase(), SlowGraph(graph_status), SlowSimulation(simulation_status))
        task_id = pipeline.start("Caso", "CASE-A")
        return pipeline, task_id

    def test_simulation_fast_graph_slow_waits(self):
        pipeline, task_id = self._pipeline(graph_delay=.15)
        time.sleep(.04)
        self.assertEqual(pipeline.status(task_id)["status"], "processing")
        self.assertEqual(await_task(pipeline, task_id)["final_result"]["court_status"], "completed")

    def test_graph_fast_simulation_slow_waits(self):
        pipeline, task_id = self._pipeline(simulation_delay=.15)
        time.sleep(.04)
        self.assertEqual(pipeline.status(task_id)["status"], "processing")
        self.assertEqual(await_task(pipeline, task_id)["final_result"]["court_status"], "completed")

    def test_graph_failure_simulation_survives(self):
        pipeline, task_id = self._pipeline(graph_status="failed")
        result = await_task(pipeline, task_id)["final_result"]
        self.assertEqual((result["court_status"], result["simulation"]["status"]), ("partial", "ready"))

    def test_simulation_failure_graph_survives(self):
        pipeline, task_id = self._pipeline(simulation_status="failed")
        result = await_task(pipeline, task_id)["final_result"]
        self.assertEqual((result["graph"]["status"], result["court_report_document"]["sections"]), ("ready", []))

    def test_both_fail_preserves_case(self):
        pipeline, task_id = self._pipeline(graph_status="failed", simulation_status="failed")
        result = await_task(pipeline, task_id)["final_result"]
        self.assertEqual(result["facts"][0]["fact_id"], "FACT-1")
        self.assertEqual(result["court_status"], "partial")


if __name__ == "__main__": unittest.main()
