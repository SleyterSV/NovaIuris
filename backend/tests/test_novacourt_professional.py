"""Canonical Court flow tests; all provider boundaries are replaced with fakes."""
import unittest
import time
from copy import deepcopy
from unittest.mock import Mock, patch

from app.services.novacourt_pipeline_service import NovaCourtPipelineService
from app import create_app
from app.config import Config
from app.services.court_simulation import LegalDebateSimulator
from app.utils.court_roles import resolve_court_roles
from app.utils.novacourt_simulation import NovaCourtSimulationOrchestrator
from tests.test_stabilization import await_task


PUBLIC = {"source_id": "SRC-PUBLIC01", "source_scope": "public", "source_type": "legislation",
          "title": "Norma recuperada", "excerpt": "Texto recuperado", "official_url": None}
PRIVATE = {"source_id": "SRC-PRIVATE01", "source_scope": "case", "source_type": "case_document",
           "title": "Contrato", "excerpt": "Cláusula concreta", "case_id": "CASE-A",
           "document_id": "DOC-A", "chunk_id": "CHUNK-A", "page_start": 2}


class FakeCase:
    def __init__(self):
        self.calls = 0

    def analyze_case(self, text, *, progress_callback, cancellation_token, case_id, document_ids):
        self.calls += 1
        progress_callback("intake", "completed")
        return {"success": True, "case_id": case_id, "case": text, "document_ids": list(document_ids),
                "analysis": {"tipo_proceso": "civil"},
                "facts": [{"fact_id": "FACT-1", "text": "Alegación", "status": "alleged"}],
                "issues": [{"issue_id": "ISSUE-1", "text": "Problema"}],
                "sources": [deepcopy(PUBLIC), deepcopy(PRIVATE)] if case_id == "CASE-A" else [deepcopy(PUBLIC)],
                "report": "Informe del caso", "strategy": {"claim_strategy": "No es simulación"}}


class FakeGraph:
    def __init__(self, status="ready"):
        self.status = status

    def build_for_case(self, case_result, cancellation_token=None):
        return {"status": self.status, "case_id": case_result["case_id"], "nodes": [], "edges": []}


class FakeSimulation:
    def __init__(self, status="ready"):
        self.status = status

    def simulate_for_case(self, case_result, case_text, cancellation_token=None):
        return {"status": self.status, "case_id": case_result["case_id"],
                "prosecutor": {"content": "Tesis [SRC-PUBLIC01] y contrato [SRC-PRIVATE01]."},
                "defense": {"content": "Objeción [SRC-FAKE001]."},
                "judge": {"content": "Decisión simulada [SRC-PUBLIC01]."}}


