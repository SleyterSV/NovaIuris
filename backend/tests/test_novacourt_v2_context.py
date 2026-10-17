"""NCourt-1 canonical context and persisted handoff regression tests."""
import tempfile
import time
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from app.models.task import TaskManager, TaskStatus
from app import create_app
from app.api.case import start_analysis, task_status
from flask import g
from app.services.case_corpus import CaseCorpusRepository
from app.services.legal_repository_v2 import LegalRepositoryV2, UNIT_DETAIL_COLUMNS
from app.services.novacourt_context import prepare_court_context
from app.services.novacourt_pipeline_service import NovaCourtPipelineService
from app.services.source_contracts import normalize_case_source, normalize_public_legal_v2_source
from app.services.task_repository import TaskRepository
from app.utils.novacourt_graph import build_graph_input
from app.utils.novacourt_simulation import NovaCourtSimulationOrchestrator


DOCUMENT = "11111111-1111-4111-8111-111111111111"
UNIT = "22222222-2222-4222-8222-222222222222"
OTHER = "33333333-3333-4333-8333-333333333333"
CASE = "case-a"
OWNER = "owner-a"
CASE_TEXT = "Relato jurídico autorizado del expediente A con hechos y pretensiones concretas."
DETAIL = {"unit_id": UNIT, "document_id": DOCUMENT, "text": "Texto íntegro de legal_units.text",
          "unit_type": "article", "unit_number": "7", "heading": "Derecho aplicable",
          "document_title": "Ley de prueba", "document_type": "law", "short_title": "Ley de prueba"}


class Cursor:
    def __init__(self, calls):
        self.calls = calls
        self.params = None
    def execute(self, sql, params):
        self.calls.append(sql)
        self.params = params
    def fetchone(self):
        if self.params != (UNIT, DOCUMENT):
            return None
        return tuple(DETAIL.get(key) for key in UNIT_DETAIL_COLUMNS)


class Connection:
    autocommit = False
    def __init__(self, calls):
        self.calls = calls
    def set_session(self, *, readonly):
        assert readonly
    def cursor(self):
        return Cursor(self.calls)
    def rollback(self):
        pass
    def close(self):
        pass


class CaseService:
    def __init__(self, corpus, public, private):
        self.case_corpus_repository = corpus
        self.public, self.private = public, private
        self.calls = 0
    def analyze_case(self, case_text, *, progress_callback, cancellation_token, case_id, document_ids):
        self.calls += 1
        if progress_callback:
            progress_callback("intake", "running")
        return {"success": True, "case": case_text, "case_id": case_id,
                "document_ids": list(document_ids), "facts": [{"fact_id": "f1", "text": "Alegación sin prueba",
                    "status": "alleged", "source_ids": [self.public["source_id"]]}],
                "evidence": {"evidence_links": [{"source_ids": [self.public["source_id"]]},
                                                 {"source_ids": [self.private["source_id"]]}]},
                "sources": [{**self.public, "source_scope": "public", "legal_source_scope": "public_legal",
                             "excerpt": "preview no canónico"},
                            {**self.private, "source_scope": "case", "excerpt": "preview privado"}]}


class Graph:
    def __init__(self):
        self.input = None
    def build_for_case(self, context, cancellation_token=None, snapshot_callback=None):
        self.input = build_graph_input(context)
        return {"status": "ready", "case_id": context["case_id"], "nodes": [], "edges": []}


class Simulation:
    def __init__(self, public, private):
        self.input = None
        self.public, self.private = public, private
    def simulate_for_case(self, context, case_text, cancellation_token=None):
        self.input = context
        return {"status": "ready", "case_id": context["case_id"],
                "prosecutor": {"content": f"Norma [{self.public['source_id']}]"},
                "defense": {"content": f"Documento [{self.private['source_id']}]"},
                "judge": {"content": f"Decisión [{self.public['source_id']}]"}}


