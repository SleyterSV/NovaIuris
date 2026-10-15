"""NovaCase public V2 source resolution and case-local provenance."""
import unittest
from unittest.mock import Mock, patch

from app.services.case_execution import resolve_public_v2_hits
from app.services.case_professional import select_report_sources
from app.services.case_service import CaseService
from app.services.source_contracts import (normalize_case_source,
    normalize_public_legal_v2_source, resolve_citations)
from app.utils.novacourt_graph import build_graph_input
from app.utils.cancellation import CancellationToken, OperationCancelled
from tests.test_stabilization import case_service


UNIT = "11111111-1111-4111-8111-111111111111"
DOCUMENT = "22222222-2222-4222-8222-222222222222"
OTHER_DOCUMENT = "33333333-3333-4333-8333-333333333333"


def hit(document_id=DOCUMENT, unit_id=UNIT):
    return {"id": unit_id, "unit_id": unit_id, "document_id": document_id,
            "unit_type": "foundation", "unit_number": "7", "tipo_documento": "judgment",
            "expediente": "00001-2024-PA/TC", "extracto_exacto": "La conclusi…"}


def detail(document_id=DOCUMENT, unit_id=UNIT, text="La conclusión jurídica íntegra."):
    return {"unit_id": unit_id, "document_id": document_id, "text": text,
            "unit_type": "foundation", "unit_number": "7", "document_type": "judgment",
            "expediente": "00001-2024-PA/TC", "court": "Tribunal Constitucional",
            "document_title": "Sentencia", "display_title": "STC Exp. 00001-2024-PA/TC",
            "page_start": 2, "page_end": 3,
            "official_url": "https://tc.gob.pe/documento.pdf"}


class NovaCaseV2Tests(unittest.TestCase):
    def test_case_constructor_selects_v2_even_when_search_default_is_v1(self):
        with patch("app.services.case_service.SearchService") as search:
            CaseService()
        search.assert_called_once_with(knowledge_version="v2")

    def test_canonical_context_reaches_all_downstream_modules_and_report(self):
        service = case_service()
        service.search_service.search.return_value = {"documents": [hit()]}
        service.search_service.repository.get_unit.return_value = detail()
        result = service.analyze_case("Relato", case_id="CASE-A")
        source = next(s for s in result["research"]["sources"] if s["source_scope"] == "public_legal")
        self.assertEqual(result["sources"][0]["legal_source_scope"], "public_legal")
        graph = build_graph_input(result)
        self.assertTrue(any(node.get("source_ids") == [source["source_id"]]
                            for node in graph["entities"]))
        self.assertEqual((source["document_id"], source["unit_id"]), (DOCUMENT, UNIT))
        self.assertEqual(source["excerpt"], detail()["text"])
        self.assertEqual(source["preview"], hit()["extracto_exacto"])
        for module, method in (("argument_service", "generate_arguments"),
                               ("evidence_analyzer", "analyze"),
                               ("risk_analyzer", "analyze"),
                               ("counter_argument_service", "generate_counterarguments")):
            with self.subTest(module=module):
                documents = getattr(getattr(service, module), method).call_args.kwargs["documents"]
                self.assertEqual(documents[0]["texto"], detail()["text"])
                self.assertEqual(documents[0]["unit_id"], UNIT)
                self.assertEqual(documents[0]["source_scope"], "public_legal")
        report_sources = service.report_service.generate_report.call_args.kwargs["sources"]
        self.assertEqual(report_sources[0]["excerpt"], detail()["text"])
        service.search_service.repository.get_unit.assert_called_once_with(UNIT, document_id=DOCUMENT)

    def test_mismatch_or_missing_unit_fails_closed_without_v1_fallback(self):
        for resolved in (None, detail(document_id=OTHER_DOCUMENT)):
            with self.subTest(resolved=resolved):
                service = case_service()
                service.search_service.search.return_value = {"documents": [hit()]}
                service.search_service.repository.get_unit.return_value = resolved
                result = service.analyze_case("Relato", case_id="CASE-A")
                self.assertEqual(result["research"]["status"], "search_failed")
                self.assertFalse([s for s in result["research"]["sources"] if s["source_scope"] == "public_legal"])
                self.assertEqual(service.argument_service.generate_arguments.call_args.kwargs["documents"], [])
                self.assertEqual(service.search_service.search.call_count, 1)
        service = case_service()
        service.search_service.knowledge_version = "v1"
        with self.assertRaisesRegex(ValueError, "NOVACASE_REQUIRES_LEGAL_KNOWLEDGE_V2"):
            service.analyze_case("Relato", case_id="CASE-A")

    def test_malformed_v2_result_and_cancellation_never_enter_llm_context(self):
        for documents in ([{"id": UNIT, "extracto_exacto": "Preview"}], [None], "invalid"):
            with self.subTest(documents=documents):
                service = case_service()
                service.search_service.search.return_value = {"documents": documents}
                result = service.analyze_case("Relato", case_id="CASE-A")
                self.assertEqual(result["research"]["status"], "search_failed")
                self.assertEqual(service.argument_service.generate_arguments.call_args.kwargs["documents"], [])
        token = CancellationToken()
        token.cancel()
        with self.assertRaises(OperationCancelled):
            resolve_public_v2_hits(Mock(), [hit()], cancellation_token=token)

    def test_duplicate_unit_resolves_once_and_budget_omits_whole_oversized_unit(self):
        repo = Mock()
        repo.get_unit.return_value = detail(text="Texto jurídico completo.")
        selected, sources, warnings = resolve_public_v2_hits(repo, [hit(), hit()])
        self.assertEqual(len(selected), 1)
        self.assertEqual(len(sources), 1)
        self.assertEqual(warnings, [])
        repo.get_unit.assert_called_once_with(UNIT, document_id=DOCUMENT)
        selected, sources, warnings = resolve_public_v2_hits(repo, [hit()], max_unit_chars=8)
        self.assertEqual((selected, sources), ([], []))
        self.assertEqual(warnings[0]["code"], "PUBLIC_UNIT_CONTEXT_BUDGET_EXCEEDED")
        self.assertEqual(select_report_sources([normalize_public_legal_v2_source(hit(), detail(text="X" * 2100))],
                                               [], "CASE-A")[0]["excerpt"], "X" * 2100)

    def test_citations_require_delivered_v2_identity_and_private_case(self):
        source = normalize_public_legal_v2_source(hit(), detail())
        marker = f'[{source["source_id"]}]'
        valid = resolve_citations(marker, [source], "CASE-A")
        self.assertEqual(valid["citations"][0]["unit_id"], UNIT)
        self.assertEqual(valid["citations"][0]["document_id"], DOCUMENT)
        self.assertEqual(resolve_citations(marker, [], "CASE-A")["citations"], [])
        forged = {**source, "document_id": OTHER_DOCUMENT}
        self.assertEqual(resolve_citations(marker, [forged], "CASE-A")["citations"], [])
        private = normalize_case_source({"case_id": "CASE-B", "document_id": "DOC-B",
                                         "chunk_id": "CH-B", "text": "Otro caso"})
        self.assertEqual(private["source_scope"], "private_case")
        self.assertEqual(resolve_citations(f'[{private["source_id"]}]', [private], "CASE-A")["citations"], [])


if __name__ == "__main__":
    unittest.main()
