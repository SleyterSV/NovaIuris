"""Offline golden structure checks for the Legal Knowledge V2 foundation."""
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from app.legal_ingestion.cleaners import remove_repeated_page_furniture
from app.legal_ingestion.extractors import extract, is_html_document
from app.legal_ingestion.identity import content_hash, document_hash, normalize_text
from app.legal_ingestion.models import Block, ExtractedDocument
from app.legal_ingestion.parsers import NormativeParser, JurisprudenceParser, case_law_metadata
from app.legal_ingestion.quality import validate_staged
from app.legal_ingestion.service import dry_run, stage_file
from app.legal_ingestion.units import OversizedUnitError, embedding_batches, split_oversized_unit


class LegalKnowledgeV2Tests(unittest.TestCase):
    def test_document_hash_is_whole_normalized_document(self):
        a = [Block("Artículo 1.  Primera regla"), Block("Artículo 2. Segunda regla")]
        b = [Block("Artículo 1. Primera regla"), Block("Artículo 2. Segunda regla")]
        self.assertEqual(document_hash(a), document_hash(b))
        self.assertNotEqual(document_hash(a), document_hash(b[:1]))

    def test_content_hash_keeps_structural_identity(self):
        self.assertNotEqual(content_hash("article", "1", None, "Mismo texto"),
                            content_hash("article", "2", None, "Mismo texto"))
        self.assertNotEqual(content_hash("article", "1", None, "Mismo texto"),
                            content_hash("foundation", "1", None, "Mismo texto"))
        self.assertNotEqual(content_hash("article", "1", None, "Mismo texto", hierarchy={"book": "I"}),
                            content_hash("article", "1", None, "Mismo texto", hierarchy={"book": "II"}))

    def test_normalization_preserves_lines_and_unicode(self):
        self.assertEqual(normalize_text("Arti\u0301culo\t 1\r\n  Texto"), "Artículo 1\nTexto")

    def test_normative_article_not_cut_and_amendment_separate(self):
        blocks = [Block("LIBRO I"), Block("TÍTULO II"), Block("Artículo 1351.- Contrato"),
                  Block("Primer párrafo."), Block("Segundo párrafo."),
                  Block("Modificado por Ley 100."), Block("Artículo 1352.- Consentimiento"),
                  Block("Regla completa.")]
        units = NormativeParser().parse(blocks)
        articles = [unit for unit in units if unit.unit_type == "article"]
        self.assertEqual([unit.unit_number for unit in articles], ["1351", "1352"])
        self.assertIn("Segundo párrafo", articles[0].text)
        self.assertNotIn("Modificado por", articles[0].text)
        self.assertEqual(articles[0].book, "I")
        self.assertEqual(articles[0].title, "II")
        self.assertEqual([unit.unit_type for unit in units].count("amendment_note"), 1)

    def test_plural_disposition_heading_is_not_a_legal_unit(self):
        blocks = [Block("DISPOSICIONES GENERALES"), Block("Artículo 1.- Regla"),
                  Block("DISPOSICIÓN PRIMERA.- Vigencia especial")]
        units = NormativeParser().parse(blocks)
        self.assertEqual([u.unit_type for u in units], ["article", "disposition"])
        self.assertNotIn("DISPOSICIONES GENERALES", units[0].text)

    def test_embedded_article_headings_are_separate_and_prose_is_not_a_number(self):
        blocks = [Block("Artículo 659-A.- Apoyos\nRegla primera.\nArtículo 659-B.- Salvaguardias\nRegla segunda."),
                  Block("Artículo afectado por la modificación")]
        units = NormativeParser().parse(blocks)
        self.assertEqual([u.unit_number for u in units], ["659-A", "659-B"])
        self.assertNotIn("Artículo 659-B", units[0].text)
        self.assertIn("Artículo afectado", units[1].text)

    def test_foundations_and_decision_keep_pages(self):
        blocks = [Block("SUMILLA: Reposición", page=1), Block("ANTECEDENTES", page=1),
                  Block("Se interpuso la demanda.", page=1), Block("FUNDAMENTOS", page=2),
                  Block("1. Primer razonamiento.", page=2), Block("1. Continúa.", page=3),
                  Block("2. Segundo razonamiento.", page=3), Block("DECISIÓN", page=4),
                  Block("Declarar fundada la demanda.", page=4)]
        units = JurisprudenceParser().parse(blocks)
        self.assertEqual([unit.unit_type for unit in units],
                         ["sumilla", "antecedent", "foundation", "foundation", "decision"])
        self.assertEqual((units[2].page_start, units[2].page_end), (2, 3))
        self.assertIn("Declarar fundada", units[-1].text)

    def test_cassation_roman_sections_and_ordinal_foundations(self):
        blocks = [Block("SUMILLA:"), Block("Regla laboral."),
                  Block("I. MATERIA DEL RECURSO DE CASACIÓN"), Block("Recurso presentado."),
                  Block("III. CONSIDERANDO:"), Block("PRIMERO.- Razón inicial."),
                  Block("SEGUNDO.- Razón siguiente."), Block("IV. DECISIÓN"),
                  Block("Declararon infundado el recurso.")]
        units = JurisprudenceParser().parse(blocks)
        self.assertEqual([u.unit_type for u in units],
                         ["sumilla", "antecedent", "foundation", "foundation", "decision"])
        self.assertEqual([u.unit_number for u in units if u.unit_type == "foundation"],
                         ["PRIMERO", "SEGUNDO"])

    def test_tc_auto_sections_and_case_number_survive_header_cleaning(self):
        blocks = []
        for page in (1, 2, 3):
            blocks.append(Block("EXP. N.° 04810-2024-PA/TC", page=page))
            blocks.append(Block("AUTO DEL TRIBUNAL CONSTITUCIONAL", page=page))
            blocks.append(Block("VISTO" if page == 1 else "ATENDIENDO A QUE" if page == 2 else "HA RESUELTO", page=page))
            blocks.append(Block("El pedido." if page == 1 else "1. Razón." if page == 2 else "Declarar improcedente.", page=page))
        extracted = ExtractedDocument("auto_tc.pdf", "pdf", blocks, "a" * 64)
        with patch("app.legal_ingestion.service.extract", return_value=extracted):
            staged = stage_file("auto_tc.pdf")
        self.assertEqual(staged.metadata["expediente"], "04810-2024-PA/TC")
        self.assertEqual(staged.metadata["resolution_type"], "auto")
        self.assertIn("decision", [u.unit_type for u in staged.units])

    def test_tc_decision_and_header_date_are_not_lost_to_case_history(self):
        blocks = [Block("Sala Segunda. Sentencia 0864/2026"),
                  Block("SENTENCIA DEL TRIBUNAL CONSTITUCIONAL"),
                  Block("En Lima, a los 22 días del mes de junio de 2026"),
                  Block("ANTECEDENTES"), Block("Demanda presentada el 25 de julio de 2023."),
                  Block("FUNDAMENTOS"), Block("1. Razonamiento."),
                  Block("HA RESUELTO"), Block("Declarar fundada la demanda.")]
        metadata = case_law_metadata(blocks, "sentencia_tc.pdf")
        self.assertEqual(metadata["resolution_date"], "2026-06-22")
        self.assertEqual(metadata["resolution_type"], "sentencia")
        self.assertEqual(JurisprudenceParser().parse(blocks)[-1].unit_type, "decision")

    def test_court_detected_with_pdf_spacing(self):
        metadata = case_law_metadata([Block("CORTE  SUPREMA  DE JUSTICIA DE LA REPÚBLICA"),
                                      Block("CASACIÓN N° 34397-2023")], "precedente.pdf")
        self.assertEqual(metadata["court"], "Corte Suprema")

    def test_pdf_sumilla_collects_wrapped_lines_on_same_page(self):
        blocks = [Block("SUMILLA :", page=1), Block("Será válido el contrato", page=1),
                  Block("que cumpla los requisitos.", page=1), Block("III. CONSIDERANDO:", page=2)]
        metadata = case_law_metadata(blocks, "casación.pdf")
        self.assertEqual(metadata["sumilla"], "Será válido el contrato que cumpla los requisitos.")

    def test_unpunctuated_date_is_not_a_foundation(self):
        blocks = [Block("ATENDIENDO A QUE"), Block("1. Fundamento."),
                  Block("29 de mayo de 2025 fue la resolución."), Block("HA RESUELTO"),
                  Block("Declarar improcedente.")]
        units = JurisprudenceParser().parse(blocks)
        self.assertEqual([u.unit_number for u in units if u.unit_type == "foundation"], ["1"])
        self.assertIn("29 de mayo", units[0].text)

    def test_case_without_resolution_date_requires_review(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "casación.txt"
            path.write_text("CORTE SUPREMA DE JUSTICIA\nCASACIÓN N.° 20221-2023\nIII. CONSIDERANDO:\nPRIMERO.- Razón.\nIV. DECISIÓN\nDeclararon infundado.", encoding="utf-8")
            staged = stage_file(path, family="jurisprudence")
        self.assertEqual(staged.ingestion_status, "review_required")
        self.assertIn("jurisprudence_date_or_type_missing", staged.warnings)

    def test_split_pdf_across_pages_requires_provenance_review(self):
        blocks = [Block("SENTENCIA DEL TRIBUNAL CONSTITUCIONAL", page=1),
                  Block("EXP. N.° 1234-2024-PA/TC", page=1),
                  Block("Lima, 2 de enero de 2025", page=1), Block("FUNDAMENTOS", page=1),
                  Block("1. Primero principio completo.", page=1),
                  Block("Otro párrafo jurídico completo.", page=2),
                  Block("HA RESUELTO", page=2), Block("Declarar fundada.", page=2)]
        extracted = ExtractedDocument("sentencia.pdf", "pdf", blocks, "a" * 64)
        with patch("app.legal_ingestion.service.extract", return_value=extracted):
            staged = stage_file("sentencia.pdf", max_unit_tokens=4)
        self.assertIn("split_page_provenance_review_required", staged.warnings)

    def test_implausible_foundation_number_requires_review(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "auto_tc.txt"
            path.write_text("TRIBUNAL CONSTITUCIONAL\nEXP. N.° 04810-2024-PA/TC\nLima, 23 de octubre de 2025\nATENDIENDO A QUE\n1. Primera razón.\n211. Texto cuya numeración requiere cotejo.\nRESUELVE\nDeclarar improcedente.", encoding="utf-8")
            staged = stage_file(path, family="jurisprudence")
        self.assertEqual(staged.ingestion_status, "review_required")
        self.assertIn("foundation_numbering_review_required", staged.warnings)

    def test_very_long_split_requires_review(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "ley.txt"
            path.write_text("Artículo 1.- Regla.\n" + "\n".join("Texto legal completo." for _ in range(10)), encoding="utf-8")
            staged = stage_file(path, family="normative", max_unit_tokens=3)
        self.assertEqual(staged.ingestion_status, "review_required")
        self.assertIn("oversized_structure_review_required", staged.warnings)

    def test_oversized_unit_splits_at_paragraphs(self):
        unit = NormativeParser().parse([Block("Artículo 1.- Inicio"),
            Block("Primera oración de la norma."), Block("Segunda oración de la norma.")])[0]
        parts = split_oversized_unit(unit, max_tokens=6)
        self.assertGreater(len(parts), 1)
        self.assertEqual([part.part_number for part in parts], list(range(1, len(parts) + 1)))
        self.assertTrue(all(part.part_count == len(parts) for part in parts))
        self.assertEqual(parts[0].metadata["parent_content_hash"], unit.content_hash)

    def test_oversized_sentence_requires_review_instead_of_cut(self):
        unit = NormativeParser().parse([Block("Artículo 1.- " + "palabra " * 30)])[0]
        with self.assertRaises(OversizedUnitError):
            split_oversized_unit(unit, max_tokens=5)
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "ley.txt"
            path.write_text("Artículo 1.- " + "palabra " * 30, encoding="utf-8")
            staged = stage_file(path, family="normative", max_unit_tokens=5)
        self.assertEqual(staged.ingestion_status, "review_required")
        self.assertEqual(len(staged.units), 1)
        self.assertEqual(staged.units[0].text.count("palabra"), 30)

    def test_repeated_page_header_and_footer_removed_conservatively(self):
        blocks = []
        for page in (1, 2, 3):
            blocks.extend([Block("Diario Oficial", page=page),
                           Block(f"Artículo {page}.- Texto diferente", page=page),
                           Block("https://validacion.example", page=page)])
        kept, removed = remove_repeated_page_furniture(blocks)
        self.assertEqual(removed, 6)
        self.assertEqual(len(kept), 3)
        only_legal_headings = [Block("SUMILLA", page=page) for page in (1, 2, 3)]
        kept, removed = remove_repeated_page_furniture(only_legal_headings)
        self.assertEqual((len(kept), removed), (3, 0))

    def test_spij_html_detected_and_cleaned_with_links(self):
        html = b'<!doctype html><html><head><style>.x{}</style></head><body><h2>Art\xc3\xadculo 1.-</h2><p>Regla <a href="https://example.org/norma">oficial</a>.</p><script>secret()</script></body></html>'
        self.assertTrue(is_html_document(html))
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "tributario.doc"
            path.write_bytes(html)
            extracted = extract(path)
        self.assertEqual(extracted.source_format, "spij_html")
        self.assertIn("https://example.org/norma", extracted.blocks[-1].links)
        self.assertNotIn("secret", str(extracted.blocks))

    def test_docx_preserves_heading_and_table_order(self):
        from docx import Document
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "ley.docx"
            doc = Document()
            doc.add_paragraph("CAPÍTULO I", style="Heading 1")
            table = doc.add_table(rows=1, cols=2)
            table.cell(0, 0).text, table.cell(0, 1).text = "A", "B"
            doc.add_paragraph("Artículo 1.- Regla")
            doc.save(path)
            extracted = extract(path)
        self.assertEqual([block.kind for block in extracted.blocks], ["heading", "table", "paragraph"])
        self.assertEqual(extracted.blocks[1].text, "A | B")

    def test_pdf_preserves_page_numbers(self):
        pages = [SimpleNamespace(extract_text=lambda: "Artículo 1.- Uno"),
                 SimpleNamespace(extract_text=lambda: "Artículo 2.- Dos")]
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "norma.pdf"
            path.write_bytes(b"%PDF-fake")
            with patch("pypdf.PdfReader", return_value=SimpleNamespace(pages=pages)):
                extracted = extract(path)
        self.assertEqual([block.page for block in extracted.blocks], [1, 2])

    def test_jurisprudence_metadata_and_sumilla(self):
        blocks = [Block("TRIBUNAL CONSTITUCIONAL"), Block("EXP. 1234-2024-PA/TC"),
                  Block("SUMILLA: Tutela judicial"),
                  Block("Se establece precedente vinculante")]
        metadata = case_law_metadata(blocks, "sentencia.pdf")
        self.assertEqual(metadata["court"], "Tribunal Constitucional")
        self.assertEqual(metadata["expediente"], "1234-2024-PA/TC")
        self.assertTrue(metadata["sumilla"].startswith("Tutela judicial"))
        self.assertIs(metadata["precedent_binding"], True)

    def test_bad_extraction_and_no_units_require_review(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "sentencia.txt"
            path.write_text("\ufffd" * 20, encoding="utf-8")
            staged = stage_file(path, family="jurisprudence")
        self.assertEqual(staged.ingestion_status, "review_required")
        self.assertIn("no_legal_units", validate_staged(staged))

    def test_idempotent_dry_run_skips_repeated_document(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "ley.txt"
            path.write_text("Artículo 1.- Una regla completa.", encoding="utf-8")
            reports = dry_run([path, path], family="normative")
        self.assertFalse(reports[0]["duplicate_skipped"])
        self.assertTrue(reports[1]["duplicate_skipped"])
        self.assertEqual(reports[0]["document_hash"], reports[1]["document_hash"])

    def test_duplicate_units_are_preserved_and_require_review(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "ley.txt"
            path.write_text("Artículo 1.- Regla.\nArtículo 1.- Regla.", encoding="utf-8")
            staged = stage_file(path, family="normative")
        self.assertEqual(len(staged.units), 2)
        self.assertEqual(staged.ingestion_status, "review_required")
        self.assertIn("duplicate_unit_hash", staged.warnings)

    def test_case_law_filename_with_ley_remains_jurisprudence(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "Sentencia_TC_sobre_Ley_32107.txt"
            path.write_text("TRIBUNAL CONSTITUCIONAL\nSUMILLA: Caso\nDECISIÓN\nDeclarar infundada.", encoding="utf-8")
            report = dry_run([path])[0]
        self.assertEqual(report["detected"], "jurisprudence")
        self.assertEqual(report["status"], "review_required")
        self.assertIn("jurisprudence_identity_missing", report["warnings"])

    def test_batch_embeddings_assert_dimension(self):
        units = [SimpleNamespace(search_text=str(i)) for i in range(3)]
        calls = []
        def fake(batch):
            calls.append(len(batch))
            return [[0.0] * 1536 for _ in batch]
        self.assertEqual(len(embedding_batches(units, fake, batch_size=2)), 3)
        self.assertEqual(calls, [2, 1])
        with self.assertRaisesRegex(ValueError, "1536"):
            embedding_batches(units[:1], lambda _: [[0.0] * 10])

    def test_sql_foundation_is_staged_and_secured(self):
        migration = next((Path(__file__).parents[2] / "supabase" / "migrations").glob("*_legal_knowledge_v2_foundation.sql"))
        sql = migration.read_text(encoding="utf-8").lower()
        for name in ("legal_documents", "legal_units", "legal_relations", "legal_ingestion_runs"):
            self.assertIn(f"create table public.{name}", sql)
            self.assertIn(f"alter table public.{name} enable row level security", sql)
        self.assertIn("vector(1536)", sql)
        self.assertIn("using hnsw", sql)
        self.assertIn("using gin", sql)
        self.assertIn("match_legal_knowledge_v2", sql)
        self.assertNotIn("drop table", sql)


if __name__ == "__main__": unittest.main()
