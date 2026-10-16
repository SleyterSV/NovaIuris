"""NovaCase research states and V2 retrieval through the canonical source boundary."""
import unittest
from unittest.mock import Mock, patch

from app.services.case_execution import research_queries
from app.services.query_analyzer import QueryAnalyzer
from app.services.search_service import SearchPipelineError, SearchService
from tests.test_stabilization import case_service


class NovaCaseResearchQualityTests(unittest.TestCase):
    def test_empty_model_queries_use_case_analysis_without_case_specific_rules(self):
        analysis = {"pretension_principal": "Reposición por cese de contrato CAS",
                    "problemas_juridicos": ["Protección del trabajador contratado bajo CAS"]}
        self.assertEqual(research_queries([], 4, fallback=analysis), [
            "Reposición por cese de contrato CAS Protección del trabajador contratado bajo CAS"])
        self.assertEqual(research_queries(["consulta propia"], 4, fallback=analysis), ["consulta propia"])
        self.assertEqual(research_queries([], 4, fallback={}), [])

    def test_cas_research_uses_v2_ranked_ids_then_complete_canonical_unit(self):
        service = case_service()
        service.strategy_builder.build_strategy.return_value = {
            "search_queries": [], "claim_strategy": "Examinar reposición CAS"}
        service.case_analyzer.analyze_case.return_value = {
            "hechos": ["Se alegó un cese CAS"],
            "pretension_principal": "Reposición por cese de contrato CAS",
            "problemas_juridicos": ["Tutela del trabajador contratado bajo CAS"]}
        search = SearchService.__new__(SearchService)
        search.knowledge_version = "v2"
        search.query_analyzer = QueryAnalyzer()
        search.repository = Mock()
        search.citation_service = Mock()
        search.citation_service.extract_citations.return_value = []
        unit_id = "11111111-1111-4111-8111-111111111111"
        document_id = "22222222-2222-4222-8222-222222222222"
        search.repository.search.return_value = [{
            "id": unit_id, "unit_id": unit_id, "document_id": document_id,
            "tipo_documento": "judgment", "unit_type": "foundation", "unit_number": "7",
            "titulo": "STC Exp. 00001-2024-PA/TC", "fuente": "Sentencia",
            "texto": "Vista previa breve", "expediente": "00001-2024-PA/TC",
            "page_start": 2, "page_end": 2, "similarity": 0.8}]
        canonical = "Texto canónico completo sobre la controversia CAS y su conclusión."
        search.repository.get_unit.return_value = {
            "unit_id": unit_id, "document_id": document_id, "text": canonical,
            "document_type": "judgment", "unit_type": "foundation", "unit_number": "7",
            "display_title": "STC Exp. 00001-2024-PA/TC", "document_title": "Sentencia",
            "expediente": "00001-2024-PA/TC", "court": "Tribunal Constitucional",
            "page_start": 2, "page_end": 2, "official_url": "https://tc.gob.pe/documento.pdf"}
        service.search_service = search
        with patch("app.services.search_service.EmbeddingService") as embedding:
            embedding.return_value.MODEL = "text-embedding-3-small"
            embedding.return_value.generate_embedding.return_value = [0.0] * 1536
            result = service.analyze_case("Caso CAS sintético", case_id="CASE-CAS")
        self.assertEqual(result["research"]["status"], "VERIFIED_SOURCES")
        self.assertEqual(result["research"]["public_source_count"], 1)
        self.assertEqual(result["legal_authority_status"], "VERIFIED")
        self.assertEqual(result["evidence_availability"], "NO_DOCUMENTS")
        self.assertEqual(result["summary"]["documentos"], 0)
        self.assertEqual(result["summary"]["fuentes_juridicas"], 1)
        source = result["research"]["sources"][0]
        self.assertEqual((source["document_id"], source["unit_id"]), (document_id, unit_id))
        self.assertEqual(source["excerpt"], canonical)
        self.assertEqual(source["preview"], "Vista previa breve")
        self.assertEqual(service.argument_service.generate_arguments.call_args.kwargs["documents"][0]["texto"], canonical)
        search.repository.search.assert_called_once()
        self.assertIsNone(search.repository.search.call_args.kwargs["filter_rama"])
        search.repository.get_unit.assert_called_once_with(unit_id, document_id=document_id)

    def test_zero_results_differs_from_error_and_facts_remain_alleged(self):
        service = case_service()
        service.search_service.search.return_value = {"documents": [], "result_status": "no_results"}
        empty = service.analyze_case("Caso sin documentos", case_id="CASE-A")
        self.assertEqual(empty["research"]["status"], "NO_RESULTS")
        self.assertEqual(empty["legal_authority_status"], "PRELIMINARY")
        self.assertEqual(empty["evidence_availability"], "NO_DOCUMENTS")
        self.assertEqual(empty["summary"]["documentos"], 0)
        self.assertEqual(empty["summary"]["fuentes_juridicas"], 0)
        self.assertTrue(all(fact["status"] == "alleged" for fact in empty["facts"]))
        self.assertEqual(empty["citations"], [])
        service = case_service()
        service.search_service.search.side_effect = SearchPipelineError("EMBEDDING_FAILED")
        failed = service.analyze_case("Caso sin servicio", case_id="CASE-B")
        self.assertEqual(failed["research"]["status"], "ERROR")
        self.assertEqual(failed["research"]["public_source_count"], 0)
        self.assertEqual(failed["legal_authority_status"], "PRELIMINARY")
        self.assertEqual(service.search_service.search.call_count, 1)


if __name__ == "__main__":
    unittest.main()
