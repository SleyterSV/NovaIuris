"""NCourt-4 integrated local smoke: real boundaries, fake external providers."""
import tempfile
import time
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from flask import g

from app import create_app
from app.api.case import start_analysis, task_status
from app.models.task import TaskManager, TaskStatus
from app.services.case_corpus import CaseCorpusRepository
from app.services.court_simulation import LegalDebateSimulator
from app.services.legal_repository_v2 import LegalRepositoryV2
from app.services.novacourt_pipeline_service import NovaCourtPipelineService
from app.services.source_contracts import normalize_case_source, normalize_public_legal_v2_source
from app.services.task_repository import TaskRepository
from app.utils.novacourt_graph import NovaCourtGraphOrchestrator
from app.utils.novacourt_simulation import NovaCourtSimulationOrchestrator
from tests.test_novacourt_graph import ReadyBuilder
from tests.test_novacourt_v2_context import Connection, DETAIL, DOCUMENT, UNIT


OWNER, CASE, PRIVATE_DOC = "smoke-owner-a", "smoke-case-a", "smoke-private-doc"
CASE_TEXT = ("Una contratista solicita reposición: el memorando comunicó la no renovación. "
             "Alega además que se contrató un reemplazo, sin aportar documento sobre ello.")


class SmokeCaseService:
    def __init__(self, corpus, private, public):
        self.case_corpus_repository = corpus
        self.private, self.public = private, public
        self.calls = 0

    def analyze_case(self, text, *, progress_callback, cancellation_token, case_id, document_ids):
        self.calls += 1
        assert case_id == CASE and document_ids == [PRIVATE_DOC]
        progress_callback("intake", "completed")
        return {"success": True, "case": text, "case_id": case_id,
            "document_ids": list(document_ids),
            "analysis": {"tipo_proceso": "civil", "partes": {"demandante": "Trabajadora",
                         "demandado": "Entidad"}, "pretension_principal": "Reposición"},
            "summary": {"materia": "Contrato de trabajo"},
            "facts": [{"fact_id": "fact-notice", "text": "Memorando comunicó la no renovación",
                       "status": "supported", "source_ids": [self.private["source_id"]]},
                      {"fact_id": "fact-replacement", "text": "Se habría contratado un reemplazo",
                       "status": "alleged", "source_ids": [self.public["source_id"]]}],
            "issues": [{"issue_id": "issue-termination", "text": "Validez de la no renovación"}],
            "evidence": {"evidence_links": [{"evidence_id": "evidence-notice",
                "text": "Memorando de no renovación", "fact_id": "fact-notice",
                "issue_id": "issue-termination", "source_ids": [self.private["source_id"]]}]},
            "arguments": {"main_arguments": [{"argument_id": "argument-a",
                "text": "La no renovación requiere control jurídico", "issue_id": "issue-termination",
                "supporting_fact_ids": ["fact-notice"], "source_ids": [self.public["source_id"]],
                "position": "claimant"}]},
            "counter_arguments": {"main_counterarguments": [{"counterargument_id": "argument-b",
                "text": "La entidad cuestiona la vía elegida", "argument_id": "argument-a",
                "issue_id": "issue-termination", "position": "respondent"}]},
            "risks": {"procedural_risks": [{"text": "Riesgo de improcedencia",
                "issue_id": "issue-termination"}]},
            "sources": [dict(self.private), {**self.public, "excerpt": "Vista previa no canónica"}]}


class SmokeGraphService:
    def __init__(self):
        self.builder = ReadyBuilder()
        self.calls = 0

    def build_for_case(self, context, cancellation_token=None, snapshot_callback=None):
        self.calls += 1
        return NovaCourtGraphOrchestrator(lambda: self.builder, enabled=True, timeout=5,
            poll_interval=.01, chunk_size=500, chunk_overlap=50, batch_size=20,
            settle_seconds=.01).build(context, cancellation_token=cancellation_token,
                                       snapshot_callback=snapshot_callback)


class SmokeSimulationService:
    def __init__(self):
        self.calls = 0

    def simulate_for_case(self, context, case_text, cancellation_token=None):
        self.calls += 1
        return NovaCourtSimulationOrchestrator(LegalDebateSimulator, enabled=True, timeout=5).simulate(
            context, case_text, cancellation_token=cancellation_token)


