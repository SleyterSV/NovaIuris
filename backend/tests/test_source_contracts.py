import unittest

from app.services.source_contracts import (
    normalize_case_source, normalize_citation, normalize_public_source,
    resolve_citations,
)


class SourceContractTests(unittest.TestCase):
    def test_public_source_preserves_real_metadata_and_stable_identity(self):
        record = {"id": "LEGAL-7", "tipo_documento": "legislation", "fuente": "Código Civil",
                  "articulo": "Artículo 1969", "texto": "Fragmento exacto", "entidad": "Congreso",
                  "official_url": "https://www.example.test/law/7", "metadata": {"vigencia": "vigente"}}
        first = normalize_public_source(record, "Fragmento exacto")
        second = normalize_public_source(record, "Fragmento exacto")
        self.assertEqual(first["source_scope"], "public")
        self.assertEqual(first["source_type"], "legislation")
        self.assertEqual(first["source_id"], second["source_id"])
        self.assertEqual(first["article"], "Artículo 1969")
        self.assertEqual(first["excerpt"], "Fragmento exacto")
        self.assertEqual(first["official_url"], record["official_url"])
        self.assertEqual(first["metadata"]["vigencia"], "vigente")

    def test_jurisprudence_and_absent_url_are_not_inferred(self):
        source = normalize_public_source({"id": "J-9", "tipo_documento": "jurisprudence",
            "tribunal": "Corte Suprema", "expediente": "123-2020", "fundamento": "Fundamento 8",
            "texto": "Considerando relevante", "metadata": {"url": "https://not-verified.test"}})
        self.assertEqual(source["source_type"], "jurisprudence")
        self.assertEqual(source["court"], "Corte Suprema")
        self.assertEqual(source["case_number"], "123-2020")
        self.assertEqual(source["legal_basis"], "Fundamento 8")
        self.assertIsNone(source["official_url"])

    def test_private_source_identity_requires_case_and_document_chunk(self):
        item = {"case_id": "CASE-A", "document_id": "DOC-A", "chunk_id": "CHUNK-A",
                "text": "Exact private passage", "source_reference": {"page_start": 7, "section": "Prueba"}}
        source = normalize_case_source(item)
        self.assertEqual(source["source_scope"], "case")
        self.assertEqual((source["case_id"], source["document_id"], source["chunk_id"]),
                         ("CASE-A", "DOC-A", "CHUNK-A"))
        self.assertEqual(source["page_start"], 7)
        self.assertEqual(source["section"], "Prueba")
        self.assertEqual(source["excerpt"], item["text"])
        with self.assertRaises(ValueError):
            normalize_case_source({"document_id": "DOC-A", "chunk_id": "CHUNK-A"})

    def test_resolver_validates_markers_deduplicates_sources_and_preserves_excerpt(self):
        source = normalize_public_source({"id": "LEGAL-1", "articulo": "Artículo 1",
                                          "texto": "Exact excerpt used by answer"})
        marker = f"[{source['source_id']}]"
        result = resolve_citations(f"Primera afirmación {marker}; reiteración {marker}.", [source])
        self.assertEqual(result["answer"], "Primera afirmación [1]; reiteración [1].")
        self.assertEqual(len(result["citations"]), 1)
        self.assertEqual(len(result["sources_used"]), 1)
        self.assertEqual(result["citations"][0]["excerpt"], "Exact excerpt used by answer")
        self.assertEqual(result["citations"][0]["source_id"], source["source_id"])
        self.assertTrue(result["citations"][0]["citation_id"].startswith("CIT-"))

    def test_invalid_markers_are_removed_and_private_sources_are_case_scoped(self):
        private = normalize_case_source({"case_id": "CASE-A", "document_id": "DOC-A", "chunk_id": "CH-A",
                                         "text": "Private excerpt"})
        invalid = resolve_citations(f"No valid citation [SRC-FAKE12345]; {private['source_id']}.",
                                    [private], case_id="CASE-B")
        self.assertEqual(invalid["citations"], [])
        self.assertEqual(invalid["sources_used"], [])
        self.assertNotIn("Private excerpt", str(invalid))
        self.assertEqual(invalid["warnings"][0]["code"], "INVALID_SOURCE_MARKER")

    def test_citation_locator_inherits_verified_source_location(self):
        source = normalize_public_source({"id": 2, "texto": "exact", "articulo": "Art. 4",
                                          "page_start": 12, "section": "Fundamentos"})
        citation = normalize_citation({"label": "[1]"}, source)
        self.assertEqual(citation["locator"], {"page": 12, "section": "Fundamentos", "article": "Art. 4"})

    def test_case_contract_preserves_public_and_private_sources_for_court(self):
        from app.utils.case_contract import normalize_case_result
        private = normalize_case_source({"case_id": "CASE-A", "document_id": "DOC-A", "chunk_id": "CH-A",
                                         "text": "private evidence"})
        citation = {"citation_id": "CIT-123456789012345678901234", "source_id": private["source_id"], "label": "[1]"}
        result = normalize_case_result({"success": True, "case_id": "CASE-A", "sources": [private],
                                        "citations": [citation], "graph": {"status": "ready"}})
        self.assertEqual(result["sources"][0]["case_id"], "CASE-A")
        self.assertEqual(result["citations"][0]["source_id"], private["source_id"])
        self.assertEqual(result["graph"]["status"], "ready")


if __name__ == "__main__":
    unittest.main()
