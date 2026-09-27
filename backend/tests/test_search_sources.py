import re
import unittest
from unittest.mock import Mock, patch

from app.services.answer_service import AnswerService
from app.services.citation_service import CitationService
from app.services.context_builder import ContextBuilder
from app.services.legal_repository import LegalRepository, LegalSearchError
from app.services.search_service import SearchService


class SearchSourceTests(unittest.TestCase):
    def make_service(self, rows):
        service = SearchService.__new__(SearchService)
        service.query_analyzer = Mock()
        service.query_analyzer.analyze.return_value = {"normalized_query": "civil query", "rama": "Civil"}
        service.repository = Mock()
        service.repository.semantic_search.return_value = rows
        service.fusion_service = Mock()
        service.fusion_service.fuse.side_effect = lambda vector_results: vector_results
        class FakeReranker:
            last_failed = False
            def rerank(self, query, documents, cancellation_token=None):
                return documents
        service.reranker = FakeReranker()
        service.citation_service = CitationService()
        service.context_builder = ContextBuilder()
        service.answer_service = Mock()
        def answer(query, context):
            marker = re.search(r"\[(SRC-[A-Za-z0-9_-]+)\]", context).group(0)
            return {"answer": f"El fundamento aplicable se relaciona con responsabilidad {marker}."}
        service.answer_service.generate_answer.side_effect = answer
        service.answer_service.clean_answer.side_effect = AnswerService.clean_answer
        return service

    def test_search_context_markers_resolve_and_result_metadata_survives(self):
        service = self.make_service([{"id": "P-1", "fuente": "Código Civil", "tipo_documento": "legislation",
            "articulo": "Artículo 1969", "texto": "Conforme al artículo 1969, quien causa daño está obligado a indemnizar.",
            "entidad": "Congreso", "expediente": None, "metadata": {"official_url": "https://official.test/cc"},
            "similarity": 0.91, "rerank_score": 87}])
        with patch("app.services.search_service.EmbeddingService") as embeddings:
            embeddings.return_value.generate_embedding.return_value = [0.1, 0.2]
            result = service.search("consulta", use_reranker=False)
        self.assertEqual(result["result_status"], "completed")
        self.assertIn("[1]", result["answer"])
        self.assertEqual(len(result["citations"]), 1)
        self.assertEqual(result["sources"][0]["article"], "Artículo 1969")
        self.assertEqual(result["sources"][0]["excerpt"], result["documents"][0]["source"]["excerpt"])
        document = result["documents"][0]
        self.assertEqual(document["article"], "Artículo 1969")
        self.assertEqual(document["source_id"], result["citations"][0]["source_id"])
        self.assertEqual(document["official_url"], "https://official.test/cc")
        self.assertEqual(document["vector_similarity"], 0.91)
        self.assertEqual(document["reranker_score"], 87)
        self.assertNotIn("score", document)
        self.assertEqual(result["detected_legal_mentions"][0]["type"], "articulo")

    def test_empty_search_is_distinct_from_repository_failure(self):
        service = self.make_service([])
        with patch("app.services.search_service.EmbeddingService") as embeddings:
            embeddings.return_value.generate_embedding.return_value = [0.1, 0.2]
            empty = service.search("consulta", use_reranker=False)
        self.assertEqual(empty["result_status"], "no_results")
        self.assertEqual(empty["warnings"][0]["code"], "NO_RESULTS")

        repository = LegalRepository.__new__(LegalRepository)
        execution = Mock()
        execution.execute.side_effect = RuntimeError("private provider details")
        repository.supabase = Mock()
        repository.supabase.rpc.return_value = execution
        with self.assertRaises(LegalSearchError):
            repository.semantic_search([0.1], limit=3)

    def test_search_api_returns_safe_search_failed_status(self):
        from app import create_app
        from app.config import Config
        class FailedSearch:
            def search(self, **kwargs):
                raise LegalSearchError("internal database details must stay private")
        class TestConfig(Config):
            TESTING = True
            RATE_LIMIT_ENABLED = False
            SEARCH_SERVICE_FACTORY = staticmethod(FailedSearch)
        response = create_app(TestConfig).test_client().post("/api/search", json={"query": "civil"})
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json["error"]["code"], "SEARCH_FAILED")
        self.assertNotIn("internal database details", str(response.json))

    def test_case_research_keeps_repository_failure_distinct_from_no_results(self):
        from tests.test_stabilization import case_service
        case = case_service()
        case.search_service.search.side_effect = LegalSearchError("provider detail")
        failed = case.analyze_case("case text", case_id="CASE-A")
        self.assertEqual(failed["research"]["status"], "search_failed")
        self.assertEqual(failed["research"]["warnings"][0]["code"], "SEARCH_FAILED")
        self.assertEqual(failed["research"]["search_results"][0]["result_status"], "search_failed")

        case = case_service()
        case.search_service.search.return_value = {"result_status": "no_results", "documents": []}
        empty = case.analyze_case("case text", case_id="CASE-B")
        self.assertEqual(empty["research"]["status"], "completed")
        self.assertEqual(empty["research"]["search_results"][0]["result_status"], "no_results")

    def test_query_analyzer_preserves_query_and_only_emits_present_keywords(self):
        from app.services.query_analyzer import QueryAnalyzer
        query = "  Casación 123-2024 y artículo 1969 del Código Civil  "
        result = QueryAnalyzer().analyze(query)
        self.assertEqual(result["original_query"], "Casación 123-2024 y artículo 1969 del Código Civil")
        self.assertEqual(result["normalized_query"], result["original_query"])
        self.assertIn("casación", result["keywords"])
        self.assertIn("civil", result["keywords"])
        self.assertNotIn("homicidio", result["keywords"])
        self.assertEqual(result["metadata"]["analysis_method"], "deterministic")

    def test_search_passes_only_supported_repository_filters_and_timings(self):
        row = {"id": "P-2", "texto": "Criterio jurídico sobre responsabilidad civil."}
        service = self.make_service([row])
        service.repository.semantic_search.return_value = [row]
        stages = []
        with patch("app.services.search_service.EmbeddingService") as embeddings:
            embeddings.return_value.generate_embedding.return_value = [0.1]
            result = service.search("consulta civil", filtros={"modulo": "Derecho Civil", "solo_vigentes": False},
                                    generate_answer=False, progress_callback=lambda *args: stages.append(args))
        service.repository.semantic_search.assert_called_once_with(
            embedding=[0.1], modulo="Derecho Civil", solo_vigentes=False, limit=20)
        self.assertEqual(result["result_status"], "completed")
        self.assertIn("retrieval", result["metadata"]["timings_ms"])
        self.assertEqual(result["metadata"]["counts"]["retrieved_count"], 1)
        self.assertIn(("retrieval", "completed"), [(row[0], row[1]) for row in stages])
        self.assertEqual(result["analysis"]["filters"], {"modulo": "Derecho Civil", "solo_vigentes": False})
        done_stages = list(dict.fromkeys(row[0] for row in stages if row[1] in {"completed", "skipped"}))
        self.assertEqual(done_stages, ["query_analysis", "embedding", "retrieval", "fusion",
                                       "reranking", "context", "answer", "citations", "completed"])

    def test_search_task_api_uses_fake_service_and_reports_real_stages(self):
        import time
        from app import create_app
        from app.config import Config

        class FakeSearch:
            def search(self, progress_callback=None, **kwargs):
                progress_callback("query_analysis", "running", {})
                progress_callback("query_analysis", "completed", {"duration_ms": 1})
                return {"query": "civil", "query_normalizada": "civil", "analysis": {},
                    "result_status": "no_results", "answer": "", "documents": [], "sources": [],
                    "citations": [], "warnings": [], "metadata": {"counts": {"retrieved_count": 0},
                                                                       "timings_ms": {"total": 1}}}

        class TestConfig(Config):
            TESTING = True
            RATE_LIMIT_ENABLED = False
            SEARCH_SERVICE_FACTORY = staticmethod(FakeSearch)

        client = create_app(TestConfig).test_client()
        created = client.post("/api/search/tasks", json={"query": "civil law", "filtros": {"modulo": "Derecho Civil"}})
        self.assertEqual(created.status_code, 202)
        task_id = created.json["task_id"]
        status = None
        for _ in range(100):
            status = client.get(f"/api/search/tasks/{task_id}")
            if status.json.get("status") in {"completed", "failed"}:
                break
            time.sleep(0.01)
        self.assertEqual(status.json["status"], "completed")
        self.assertEqual(status.json["final_result"]["result_status"], "no_results")
        self.assertEqual(status.json["timings_ms"]["total"], 1)
        self.assertTrue(any(stage["status"] == "completed" for stage in status.json["stages"]))

    def test_search_task_rejects_nonfunctional_filter(self):
        from app import create_app
        from app.config import Config
        class TestConfig(Config):
            TESTING = True
            RATE_LIMIT_ENABLED = False
        response = create_app(TestConfig).test_client().post("/api/search/tasks", json={
            "query": "consulta jurídica", "filtros": {"tipoDocumento": "Jurisprudencia"}})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json["error"]["code"], "UNSUPPORTED_FILTER")

    def test_embedding_failure_is_not_reported_as_no_results(self):
        from app.services.search_service import SearchPipelineError
        service = self.make_service([])
        with patch("app.services.search_service.EmbeddingService") as embeddings:
            embeddings.return_value.generate_embedding.side_effect = RuntimeError("provider detail")
            with self.assertRaises(SearchPipelineError) as error:
                service.search("consulta jurídica", use_reranker=False)
        self.assertEqual(error.exception.code, "EMBEDDING_FAILED")
        service.repository.semantic_search.assert_not_called()

    def test_cancellation_during_search_stops_before_retrieval(self):
        from app.utils.cancellation import CancellationToken, OperationCancelled
        service = self.make_service([])
        token = CancellationToken()
        def cancel_after_embedding(*args, **kwargs):
            token.cancel()
            return [0.1]
        with patch("app.services.search_service.EmbeddingService") as embeddings:
            embeddings.return_value.generate_embedding.side_effect = cancel_after_embedding
            with self.assertRaises(OperationCancelled):
                service.search("consulta jurídica", use_reranker=False, cancellation_token=token)
        service.repository.semantic_search.assert_not_called()

    def test_reranker_failure_keeps_retrieval_and_exposes_controlled_warning(self):
        row = {"id": "P-3", "texto": "Criterio recuperado con procedencia jurídica."}
        service = self.make_service([row])
        class DegradedReranker:
            last_failed = False
            def rerank(self, query, documents, cancellation_token=None):
                self.last_failed = True
                return documents
        service.reranker = DegradedReranker()
        with patch("app.services.search_service.EmbeddingService") as embeddings:
            embeddings.return_value.generate_embedding.return_value = [0.1]
            result = service.search("consulta", generate_answer=False)
        self.assertEqual(result["result_status"], "completed")
        self.assertEqual(result["documents"][0]["id"], "P-3")
        self.assertEqual(result["warnings"][0]["code"], "RERANKING_DEGRADED")

    def test_cancelled_reranker_does_not_start_provider_request(self):
        from app.services.reranker_service import RerankerService
        from app.utils.cancellation import CancellationToken, OperationCancelled
        token = CancellationToken()
        token.cancel()
        reranker = RerankerService.__new__(RerankerService)
        reranker.client = Mock()
        reranker.enabled = True
        with self.assertRaises(OperationCancelled):
            reranker.rerank("query", [{"id": "P-1"}], cancellation_token=token)
        reranker.client.chat.completions.create.assert_not_called()


if __name__ == "__main__":
    unittest.main()