class NovaCourtClosureSmoke(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory(dir=Path(__file__).parent)
        self.addCleanup(directory.cleanup)
        self.task_path = str(Path(directory.name) / "tasks.sqlite")
        corpus = CaseCorpusRepository(str(Path(directory.name) / "corpus.sqlite"))
        corpus.save({"case_id": CASE, "document_id": PRIVATE_DOC, "sha256": "smoke-hash",
            "document_version": 1, "status": "ready", "updated_at": "now", "filename": "Memorando sintético"},
            [{"chunk_id": "chunk-notice", "chunk_hash": "chunk-hash",
              "text": "Memorando sintético: no se renovará el contrato.",
              "source_reference": {"filename": "Memorando sintético", "case_id": CASE,
                                   "document_id": PRIVATE_DOC, "chunk_id": "chunk-notice"},
              "embedding": []}])
        self.private = normalize_case_source(corpus.get_chunk(CASE, PRIVATE_DOC, "chunk-notice"))
        self.public = normalize_public_legal_v2_source({"document_id": DOCUMENT, "unit_id": UNIT}, DETAIL)
        self.sql_calls = []
        self.legal = LegalRepositoryV2(connection_factory=lambda: Connection(self.sql_calls))
        self.case_service = SmokeCaseService(corpus, self.private, self.public)
        self.graph_service = SmokeGraphService()
        self.simulation_service = SmokeSimulationService()
        self.pipeline = NovaCourtPipelineService(self.case_service, self.graph_service,
            self.simulation_service, task_manager=TaskManager(TaskRepository(self.task_path)),
            legal_repository=self.legal)

    def await_task(self, task_id):
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            task = self.pipeline.status(task_id)
            if task["status"] in {"completed", "failed", "cancelled"}:
                return task
            time.sleep(.01)
        self.fail("Court smoke task did not finish")

    def test_real_boundaries_handoff_graph_simulation_citations_and_reopen(self):
        prompts = []
        def provider(prompt, config, stage):
            prompts.append((stage, prompt))
            if stage == "position_a":
                return SimpleNamespace(content=f"La demandante invoca la norma [{self.public['source_id']}] y el memorando [{self.private['source_id']}].")
            if stage == "position_b":
                return SimpleNamespace(content="La demandada cuestiona la vía y niega el reemplazo [SRC-UNKNOWN01].")
            return SimpleNamespace(content=f"Decisión SIMULADA: valoro ambas posiciones y la norma [{self.public['source_id']}].")

        with patch("app.services.langgraph_engine.invoke_court_llm", side_effect=provider), \
             patch.object(LegalDebateSimulator, "simulate_case", side_effect=AssertionError("V1 called")):
            case_task = self.pipeline.start(CASE_TEXT, CASE, tool="case",
                document_ids=[PRIVATE_DOC], owner_id=OWNER)
            self.assertEqual(self.await_task(case_task)["status"], "completed")
            app = create_app()
            with app.test_request_context("/api/novacourt/analyze", method="POST", json={
                    "case_text": CASE_TEXT, "case_id": CASE, "document_ids": [PRIVATE_DOC],
                    "reuse_task_id": case_task, "final_result": {"sources": ["forged"]}}), \
                    patch("app.api.case.owns_case", return_value=True), \
                    patch("app.api.case.authenticated_user_id", return_value=OWNER), \
                    patch("app.api.case.pipeline", return_value=self.pipeline):
                g.request_id = "smoke-request"
                response, code = start_analysis()
            self.assertEqual(code, 202)
            self.assertEqual((response.json["case_id"], response.json["tool"]), (CASE, "court"))
            court_task = response.json["task_id"]
            self.assertNotEqual(court_task, case_task)
            completed = self.await_task(court_task)

        self.assertEqual(completed["status"], "completed")
        self.assertEqual(self.case_service.calls, 1)
        self.assertEqual(self.graph_service.calls, 1)
        self.assertEqual(self.simulation_service.calls, 1)
        self.assertEqual([stage for stage, _ in prompts], ["position_a", "position_b", "judge"])
        for _, prompt in prompts:
            self.assertIn(DETAIL["text"], prompt)
            self.assertIn("Memorando sintético: no se renovará el contrato.", prompt)
            self.assertNotIn("Vista previa no canónica", prompt)
            self.assertNotIn("forged", prompt)
        self.assertIn("La demandante invoca", prompts[1][1])
        self.assertIn("La demandada cuestiona", prompts[2][1])
        self.assertTrue(any("public.legal_units" in sql for sql in self.sql_calls))

        result = completed["final_result"]
        self.assertEqual(result["case_id"], CASE)
        self.assertEqual(result["simulation"]["status"], "ready")
        self.assertEqual(result["graph"]["status"], "ready")
        self.assertEqual(result["simulation"]["decision"]["label"], "Decisión simulada")
        self.assertNotIn("SRC-UNKNOWN01", str(result["simulation"]))
        self.assertTrue(any(item["code"] == "INVALID_SOURCE_MARKER" for item in result["warnings"]))
        self.assertEqual({item["source_id"] for item in result["simulation"]["sources"]},
                         {self.private["source_id"], self.public["source_id"]})
        citation = next(item for item in result["simulation"]["citations"]
                        if item["source_id"] == self.public["source_id"])
        self.assertEqual((citation["source_scope"], citation["provenance_version"],
                          citation["document_id"], citation["unit_id"]),
                         ("public_legal", "v2", DOCUMENT, UNIT))
        self.assertNotIn("page", citation["locator"])
        self.assertNotIn("article", citation["locator"])

        nodes, edges = result["graph"]["nodes"], result["graph"]["edges"]
        self.assertTrue({"CASE", "FACT", "EVIDENCE", "DOCUMENT", "LAW", "ARGUMENT",
                         "COUNTERARGUMENT", "RISK", "PARTY", "JUDGE_ANALYSIS", "DECISION"}
                        <= {node["entity_type"] for node in nodes})
        facts = {node["fact_id"]: node for node in nodes if node["entity_type"] == "FACT"}
        self.assertEqual((facts["fact-notice"]["status"], facts["fact-replacement"]["status"]),
                         ("supported", "alleged"))
        self.assertTrue(any(edge["relation_type"] == "PROVES" and
                            edge["target_node_id"] == facts["fact-notice"]["node_id"] for edge in edges))
        self.assertFalse(any(edge["relation_type"] == "PROVES" and
                             edge["target_node_id"] == facts["fact-replacement"]["node_id"] for edge in edges))
        legal_node = next(node for node in nodes if node.get("source_id") == self.public["source_id"])
        self.assertEqual((legal_node["source_scope"], legal_node["provenance_version"],
                          legal_node["document_id"], legal_node["unit_id"]),
                         ("public_legal", "v2", DOCUMENT, UNIT))
        self.assertFalse(any(node["entity_type"] == "EVIDENCE" and
                             self.public["source_id"] in node["source_ids"] for node in nodes))
        self.assertTrue(any(node["entity_type"] == "EVIDENCE" and
                            self.private["source_id"] in node["source_ids"] for node in nodes))
        self.assertTrue(any(node["entity_type"] == "DECISION" and node.get("simulation") for node in nodes))

        restored = NovaCourtPipelineService(Mock(), Mock(), Mock(),
            task_manager=TaskManager(TaskRepository(self.task_path)), legal_repository=self.legal)
        with app.test_request_context(f"/api/novacourt/results/{court_task}?case_id={CASE}"), \
                patch("app.api.case.owns_case", return_value=True), \
                patch("app.api.case.authenticated_user_id", return_value=OWNER), \
                patch("app.api.case.pipeline", return_value=restored):
            g.request_id = "reopen-request"
            reopened = task_status(court_task)
        self.assertEqual(reopened.json["status"], "completed")
        self.assertEqual(reopened.json["final_result"], result)
        restored.case_service.analyze_case.assert_not_called()
        restored.graph_service.build_for_case.assert_not_called()
        restored.simulation_service.simulate_for_case.assert_not_called()
        for owner, case_id, task_id in (("owner-b", CASE, court_task),
                                        (OWNER, "case-b", court_task), (OWNER, CASE, case_task),
                                        (OWNER, CASE, "unknown")):
            self.assertIsNone(restored.scoped_status(owner, case_id, task_id, tool="court"))

    def test_active_restart_cancel_and_invalid_v2_source(self):
        metadata = {"owner_id": OWNER, "case_id": CASE, "tool": "court"}
        active = self.pipeline.tasks.create_task("legal_analysis", metadata)
        self.pipeline.tasks.update_task(active, status=TaskStatus.PROCESSING)
        cancelled = self.pipeline.tasks.create_task("legal_analysis", metadata)
        self.assertTrue(self.pipeline.tasks.cancel_task(cancelled))
        restored = NovaCourtPipelineService(Mock(), Mock(), Mock(),
            task_manager=TaskManager(TaskRepository(self.task_path)), legal_repository=self.legal)
        self.assertEqual(restored.scoped_status(OWNER, CASE, active, tool="court")["status"], "interrupted")
        self.assertIsNone(restored.scoped_status(OWNER, CASE, active, tool="court")["final_result"])
        self.assertEqual(restored.scoped_status(OWNER, CASE, cancelled, tool="court")["status"], "cancelled")
        self.assertIsNone(restored.scoped_status("owner-b", CASE, cancelled, tool="court"))
        result = self.case_service.analyze_case(CASE_TEXT, progress_callback=lambda *_: None,
            cancellation_token=None, case_id=CASE, document_ids=[PRIVATE_DOC])
        result["sources"][1]["unit_id"] = "33333333-3333-4333-8333-333333333333"
        from app.services.novacourt_context import prepare_court_context
        with self.assertRaises(ValueError):
            prepare_court_context(result, owner_id=OWNER, case_id=CASE,
                legal_repository=self.legal, case_corpus_repository=self.case_service.case_corpus_repository)


if __name__ == "__main__":
    unittest.main()