class NovaCourtV2ContextTests(unittest.TestCase):
    def await_task(self, task_id):
        deadline = time.monotonic() + 15
        while time.monotonic() < deadline:
            task = self.pipeline.status(task_id)
            if task["status"] in {"completed", "failed", "cancelled"}:
                return task
            time.sleep(.01)
        self.fail(f"Court task did not terminate: calls={self.case_service.calls} {self.pipeline.status(task_id)}")

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(dir=Path(__file__).parent)
        self.addCleanup(self.directory.cleanup)
        self.calls = []
        self.legal = LegalRepositoryV2(connection_factory=lambda: Connection(self.calls))
        self.public = normalize_public_legal_v2_source(
            {"document_id": DOCUMENT, "unit_id": UNIT, "extracto_exacto": "preview"}, DETAIL)
        self.corpus = CaseCorpusRepository(str(Path(self.directory.name) / "corpus.sqlite"))
        manifest = {"case_id": CASE, "document_id": "private-doc", "sha256": "abc",
                    "document_version": 1, "status": "ready", "updated_at": "now", "filename": "Contrato"}
        chunk = {"chunk_id": "chunk-a", "chunk_hash": "hash", "text": "Cláusula canónica privada",
                 "source_reference": {"filename": "Contrato", "case_id": CASE,
                                      "document_id": "private-doc", "chunk_id": "chunk-a"}, "embedding": []}
        self.corpus.save(manifest, [chunk])
        self.private = normalize_case_source(self.corpus.get_chunk(CASE, "private-doc", "chunk-a"))
        self.case_service = CaseService(self.corpus, self.public, self.private)
        self.graph, self.simulation = Graph(), Simulation(self.public, self.private)
        self.task_path = str(Path(self.directory.name) / "tasks.sqlite")
        tasks = TaskManager(TaskRepository(self.task_path))
        self.pipeline = NovaCourtPipelineService(self.case_service, self.graph, self.simulation,
                                                 task_manager=tasks, legal_repository=self.legal)

    def result(self):
        return self.case_service.analyze_case(CASE_TEXT, progress_callback=None, cancellation_token=None,
                                              case_id=CASE, document_ids=["private-doc"])

    def prepare(self, result=None):
        return prepare_court_context(result or self.result(), owner_id=OWNER, case_id=CASE,
                                     legal_repository=self.legal, case_corpus_repository=self.corpus)

    def test_canonical_reopen_separates_fact_evidence_and_legal_source(self):
        context = self.prepare()
        self.assertTrue(any("public.legal_units" in sql and "d.id = %s::uuid" in sql for sql in self.calls))
        self.assertEqual(context["public_legal_sources"][0]["excerpt"], DETAIL["text"])
        self.assertEqual(context["private_sources"][0]["excerpt"], "Cláusula canónica privada")
        self.assertEqual(context["facts"][0]["status"], "alleged")
        self.assertEqual(context["facts"][0]["source_ids"], [])
        self.assertEqual(len(context["evidence"]["evidence_links"]), 1)
        self.assertEqual(context["evidence"]["evidence_links"][0]["source_ids"], [self.private["source_id"]])
        graph = build_graph_input(context)
        legal = next(item for item in graph["entities"] if self.public["source_id"] in item["source_ids"])
        self.assertEqual((legal["source_scope"], legal["provenance_version"], legal["document_id"], legal["unit_id"]),
                         ("public_legal", "v2", DOCUMENT, UNIT))

    def test_invalid_v2_references_fail_closed(self):
        for change in ({"document_id": OTHER}, {"unit_id": OTHER}, {"provenance_version": "v1"},
                       {"source_id": "SRC-forged"}):
            with self.subTest(change=change):
                result = self.result()
                result["sources"][0].update(change)
                with self.assertRaises(ValueError):
                    self.prepare(result)

    def test_persisted_task_handoff_and_authorized_citations(self):
        case_task = self.pipeline.start(CASE_TEXT, CASE, tool="case", document_ids=["private-doc"], owner_id=OWNER)
        self.assertEqual(self.await_task(case_task)["status"], "completed")
        for owner, case in (("other-owner", CASE), (OWNER, "other-case")):
            with self.assertRaises(ValueError):
                self.pipeline.start(CASE_TEXT, case, document_ids=["private-doc"],
                                    reuse_task_id=case_task, owner_id=owner)
        court_task = self.pipeline.start(CASE_TEXT, CASE, document_ids=["private-doc"],
                                         reuse_task_id=case_task, owner_id=OWNER)
        task = self.await_task(court_task)
        self.assertEqual(task["status"], "completed")
        self.assertEqual(self.case_service.calls, 1)
        self.assertEqual(self.simulation.input["source_case_task_id"], case_task)
        self.assertEqual(self.simulation.input["public_legal_sources"][0]["excerpt"], DETAIL["text"])
        self.assertEqual(self.simulation.input["private_sources"][0]["source_scope"], "private_case")
        self.assertEqual({source["source_id"] for source in task["final_result"]["simulation"]["sources"]},
                         {self.public["source_id"], self.private["source_id"]})
        self.assertEqual(task["final_result"]["simulation"]["citations"][0]["provenance_version"], "v2")
        self.assertTrue(self.graph.input["provenance"])

    def test_simulator_requires_prepared_method(self):
        class LegacyOnly:
            def simulate_case(self, *args, **kwargs):
                raise AssertionError("V1 fallback called")
        result = NovaCourtSimulationOrchestrator(lambda: LegacyOnly(), enabled=True, timeout=1).simulate(
            self.prepare(), CASE_TEXT)
        self.assertEqual(result["status"], "failed")
        self.assertNotIn("V1 fallback", str(result))

    def test_browser_final_result_is_never_forwarded(self):
        app = create_app()
        manager = SimpleNamespace(tasks=SimpleNamespace(active_count=lambda owner: 0),
                                  start=Mock(return_value="court-task"))
        with app.test_request_context("/api/novacourt/analyze", method="POST", json={
                "case_text": "A" * 60, "case_id": CASE, "final_result": {"sources": ["forged"]}}), \
                patch("app.api.case.owns_case", return_value=True), \
                patch("app.api.case.authenticated_user_id", return_value=OWNER), \
                patch("app.api.case.pipeline", return_value=manager):
            g.request_id = "request"
            response, status = start_analysis()
        self.assertEqual(status, 202)
        self.assertEqual(response.json["task_id"], "court-task")
        self.assertNotIn("final_result", manager.start.call_args.kwargs)

    def test_completed_court_http_reopen_survives_manager_recreation_without_rerun(self):
        case_task = self.pipeline.start(CASE_TEXT, CASE, tool="case", document_ids=["private-doc"], owner_id=OWNER)
        self.assertEqual(self.await_task(case_task)["status"], "completed")
        app = create_app()
        with app.test_request_context("/api/novacourt/analyze", method="POST", json={
                "case_text": CASE_TEXT, "case_id": CASE, "document_ids": ["private-doc"],
                "reuse_task_id": case_task}), \
                patch("app.api.case.owns_case", return_value=True), \
                patch("app.api.case.authenticated_user_id", return_value=OWNER), \
                patch("app.api.case.pipeline", return_value=self.pipeline):
            g.request_id = "request"
            response, status = start_analysis()
        self.assertEqual(status, 202)
        court_task = response.json["task_id"]
        completed = self.await_task(court_task)
        self.assertEqual(completed["status"], "completed")
        expected = completed["final_result"]
        calls = self.case_service.calls
        restored = NovaCourtPipelineService(Mock(), Mock(), Mock(),
            task_manager=TaskManager(TaskRepository(self.task_path)), legal_repository=self.legal)
        with app.test_request_context(f"/api/novacourt/results/{court_task}?case_id={CASE}"), \
                patch("app.api.case.owns_case", return_value=True), \
                patch("app.api.case.authenticated_user_id", return_value=OWNER), \
                patch("app.api.case.pipeline", return_value=restored):
            g.request_id = "request"
            reopened = task_status(court_task)
        self.assertEqual(reopened.json["status"], "completed")
        self.assertEqual(reopened.json["final_result"], expected)
        self.assertEqual(self.case_service.calls, calls)
        restored.case_service.analyze_case.assert_not_called()
        restored.graph_service.build_for_case.assert_not_called()
        restored.simulation_service.simulate_for_case.assert_not_called()
        self.assertIsNone(restored.scoped_status("owner-b", CASE, court_task, tool="court"))
        self.assertIsNone(restored.scoped_status(OWNER, "case-b", court_task, tool="court"))
        self.assertIsNone(restored.scoped_status(OWNER, CASE, case_task, tool="court"))
        self.assertIsNone(restored.scoped_status(OWNER, CASE, "unknown", tool="court"))
        for owner, case_id, task_id in (("owner-b", CASE, court_task), (OWNER, "case-b", court_task),
                                        (OWNER, CASE, case_task), (OWNER, CASE, "unknown")):
            with app.test_request_context(f"/api/novacourt/results/{task_id}?case_id={case_id}"), \
                    patch("app.api.case.owns_case", return_value=True), \
                    patch("app.api.case.authenticated_user_id", return_value=owner), \
                    patch("app.api.case.pipeline", return_value=restored):
                g.request_id = "request"
                denied, code = task_status(task_id)
            self.assertEqual(code, 404)
            self.assertNotIn(DOCUMENT, str(denied.json))

    def test_terminal_states_and_active_restart_are_scoped(self):
        manager = self.pipeline.tasks
        metadata = {"owner_id": OWNER, "case_id": CASE, "tool": "court"}
        failed = manager.create_task("legal_analysis", metadata)
        manager.update_task(failed, status=TaskStatus.PROCESSING)
        manager.fail_task(failed, {"code": "ANALYSIS_FAILED", "message": "No fue posible completar la tarea."})
        cancelled = manager.create_task("legal_analysis", metadata)
        self.assertTrue(manager.cancel_task(cancelled))
        active = manager.create_task("legal_analysis", metadata)
        manager.update_task(active, status=TaskStatus.PROCESSING)
        pending = manager.create_task("legal_analysis", metadata)
        restored = NovaCourtPipelineService(Mock(), Mock(), Mock(),
            task_manager=TaskManager(TaskRepository(self.task_path)))
        for task_id, expected in ((failed, "failed"), (cancelled, "cancelled"),
                                  (active, "interrupted"), (pending, "interrupted")):
            task = restored.scoped_status(OWNER, CASE, task_id, tool="court")
            self.assertEqual(task["status"], expected)
            self.assertIsNone(task["final_result"])
            self.assertIsNone(restored.scoped_status("owner-b", CASE, task_id, tool="court"))


if __name__ == "__main__":
    unittest.main()