class CourtProfessionalTests(unittest.TestCase):
    def pipeline(self, graph="ready", simulation="ready"):
        case = FakeCase()
        return NovaCourtPipelineService(case, FakeGraph(graph), FakeSimulation(simulation)), case

    def test_explicit_reuse_and_mismatch_rejection(self):
        pipeline, case = self.pipeline()
        case_task = pipeline.start("Relato CASE-A", "CASE-A", tool="case", document_ids=["DOC-A"])
        self.assertEqual(await_task(pipeline, case_task)["status"], "completed")
        court_task = pipeline.start("Relato CASE-A", "CASE-A", document_ids=["DOC-A"], reuse_task_id=case_task)
        result = await_task(pipeline, court_task)["final_result"]
        self.assertEqual(case.calls, 1)
        self.assertTrue(result["metadata"]["case_reused"])
        self.assertEqual(result["facts"][0]["status"], "alleged")
        self.assertEqual(result["court_status"], "completed")
        for changes in ({"case_id": "CASE-B"}, {"document_ids": []}, {"case_text": "Otro relato"},
                        {"reuse_task_id": "00000000-0000-0000-0000-000000000000"}):
            options = {"case_text": "Relato CASE-A", "case_id": "CASE-A", "document_ids": ["DOC-A"],
                       "reuse_task_id": case_task}
            options.update(changes)
            with self.assertRaises(ValueError):
                pipeline.start(**options)

    def test_new_case_has_no_private_source_from_previous_case(self):
        pipeline, case = self.pipeline()
        await_task(pipeline, pipeline.start("Relato A", "CASE-A", document_ids=["DOC-A"]))
        result = await_task(pipeline, pipeline.start("Relato B", "CASE-B"))["final_result"]
        self.assertEqual(case.calls, 2)
        self.assertEqual(result["case_id"], "CASE-B")
        self.assertNotIn("Contrato", str(result))
        self.assertFalse(result["metadata"]["case_reused"])

    def test_citations_and_report_only_use_verified_sources(self):
        pipeline, _ = self.pipeline()
        result = await_task(pipeline, pipeline.start("Relato A", "CASE-A", document_ids=["DOC-A"]))["final_result"]
        simulation = result["simulation"]
        self.assertEqual([source["source_id"] for source in simulation["sources"]],
                         ["SRC-PUBLIC01", "SRC-PRIVATE01"])
        self.assertNotIn("SRC-FAKE001", str(simulation))
        self.assertEqual(result["court_report_document"]["sources"], simulation["sources"])
        self.assertEqual(simulation["projection"], {})
        self.assertIn("[1]", simulation["prosecutor"]["content"])
        self.assertIn("[1]", simulation["judge"]["content"])
        self.assertTrue(any(item["code"] == "INVALID_SOURCE_MARKER" for item in result["warnings"]))

    def test_secondary_failures_preserve_case(self):
        for graph, simulation in (("failed", "ready"), ("ready", "failed"), ("failed", "failed")):
            with self.subTest(graph=graph, simulation=simulation):
                pipeline, _ = self.pipeline(graph, simulation)
                result = await_task(pipeline, pipeline.start("Relato", "CASE-A", document_ids=["DOC-A"]))["final_result"]
                self.assertEqual(result["court_status"], "partial")
                self.assertEqual(result["facts"][0]["status"], "alleged")
                self.assertEqual(result["graph"]["status"], graph)
                self.assertEqual(result["simulation"]["status"], simulation)
                if simulation == "failed":
                    self.assertEqual(result["court_report_document"]["sections"], [])
                    self.assertNotIn("claim_strategy", str(result["simulation"]))

    def test_private_source_or_secondary_identity_mismatch_never_reaches_other_branch(self):
        pipeline, _ = self.pipeline()
        pipeline.case_service.analyze_case = Mock(return_value={"success": True, "case_id": "CASE-A",
            "case": "Relato", "document_ids": [], "sources": [{**PRIVATE, "case_id": "CASE-B"}]})
        task = await_task(pipeline, pipeline.start("Relato", "CASE-A"))
        self.assertEqual(task["status"], "failed")

        pipeline, _ = self.pipeline()
        pipeline.graph_service.build_for_case = Mock(return_value={"status": "ready", "case_id": "CASE-B"})
        result = await_task(pipeline, pipeline.start("Relato", "CASE-A"))["final_result"]
        self.assertEqual(result["graph"]["status"], "failed")
        self.assertEqual(result["graph"]["case_id"], "CASE-A")
        self.assertEqual(result["simulation"]["status"], "ready")

    def test_cancel_after_graph_prevents_simulation(self):
        pipeline, _ = self.pipeline()
        def cancel_during_graph(case_result, cancellation_token=None):
            cancellation_token.cancel()
            return {"status": "ready"}
        pipeline.graph_service.build_for_case = cancel_during_graph
        pipeline.simulation_service.simulate_for_case = Mock()
        task = await_task(pipeline, pipeline.start("Relato", "CASE-A"))
        self.assertEqual(task["status"], "cancelled")
        pipeline.simulation_service.simulate_for_case.assert_not_called()

    def test_citation_validation_failure_keeps_case_and_graph_without_unverified_text(self):
        pipeline, _ = self.pipeline()
        with patch("app.services.novacourt_pipeline_service.resolve_citations", side_effect=RuntimeError("private")):
            result = await_task(pipeline, pipeline.start("Relato", "CASE-A"))["final_result"]
        self.assertEqual(result["court_status"], "partial")
        self.assertEqual(result["graph"]["status"], "ready")
        self.assertEqual(result["simulation"]["status"], "failed")
        self.assertEqual(result["court_report_document"]["sections"], [])
        self.assertEqual(result["facts"][0]["status"], "alleged")
        self.assertNotIn("private", str(result))

    def test_incomplete_position_is_not_published_as_ready_simulation(self):
        pipeline, _ = self.pipeline()
        pipeline.simulation_service.simulate_for_case = Mock(return_value={"status": "ready",
            "prosecutor": {"content": "Solo una postura"}})
        result = await_task(pipeline, pipeline.start("Relato", "CASE-A"))["final_result"]
        self.assertEqual(result["simulation"]["status"], "failed")
        self.assertEqual(result["court_report_document"]["sections"], [])

    def test_role_labels_are_deterministic(self):
        expectations = {"penal": ("Fiscalía", "Defensa"), "civil": ("Parte demandante", "Parte demandada"),
                        "constitucional": ("Parte recurrente", "Parte recurrida"),
                        "desconocida": ("Parte promotora", "Parte contraria")}
        for area, expected in expectations.items():
            roles = resolve_court_roles({"analysis": {"tipo_proceso": area}})
            self.assertEqual(tuple(roles.values()), expected)

    def test_task_api_requires_matching_case_id_for_status_and_cancellation(self):
        class TestConfig(Config):
            TESTING = True
            RATE_LIMIT_ENABLED = False
            CASE_SERVICE_FACTORY = FakeCase
            GRAPH_SERVICE_FACTORY = FakeGraph
            SIMULATION_SERVICE_FACTORY = FakeSimulation
        client = create_app(TestConfig).test_client()
        started = client.post('/api/case/tasks', json={"case_text": "Relato " * 12, "case_id": "CASE-A"})
        self.assertEqual(started.status_code, 202)
        task_id = started.json["task_id"]
        deadline = time.monotonic() + 2
        while time.monotonic() < deadline:
            response = client.get(f'/api/tasks/{task_id}?case_id=CASE-A')
            if response.json["status"] == "completed":
                break
            time.sleep(.005)
        self.assertEqual(response.json["case_id"], "CASE-A")
        self.assertEqual(client.get(f'/api/tasks/{task_id}?case_id=CASE-B').status_code, 404)
        self.assertEqual(client.get(f'/api/tasks/{task_id}').status_code, 404)
        self.assertEqual(client.post(f'/api/tasks/{task_id}/cancel', json={"case_id": "CASE-B"}).status_code, 404)
        text = "Relato " * 12
        self.assertEqual(client.post('/api/novacourt/analyze', json={"case_text": text,
            "case_id": "CASE-B", "reuse_task_id": task_id}).status_code, 409)
        self.assertEqual(client.post('/api/novacourt/analyze', json={"case_text": text,
            "case_id": "CASE-A", "reuse_task_id": "00000000-0000-0000-0000-000000000000"}).status_code, 409)

    def test_canonical_simulation_skips_legacy_vector_ingestion_and_metrics(self):
        with patch.object(LegalDebateSimulator, "_vectorizar_expediente_vivo") as ingest, \
             patch.object(LegalDebateSimulator, "_generar_metricas") as metrics, \
             patch("app.services.court_simulation.nova_iuris_tribunal") as tribunal:
            tribunal.invoke.return_value = {"argumento_fiscal": "Posición A", "argumento_defensa": "Posición B",
                                            "veredicto_juez": "Decisión simulada"}
            orchestrator = NovaCourtSimulationOrchestrator(LegalDebateSimulator, enabled=True, timeout=1)
            result = orchestrator.simulate({"case_id": "CASE-A", "analysis": {"tipo_proceso": "civil"}}, "Relato")
            self.assertEqual(result["status"], "ready")
            self.assertEqual(result["prosecutor"]["role_label"], "Parte demandante")
            ingest.assert_not_called()
            metrics.assert_not_called()
            tribunal.invoke.assert_called_once()


if __name__ == "__main__":
    unittest.main()
