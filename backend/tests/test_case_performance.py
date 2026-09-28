import json
import threading
import unittest
from unittest.mock import Mock

from app.services.case_execution import CaseExecutionContext, prompt_documents, research_queries
from app.services.case_corpus import CaseContextService
from app.utils.cancellation import CancellationToken, OperationCancelled
from scripts.bench_case_synthetic import run_scenario
from tests.test_stabilization import case_service


class CasePerformanceTests(unittest.TestCase):
    def test_research_deduplicates_safe_variants_and_keeps_distinct_questions(self):
        self.assertEqual(research_queries([
            "  artículo 1969   responsabilidad ",
            "ARTÍCULO 1969 RESPONSABILIDAD", "artículo 1970 responsabilidad",
            "¿Prescribió la acción?", "¿Prescribió el recurso?",
        ], 4), ["artículo 1969 responsabilidad", "artículo 1970 responsabilidad",
               "¿Prescribió la acción?", "¿Prescribió el recurso?"])
        self.assertEqual(research_queries(["A", "B"], 0), ["A"])

    def test_document_projection_preserves_exact_excerpt_and_location_without_duplicate_text(self):
        original = [{"id": "CH-1", "texto": "full duplicate" * 300,
                     "extracto_exacto": "full duplicate" * 300, "source": {
                         "source_id": "SRC-CASEA001", "source_scope": "case", "case_id": "CASE-A",
                         "document_id": "DOC-A", "chunk_id": "CH-1", "page_start": 27,
                         "excerpt": "Exact fragment", "title": "contract.pdf"}}]
        projected = prompt_documents(original)
        self.assertEqual(projected[0]["texto"], "Exact fragment")
        self.assertEqual(projected[0]["page_start"], 27)
        self.assertEqual(projected[0]["case_id"], "CASE-A")
        self.assertEqual(projected[0]["source_id"], "SRC-CASEA001")
        self.assertNotIn("source", projected[0])
        self.assertLess(len(json.dumps(projected)), len(json.dumps(original)))

    def test_request_local_reuse_includes_case_document_version_query_and_filters(self):
        calls = []
        def load(label):
            calls.append(label)
            return [{"text": label}]
        case_a = CaseExecutionContext("CASE-A", (("DOC-1", "1", "HASH-A"),))
        self.assertEqual(case_a.case_context("hechos", lambda: load("A")),
                         case_a.case_context("hechos", lambda: load("wrong")))
        self.assertEqual(calls, ["A"])
        self.assertEqual(case_a.research("consulta", {"modulo": "Civil"}, lambda: load("public")),
                         case_a.research("consulta", {"modulo": "Civil"}, lambda: load("wrong")))
        self.assertEqual(len(calls), 2)
        case_a.research("consulta", {"modulo": "Penal"}, lambda: load("other filter"))
        CaseExecutionContext("CASE-A", (("DOC-1", "2", "HASH-B"),)).case_context(
            "hechos", lambda: load("new version"))
        case_b = CaseExecutionContext("CASE-B", (("DOC-1", "1", "HASH-A"),))
        self.assertEqual(case_b.case_context("hechos", lambda: load("B")), [{"text": "B"}])
        self.assertEqual(calls, ["A", "public", "other filter", "new version", "B"])

    def test_search_calls_once_per_unique_query_and_metrics_count_real_progress_events(self):
        service = case_service()
        service.strategy_builder.build_strategy.return_value = {
            "search_queries": ["Civil   contrato", "civil contrato", "prescripción contractual"]}
        original = service.search_service.search.return_value
        def search(**kwargs):
            kwargs["progress_callback"]("embedding", "running")
            kwargs["progress_callback"]("retrieval", "running")
            return original
        service.search_service.search.side_effect = search
        result = service.analyze_case("Caso A", case_id="CASE-A")
        self.assertEqual(service.search_service.search.call_count, 2)
        self.assertEqual(result["research"]["queries"], ["Civil contrato", "prescripción contractual"])
        self.assertEqual(result["metadata"]["counts"]["llm_service_call_count"], 7)
        self.assertEqual(result["metadata"]["counts"]["research_service_call_count"], 2)
        self.assertEqual(result["metadata"]["counts"]["embedding_call_count"], 2)
        self.assertEqual(result["metadata"]["counts"]["retrieval_call_count"], 2)
        self.assertGreaterEqual(result["metadata"]["timings_ms"]["total"], 0)
        self.assertIn("evidence", result["metadata"]["timings_ms"])
        self.assertIn("risks", result["metadata"]["timings_ms"])
        self.assertEqual(result["metadata"]["input_characters"]["user_statement"], len("Caso A"))
        for field in ("facts", "issues", "timeline", "sources", "citations", "report_document", "warnings"):
            self.assertIn(field, result)

    def test_evidence_and_risks_overlap_without_sharing_other_case_state(self):
        for case_id in ("CASE-A", "CASE-B"):
            service = case_service()
            evidence_started, risk_started = threading.Event(), threading.Event()
            evidence_value = service.evidence_analyzer.analyze.return_value
            risk_value = service.risk_analyzer.analyze.return_value
            def evidence(**_):
                evidence_started.set()
                self.assertTrue(risk_started.wait(0.5))
                return evidence_value
            def risk(**_):
                risk_started.set()
                self.assertTrue(evidence_started.wait(0.5))
                return risk_value
            service.evidence_analyzer.analyze.side_effect = evidence
            service.risk_analyzer.analyze.side_effect = risk
            result = service.analyze_case("Relato", case_id=case_id)
            self.assertEqual(result["case_id"], case_id)
            self.assertEqual(result["metadata"]["case_id"], case_id)

    def test_cancellation_after_strategy_prevents_new_search(self):
        service, token = case_service(), CancellationToken()
        strategy = service.strategy_builder.build_strategy.return_value
        def cancel_after_strategy(_):
            token.cancel()
            return strategy
        service.strategy_builder.build_strategy.side_effect = cancel_after_strategy
        with self.assertRaises(OperationCancelled):
            service.analyze_case("Relato", cancellation_token=token, case_id="CASE-A")
        service.search_service.search.assert_not_called()

    def test_private_retrieval_reports_only_started_operations_and_honors_cancellation(self):
        repository, embedding = Mock(), Mock()
        repository.validate_documents.return_value = True
        repository.iter_retrieve.return_value = iter(())
        embedding.generate_embedding.return_value = [1.0]
        events = []
        context = CaseContextService(repository, embedding)
        self.assertEqual(context.relevant_context("CASE-A", "hechos", document_ids=["DOC-A"],
                                                 operation_callback=events.append), [])
        self.assertEqual(events, ["embedding", "retrieval"])
        token = CancellationToken()
        token.cancel()
        with self.assertRaises(OperationCancelled):
            context.relevant_context("CASE-A", "hechos", document_ids=["DOC-A"],
                                     cancellation_token=token, operation_callback=events.append)
        self.assertEqual(events, ["embedding", "retrieval"])
        self.assertEqual(embedding.generate_embedding.call_count, 1)

    def test_synthetic_harness_preserves_contract_and_reduces_duplicate_work(self):
        medium = run_scenario("medium", delay_seconds=0)
        large = run_scenario("large_document", delay_seconds=0)
        self.assertEqual(medium["research_calls"], 2)
        self.assertEqual(medium["embedding_operations"], 2)
        self.assertEqual(large["private_context_calls"], 1)
        self.assertEqual(large["retrieval_operations"], 3)
        self.assertEqual(large["llm_service_calls"], 7)
        self.assertIn("report_document", large["result_keys"])
        self.assertIn("citations", large["result_keys"])


if __name__ == "__main__":
    unittest.main()
