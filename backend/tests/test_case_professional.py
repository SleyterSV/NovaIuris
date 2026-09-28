import unittest
from unittest.mock import patch

from app.services.case_professional import (
    build_report_document, case_facts, case_issues, case_timeline,
    final_strategy, ground_links, select_report_sources,
)
from app.services.case_report_service import CaseReportService
from app.services.counter_argument_service import CounterArgumentService
from app.services.evidence_analyzer import EvidenceAnalyzer
from app.services.risk_analyzer import RiskAnalyzer
from app.services.source_contracts import resolve_citations
from tests.test_stabilization import case_service


class CaseProfessionalTests(unittest.TestCase):
    def setUp(self):
        self.private_a = {
            "source_id": "SRC-CASEA001", "source_scope": "case", "case_id": "CASE-A",
            "document_id": "DOC-A", "chunk_id": "CH-A", "excerpt": "Fragmento A",
        }
        self.private_b = {
            "source_id": "SRC-CASEB001", "source_scope": "case", "case_id": "CASE-B",
            "document_id": "DOC-B", "chunk_id": "CH-B", "excerpt": "Fragmento B",
        }

    def test_explicit_dates_include_spanish_month_names_and_reject_invalid(self):
        analysis = {"hechos": [
            "Ocurrió el 2026-02-26", "Presentación el 15/04/2025",
            "Audiencia el 26 de febrero de 2026", "Evento el 10 de setiembre de 2022",
            "Evento el 1 de septiembre de 2019", "Evento el 31 de febrero de 2020",
            "Se presentó durante el año 2024",
        ]}
        dates = [item["date"] for item in case_facts(analysis, [], "CASE-A")]
        self.assertEqual(dates, ["2026-02-26", "2025-04-15", "2026-02-26",
                                 "2022-09-10", "2019-09-01", None, None])

    def test_allegations_do_not_become_proven_facts_from_a_source_marker(self):
        facts = case_facts({"hechos_estructurados": [
            {"text": "Se entregó el bien [SRC-CASEA001]", "source_ids": ["SRC-CASEA001"]},
            {"text": "El recibo acredita el pago", "status": "supported", "source_ids": ["SRC-CASEA001"]},
            {"text": "Fue pagado", "status": "supported", "source_ids": ["SRC-CASEB001"]},
            {"text": "Entrega alegada", "status": "disputed", "source_ids": ["SRC-CASEA001"]},
        ]}, [self.private_a, self.private_b], "CASE-A")
        self.assertEqual([fact["status"] for fact in facts], ["alleged", "supported", "alleged", "disputed"])
        self.assertEqual(facts[0]["source_ids"], ["SRC-CASEA001"])
        self.assertEqual(facts[1]["source_ids"], ["SRC-CASEA001"])
        self.assertEqual(facts[2]["source_ids"], [])
        self.assertNotIn("[SRC-", facts[0]["text"])

    def test_timeline_is_explicit_and_chronological(self):
        facts = case_facts({"hechos": [
            "Demanda presentada el 15 de abril de 2025", "Contrato firmado el 26 de febrero de 2026",
            "El plazo venció posteriormente",
        ]}, [], "CASE-A")
        timeline = case_timeline(facts)
        self.assertEqual([item["date"] for item in timeline], ["2025-04-15", "2026-02-26"])
        self.assertEqual([item["fact_id"] for item in timeline], [facts[0]["fact_id"], facts[1]["fact_id"]])

    def test_issue_ids_are_stable_and_ground_links_preserve_content(self):
        first = case_issues({"problemas_juridicos": ["¿Se incumplió el contrato?", {"issue": "¿Venció el plazo?"}]}, "CASE-A")
        second = case_issues({"problemas_juridicos": ["¿Se incumplió el contrato?", {"issue": "¿Venció el plazo?"}]}, "CASE-A")
        self.assertEqual(first, second)
        reversed_issues = case_issues({"problemas_juridicos": ["¿Venció el plazo?", "¿Se incumplió el contrato?"]}, "CASE-A")
        self.assertEqual({item["text"]: item["issue_id"] for item in first},
                         {item["text"]: item["issue_id"] for item in reversed_issues})
        grounded = ground_links([
            {"argument": "Se incumplió", "issue_id": first[0]["issue_id"],
             "fact_ids": ["FACT-NOPE"], "source_ids": ["SRC-CASEB001"]},
            "Argumento legado válido",
        ], first, [], [self.private_a, self.private_b], "CASE-A")
        self.assertEqual(grounded[0]["argument"], "Se incumplió")
        self.assertEqual(grounded[0]["issue_id"], first[0]["issue_id"])
        self.assertEqual(grounded[0]["fact_ids"], [])
        self.assertEqual(grounded[0]["source_ids"], [])
        self.assertEqual(grounded[1], "Argumento legado válido")

    def test_final_strategy_projects_existing_work_without_inference(self):
        result = final_strategy(
            {"pretension_principal": "Resolución contractual", "informacion_faltante": ["fecha"]},
            {"claim_strategy": "Acreditar incumplimiento", "recommended_actions": ["Revisar contrato"]},
            {"main_arguments": [{"text": "Argumento"}]},
            {"documentary_evidence": ["Contrato"]}, {"critical_risks": ["Plazo"]},
            {"main_counterarguments": ["Pago alegado"]},
        )
        self.assertEqual(result["objective"], "Resolución contractual")
        self.assertEqual(result["priority_evidence"], ["Contrato"])
        self.assertEqual(result["opposing_positions"], ["Pago alegado"])

    def test_report_document_keeps_only_used_sources_and_section_citations(self):
        source_a = {"source_id": "SRC-CASEA001", "source_scope": "case", "case_id": "CASE-A", "excerpt": "A"}
        source_b = {"source_id": "SRC-PUBLIC01", "source_scope": "public", "excerpt": "B"}
        resolved = resolve_citations(
            "# Informe\n\n## I. Análisis jurídico\nRegla aplicable [SRC-PUBLIC01].\n\n## XI. Conclusiones\nConclusión del caso.",
            [source_a, source_b], "CASE-A")
        document = build_report_document(resolved["answer"], "CASE-A", resolved["citations"], resolved["sources_used"])
        self.assertEqual(document["document_type"], "analysis_report")
        self.assertEqual(document["case_id"], "CASE-A")
        self.assertEqual(len(document["sections"]), 2)
        self.assertEqual(document["sections"][0]["citation_ids"], [resolved["citations"][0]["citation_id"]])
        self.assertEqual(document["sections"][1]["citation_ids"], [])
        self.assertEqual([source["source_id"] for source in document["sources"]], ["SRC-PUBLIC01"])

    def test_invalid_markers_are_not_citations_and_numeric_text_is_preserved(self):
        result = resolve_citations("Véase el artículo 1 [1] y [SRC-FAKE001].", [], "CASE-A")
        self.assertEqual(result["citations"], [])
        self.assertEqual(result["answer"], "Véase el artículo 1 [1] y .")
        self.assertIn("INVALID_SOURCE_MARKER", [warning["code"] for warning in result["warnings"]])

    def test_report_failure_preserves_structured_analysis(self):
        service = case_service()
        service.report_service.generate_report.side_effect = RuntimeError("provider internals")
        result = service.analyze_case("Expediente A", case_id="CASE-A")
        self.assertTrue(result["success"])
        self.assertEqual(result["status"], "partial")
        self.assertEqual(result["report_status"], "failed")
        self.assertEqual(result["report_error"]["code"], "REPORT_FAILED")
        self.assertEqual(result["facts"][0]["text"], "HECHO-A")
        self.assertTrue(result["research"])
        self.assertTrue(result["arguments"])
        self.assertTrue(result["evidence"])
        self.assertTrue(result["risks"])
        self.assertNotIn("provider internals", str(result))

    def test_citation_failure_preserves_structured_analysis(self):
        service = case_service()
        service.report_service.generate_report.return_value = (
            "## Análisis jurídico\n" + "Razonamiento suficiente. " * 10 +
            "\n## Conclusiones\nConclusión."
        )
        with patch("app.services.case_service.resolve_citations", side_effect=RuntimeError("resolver detail")):
            result = service.analyze_case("Expediente A", case_id="CASE-A")
        self.assertTrue(result["success"])
        self.assertEqual(result["status"], "partial")
        self.assertEqual(result["report_status"], "failed")
        self.assertEqual(result["citations"], [])
        self.assertTrue(result["analysis"])
        self.assertTrue(result["final_strategy"])

    def test_report_source_selection_is_case_scoped_and_deduplicated(self):
        selected = select_report_sources([self.private_a], [self.private_a, self.private_b], "CASE-A")
        self.assertEqual(len(selected), 1)
        self.assertEqual(selected[0]["case_id"], "CASE-A")

    def test_report_validation_is_adaptive_and_prompt_uses_only_verified_sources(self):
        report = ("## I. Objeto y alcance\n" + "Alcance concreto. " * 9 +
                  "\n## II. Análisis de la controversia\n" + "Análisis aplicado. " * 10 +
                  "\n## III. Conclusiones\nConclusión concreta.")
        self.assertTrue(CaseReportService.validate_report(report))
        self.assertFalse(CaseReportService.validate_report("## Análisis\n## Conclusiones"))
        prompt = CaseReportService._build_prompt(
            case_text="Alegación del usuario", analysis={"normas_probables": ["Norma hipotética"]},
            strategy={}, legal_arguments={}, evidence_analysis={}, risk_analysis={},
            counter_arguments={}, research={"status": "completed"}, sources=[self.private_a],
            facts=[], issues=[], timeline=[], final_strategy={}, case_id="CASE-A")
        self.assertIn("SRC-CASEA001", prompt)
        self.assertIn("normas preliminares", prompt)
        self.assertNotIn("Norma hipotética", prompt)

    def test_active_case_result_drops_legacy_numeric_scores_and_keeps_only_retrieved_law(self):
        service = case_service()
        service.strategy_builder.build_strategy.return_value = {
            "search_queries": ["consulta 1", "consulta 2", "consulta 3", "consulta 4", "consulta 5", "consulta 6"],
            "claim_strategy": "Estrategia inicial",
        }
        service.evidence_analyzer.analyze.return_value = {
            "available_evidence": ["PRUEBA-A"], "documentary_evidence": ["PRUEBA-A"],
            "missing_evidence": [], "evidence_strength": "Media", "evidence_score": 87,
            "evidence_links": [],
        }
        service.risk_analyzer.analyze.return_value = {
            "risk_level": "Medio", "critical_risks": [], "procedural_risks": [],
            "legal_risks": [], "evidentiary_risks": [], "overall_probability": 73,
        }
        service.counter_argument_service.generate_counterarguments.return_value = {
            "main_counterarguments": [], "procedural_exceptions": [], "legal_defenses": [],
            "attacks_on_evidence": [], "opponent_success_probability": 62,
        }
        result = service.analyze_case("Caso de prueba", case_id="CASE-A")
        self.assertEqual(service.search_service.search.call_count, 4)
        self.assertNotIn("evidence_score", result["evidence"])
        self.assertNotIn("overall_probability", result["risks"])
        self.assertNotIn("opponent_success_probability", result["counter_arguments"])
        self.assertNotIn("NORMA-A", [source["title"] for source in result["sources"]])

    def test_analyzer_contracts_do_not_require_or_summarize_fake_scores(self):
        self.assertFalse(hasattr(EvidenceAnalyzer, "calculate_evidence_score"))
        self.assertFalse(hasattr(RiskAnalyzer, "calculate_case_score"))
        self.assertFalse(hasattr(CounterArgumentService, "calculate_opponent_score"))
        self.assertTrue(EvidenceAnalyzer.validate_evidence({
            "available_evidence": [], "documentary_evidence": [], "missing_evidence": [],
            "evidence_strength": "DESCONOCIDA", "evidence_links": [],
        }))
        self.assertNotIn("evidence_score", EvidenceAnalyzer.summary({}))
        self.assertTrue(RiskAnalyzer.validate_risk({
            "risk_level": "DESCONOCIDO", "critical_risks": [], "procedural_risks": [],
            "legal_risks": [], "evidentiary_risks": [],
        }))
        self.assertNotIn("overall_probability", RiskAnalyzer.summary({}))
        self.assertTrue(CounterArgumentService.validate_counterarguments({
            "main_counterarguments": [], "procedural_exceptions": [],
            "legal_defenses": [], "attacks_on_evidence": [],
        }))
        self.assertNotIn("opponent_success_probability", CounterArgumentService.summary({}))


if __name__ == "__main__":
    unittest.main()
