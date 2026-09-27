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
        service.reranker = Mock()
        service.reranker.rerank.side_effect = lambda query, documents: documents
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
            "similarity": 0.91}])
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


if __name__ == "__main__":
    unittest.main()
