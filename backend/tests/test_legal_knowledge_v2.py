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
    def test_septimo_is_its_own_foundation_and_legacy_parser_is_reproducible(self):
        blocks = [Block("FUNDAMENTOS", page=1),
                  Block("Sexto. Razón sexta.", page=1),
                  Block("Séptimo. Razón séptima.", page=2),
                  Block("Octavo. Razón octava.", page=2),
                  Block("DECISIÓN", page=2), Block("Declararon infundado.", page=2)]
        current = JurisprudenceParser().parse(blocks)
        self.assertEqual([u.unit_number for u in current if u.unit_type == "foundation"],
                         ["Sexto", "Séptimo", "Octavo"])
        self.assertEqual((current[1].page_start, current[1].page_end), (2, 2))
        legacy = JurisprudenceParser(legacy=True).parse(blocks)
        self.assertEqual([u.unit_number for u in legacy if u.unit_type == "foundation"],
                         ["Sexto", "Octavo"])

    def test_heading_only_foundation_is_attached_to_numbered_unit(self):
        blocks = [Block("FUNDAMENTOS", page=1), Block("Delimitación del petitorio", page=1),
                  Block("1. El pedido debe examinarse.", page=1),
                  Block("2. El Tribunal resuelve.", page=2),
                  Block("HA RESUELTO", page=2), Block("Declarar fundada.", page=2)]
        units = JurisprudenceParser().parse(blocks)
        self.assertEqual([u.unit_type for u in units],
                         ["foundation", "foundation", "decision"])
        self.assertEqual(units[0].heading, "Delimitación del petitorio")
        self.assertEqual(units[0].unit_number, "1")
        self.assertEqual(len(JurisprudenceParser(legacy=True).parse(blocks)), 4)

    def test_tc_verification_footer_removed_only_when_complete(self):
        footer = ["Esta es una representación impresa cuya autenticidad puede ser contrastada con la representación imprimible",
                  "localizada en la sede digital del Tribunal Constitucional. La verificación puede ser efectuada a partir de la fecha",
                  "de publicación web de la presente resolución. Base legal: Decreto Legislativo N.° 1412, Decreto Supremo N.°",
                  "029-2021-PCM y la Directiva N.° 002-2021-PCM/SGTD.",
                  "URL: https://www.tc.gob.pe/jurisprudencia/2026/00001.pdf"]
        blocks = [Block("4. Razón anterior.", page=1)] + [Block(line, page=1) for line in footer] + [
            Block("El razonamiento continúa.", page=2)]
        cleaned, removed = remove_repeated_page_furniture(blocks, strip_verification=True)
        self.assertEqual(removed, 5)
        self.assertEqual([b.text for b in cleaned], [blocks[0].text, blocks[-1].text])
        incomplete, removed = remove_repeated_page_furniture(blocks[:-2] + blocks[-1:],
                                                               strip_verification=True)
        self.assertEqual(removed, 0)
        self.assertEqual(len(incomplete), len(blocks) - 1)

    def test_expanded_header_removal_preserves_legal_opening(self):
        blocks = []
        for page in range(1, 5):
            blocks.extend(Block(text, page=page) for text in (
                str(page), "CORTE SUPREMA", "DE JUSTICIA", "DE LA REPÚBLICA",
                "SALA PENAL PERMANENTE", "CASACIÓN N.° 123-2025", "LIMA",
                f"{page}. Razonamiento jurídico de la página {page}."))
        cleaned, removed = remove_repeated_page_furniture(blocks, expanded_top=True)
        self.assertGreater(removed, 0)
        self.assertFalse(any(b.text == "CASACIÓN N.° 123-2025" for b in cleaned))
        self.assertEqual(sum("Razonamiento jurídico" in b.text for b in cleaned), 4)

    def test_tc_official_url_is_from_source_and_not_derived_from_arbitrary_domain(self):
        base = [Block("AUTO DEL TRIBUNAL CONSTITUCIONAL", page=1),
                Block("EXP. N.° 00001-2025-PA/TC", page=1),
                Block("Lima, 9 de abril de 2026", page=1),
                Block("RESUELVE", page=1), Block("Declarar improcedente.", page=1)]
        source = ExtractedDocument("auto.pdf", "pdf", base + [
            Block("URL: https://www.tc.gob.pe/jurisprudencia/2026/00001.pdf", page=1)], "a" * 64)
        with patch("app.legal_ingestion.service.extract", return_value=source):
            current = stage_file("auto.pdf")
            legacy = stage_file("auto.pdf", parser_version="legal-v2.1.0")
        self.assertEqual(current.metadata["official_url"],
                         "https://www.tc.gob.pe/jurisprudencia/2026/00001.pdf")
        self.assertNotIn("official_url", legacy.metadata)
        source.blocks[-1].text = "URL: https://example.com/jurisprudencia/2026/00001.pdf"
        with patch("app.legal_ingestion.service.extract", return_value=source):
            self.assertNotIn("official_url", stage_file("auto.pdf").metadata)

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

    def test_preliminary_title_resets_index_hierarchy_and_article_heading(self):
        units = NormativeParser().parse([Block("TÍTULO VII"), Block("CAPÍTULO IV"),
            Block("DISPOSICIONES COMPLEMENTARIAS FINALES"), Block("TÍTULO PRELIMINAR"),
            Block("Artículo I.- Contenido"), Block("El código establece las reglas."),
            Block("TÍTULO I"), Block("Artículo 1.- Objeto"), Block("El objeto se define.")])
        self.assertEqual([u.title for u in units], ["PRELIMINAR", "I"])
        self.assertIsNone(units[0].chapter)
        self.assertEqual([u.heading for u in units], ["Contenido", "Objeto"])

    def test_plural_disposition_heading_is_not_a_legal_unit(self):
        blocks = [Block("DISPOSICIONES GENERALES"), Block("Artículo 1.- Regla"),
                  Block("DISPOSICIÓN PRIMERA.- Vigencia especial")]
        units = NormativeParser().parse(blocks)
        self.assertEqual([u.unit_type for u in units], ["article", "disposition"])
        self.assertNotIn("DISPOSICIONES GENERALES", units[0].text)

    def test_final_provisions_do_not_extend_last_article(self):
        blocks = [Block("Artículo 448.- Regla"), Block("Texto del artículo."),
                  Block("DISPOSICIONES FINALES"), Block("PRIMERA.- Vigencia"),
                  Block("La ley entra en vigor."), Block("SEGUNDA.- Derogación"),
                  Block("Queda derogada la norma anterior.")]
        units = NormativeParser().parse(blocks)
        self.assertEqual([u.unit_type for u in units], ["article", "disposition", "disposition"])
        self.assertEqual([u.unit_number for u in units[1:]], ["PRIMERA", "SEGUNDA"])
        self.assertNotIn("Vigencia", units[0].text)

    def test_compound_ordinal_provision_is_separate(self):
        units = NormativeParser().parse([Block("DISPOSICIONES TRANSITORIAS"),
            Block("DECIMA.- Extinción"), Block("Regla de extinción."),
            Block("DECIMA PRIMERA.- Publicaciones"), Block("Regla de publicación.")])
        self.assertEqual([u.unit_number for u in units], ["DECIMA", "DECIMA PRIMERA"])

    def test_complementary_provision_sections_and_embedded_amending_article(self):
        units = NormativeParser().parse([
            Block("DISPOSICIONES COMPLEMENTARIAS FINALES", index=1),
            Block("PRIMERA.- Vigencia", index=2), Block("La ley entra en vigor mañana.", index=3),
            Block("DISPOSICIONES COMPLEMENTARIAS MODIFICATORIAS", index=4),
            Block("PRIMERA.- Modificación", index=5),
            Block("Modifícase el texto siguiente:", index=6),
            Block("“Artículo 38.- Nuevo texto de otra norma.”", index=7),
            Block("DISPOSICIÓN COMPLEMENTARIA TRANSITORIA", index=8),
            Block("ÚNICA.- Procedimientos en trámite", index=9),
            Block("Los trámites existentes continúan.", index=10)])
        self.assertEqual([u.unit_type for u in units], ["disposition"] * 3)
        self.assertEqual([u.unit_number for u in units], ["PRIMERA", "PRIMERA", "ÚNICA"])
        self.assertIn("Artículo 38", units[1].text)
        self.assertIn("MODIFICATORIAS", units[1].metadata["provision_heading"])
        self.assertNotIn("DISPOSICIÓN COMPLEMENTARIA TRANSITORIA", units[1].text)
        self.assertEqual(units[2].metadata["provision_heading"], "DISPOSICIÓN COMPLEMENTARIA TRANSITORIA")
        self.assertNotEqual(units[0].content_hash, units[1].content_hash)

    def test_formal_promulgation_closes_provisions_before_editorial_appendix(self):
        parser = NormativeParser()
        units = parser.parse([Block("DISPOSICIONES TRANSITORIAS", index=0),
            Block("PRIMERA.- Regla", index=1), Block("Texto jurídico.", index=2),
            Block("Comuníquese al señor Presidente de la República para su promulgación.", index=3),
            Block("CONCORDANCIAS A LA LEY", index=4), Block("NOTA SPIJ (*)", index=5)])
        self.assertEqual(len(units), 1)
        self.assertEqual(units[0].unit_type, "disposition")
        self.assertNotIn("NOTA SPIJ", units[0].text)
        self.assertEqual(parser.postamble_start_index, 3)

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

    def test_ponente_signature_at_end_is_metadata(self):
        blocks = [Block("AUTO DEL TRIBUNAL CONSTITUCIONAL"), Block("EXP. N.° 04810-2024-PA/TC"),
                  Block("Lima, 23 de octubre de 2025"), Block("RESUELVE"),
                  Block("Declarar improcedente."), Block("PONENTE OCHOA CARDICH")]
        self.assertEqual(case_law_metadata(blocks, "auto.pdf")["ponente"], "OCHOA CARDICH")

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

    def test_written_resolution_date_requires_lima_heading(self):
        blocks = [Block("CORTE SUPREMA"), Block("CASACIÓN N.° 20221-2023"),
                  Block("Lima, siete de abril de dos mil veinticinco -"),
                  Block("Sentencia apelada de veintitrés de noviembre de dos mil veintidós")]
        metadata = case_law_metadata(blocks, "casación.pdf")
        self.assertEqual(metadata["resolution_date"], "2025-04-07")
        self.assertEqual(metadata["resolution_date_text"], "Lima, siete de abril de dos mil veinticinco")

    def test_number_from_quoted_judgment_stays_in_citing_foundation(self):
        blocks = [Block("ATENDIENDO A QUE"), Block("5. El Tribunal publicó la Sentencia 47/2023,"),
                  Block("entre sus fundamentos, señala lo siguiente:"),
                  Block("211. Dentro de esta lógica discursiva se admitirá el recurso."),
                  Block("6. Por tanto, corresponde resolver."), Block("RESUELVE"),
                  Block("Declarar improcedente.")]
        units = JurisprudenceParser().parse(blocks)
        self.assertEqual([u.unit_number for u in units if u.unit_type == "foundation"], ["5", "6"])
        self.assertIn("211.", units[0].text)

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

    def test_editorial_marker_inside_article_blocks_publication(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "ley.txt"
            path.write_text("Artículo 1.- La sociedad constituyenla(*) NOTA SPIJ conforme a ley.", encoding="utf-8")
            staged = stage_file(path, family="normative")
        self.assertIn("editorial_material_mixed_with_law", staged.warnings)
        self.assertEqual(staged.ingestion_status, "review_required")

    def test_versioned_amendment_inside_article_requires_review(self):
        blocks = [Block("LEY N° 29571"), Block("Artículo 1.- Protección"),
                  Block("El consumidor tiene derecho a protección."),
                  Block("(*) Literal modificado por la Ley N° 31040, cuyo texto es el siguiente:")]
        source = ExtractedDocument("codigo.docx", "docx", blocks, "a" * 64)
        with patch("app.legal_ingestion.service.extract", return_value=source):
            staged = stage_file("codigo.docx")
        self.assertIn("versioned_amendment_mixed_with_law", staged.warnings)

    def test_large_article_number_restart_requires_review(self):
        blocks = [Block("LEY N° 29571"), Block("Artículo 1.- Inicio"),
                  Block("Regla inicial."), Block("Artículo 150.- Cierre"),
                  Block("Regla de cierre."), Block("TEXTO INCORPORADO:"),
                  Block("Artículo 37.- Texto de otra versión"), Block("Regla adicional.")]
        source = ExtractedDocument("codigo.docx", "docx", blocks, "a" * 64)
        with patch("app.legal_ingestion.service.extract", return_value=source):
            staged = stage_file("codigo.docx")
        self.assertIn("article_numbering_restart_review_required", staged.warnings)

    def test_unverified_precedent_claim_blocks_publication(self):
        blocks = [Block("CORTE SUPREMA"), Block("CASACIÓN N.° 34397-2023"),
                  Block("Lima, 15 de octubre de 2025"),
                  Block("SUMILLA: PRECEDENTE VINCULANTE sobre remuneración"),
                  Block("FUNDAMENTOS"), Block("1. Razón."), Block("DECISIÓN"),
                  Block("Declararon infundado.")]
        extracted = ExtractedDocument("casación.pdf", "pdf", blocks, "a" * 64)
        with patch("app.legal_ingestion.service.extract", return_value=extracted):
            staged = stage_file("casación.pdf")
        self.assertIn("precedent_claim_unverified", staged.warnings)

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
        self.assertNotIn("split_page_provenance_review_required", staged.warnings)
        self.assertTrue(all(part.page_start == part.page_end for part in staged.units if part.part_count))

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

    def test_resolution_heading_overrides_editorial_filename(self):
        blocks = [Block("EXP. N.º 00102-2022-Q/TC"),
                  Block("AUTO DEL TRIBUNAL CONSTITUCIONAL"),
                  Block("Lima, 9 de abril de 2026"),
                  Block("VISTO"), Block("El escrito de la parte recurrente."),
                  Block("ATENDIENDO A QUE"), Block("1. La solicitud es improcedente."),
                  Block("RESUELVE"), Block("Declarar improcedente la solicitud.")]
        source = ExtractedDocument("TC_llama_atencion.pdf", "pdf", blocks, "a" * 64)
        with patch("app.legal_ingestion.service.extract", return_value=source):
            staged = stage_file("TC_llama_atencion.pdf")
        self.assertEqual(staged.document_type, "order")
        self.assertEqual(staged.metadata["resolution_type"], "auto")

    def test_tc_primary_date_with_al_dia_del_mes(self):
        blocks = [Block("EXP. N.º 00005-2025-PCC/TC"),
                  Block("AUTO DEL TRIBUNAL CONSTITUCIONAL"),
                  Block("En Lima, al día 1 del mes de diciembre de 2025, se emite el auto."),
                  Block("VISTO"), Block("RESUELVE")]
        metadata = case_law_metadata(blocks, "auto.pdf")
        self.assertEqual(metadata["resolution_date"], "2025-12-01")
        self.assertEqual(metadata["resolution_type"], "auto")

    def test_repeated_multiline_pdf_header_is_removed_without_legal_heading(self):
        blocks = []
        for page in range(1, 5):
            for line in ("EXP. N.º 00005-2025-PCC/TC", "JURADO NACIONAL DE",
                         "ELECCIONES", "AUTO 2 - MEDIDA CAUTELAR",
                         "FUNDAMENTOS", f"{page}. Razón jurídica de la página {page}."):
                blocks.append(Block(line, page=page, index=len(blocks)))
        cleaned, removed = remove_repeated_page_furniture(blocks)
        self.assertEqual(removed, 16)
        self.assertEqual(sum(b.text == "FUNDAMENTOS" for b in cleaned), 4)
        self.assertEqual(sum(b.text.startswith("1. Razón") for b in cleaned), 1)

    def test_separate_vote_does_not_extend_main_decision_or_foundations(self):
        blocks = [Block("SENTENCIA DEL TRIBUNAL CONSTITUCIONAL", page=1),
                  Block("FUNDAMENTOS", page=1), Block("1. Razón de mayoría.", page=1),
                  Block("HA RESUELTO", page=2), Block("Declarar fundada la demanda.", page=2),
                  Block("FUNDAMENTO DE VOTO DEL MAGISTRADO", page=3),
                  Block("DOMÍNGUEZ HARO", page=3),
                  Block("ANÁLISIS DEL CASO EN CONCRETO", page=3),
                  Block("1. Considero que procede por otra razón.", page=3),
                  Block("DECISIÓN", page=3), Block("Comparto el fallo.", page=3)]
        units = JurisprudenceParser().parse(blocks)
        self.assertEqual([u.unit_type for u in units],
                         ["foundation", "decision", "separate_opinion"])
        self.assertNotIn("DOMÍNGUEZ HARO", units[1].text)
        self.assertEqual((units[-1].page_start, units[-1].page_end), (3, 3))

    def test_vote_phrase_inside_reasoning_is_not_a_heading(self):
        units = JurisprudenceParser().parse([
            Block("FUNDAMENTOS"), Block("1. El fundamento de voto del magistrado consta en autos."),
            Block("RESUELVE"), Block("Declarar improcedente la petición.")])
        self.assertEqual([u.unit_type for u in units], ["foundation", "decision"])

    def test_named_separate_votes_remain_outside_majority_decision(self):
        units = JurisprudenceParser().parse([
            Block("RESUELVE"), Block("Declarar fundada la demanda."),
            Block("VOTO DEL MAGISTRADO HERNÁNDEZ CHÁVEZ"),
            Block("1. Concuerdo con el resultado."),
            Block("VOTO SINGULAR DE LA MAGISTRADA LEDESMA NARVÁEZ"),
            Block("1. Discrepo del resultado."),
            Block("RESUELVE"), Block("Declarar improcedente la demanda.")])
        self.assertEqual([u.unit_type for u in units],
                         ["decision", "separate_opinion", "separate_opinion"])
        self.assertIn("Declarar improcedente", units[-1].text)
        self.assertNotIn("Discrepo", units[0].text)

    def test_cassation_autos_y_vistos_closes_sumilla(self):
        blocks = [Block("CORTE SUPREMA DE JUSTICIA DE LA REPÚBLICA", page=1),
                  Block("RECURSO CASACIÓN N.º 1913-2023/VENTANILLA", page=1),
                  Block("SUMILLA: Cuestión jurídica relevante.", page=1),
                  Block("Regla interpretativa.", page=1),
                  Block("AUTOS y VISTOS: el recurso interpuesto", page=1),
                  Block("Se impugna la resolución.", page=1),
                  Block("FUNDAMENTOS", page=2), Block("PRIMERO.- Razón.", page=2),
                  Block("DECISIÓN", page=3), Block("Declararon fundado el recurso.", page=3)]
        metadata = case_law_metadata(blocks, "casacion.pdf")
        units = JurisprudenceParser().parse(blocks)
        self.assertNotIn("AUTOS y VISTOS", metadata["sumilla"])
        self.assertEqual([u.unit_type for u in units],
                         ["sumilla", "antecedent", "foundation", "decision"])

    def test_primary_court_and_chamber_do_not_follow_cited_court(self):
        blocks = [Block("CORTE SUPERIOR DE JUSTICIA DE LIMA"),
                  Block("PRIMERA SALA CONSTITUCIONAL"),
                  Block("EXP. N.º 19340-2025-0-1801-JR-DC-06"),
                  Block("Resolución N.º 15"),
                  Block("La Corte Suprema resolvió otro caso."),
                  Block("VISTOS")]
        metadata = case_law_metadata(blocks, "habeas.pdf")
        self.assertEqual(metadata["court"], "Corte Superior")
        self.assertEqual(metadata["chamber"], "Primera Sala Constitucional")

    def test_penal_chamber_from_cassation_header(self):
        blocks = [Block("CORTE SUPREMA DE JUSTICIA DE LA REPÚBLICA"),
                  Block("SALA PENAL PERMANENTE"),
                  Block("RECURSO CASACIÓN N.º 1913-2023/VENTANILLA")]
        metadata = case_law_metadata(blocks, "casacion.pdf")
        self.assertEqual(metadata["court"], "Corte Suprema")
        self.assertEqual(metadata["chamber"], "Sala Penal Permanente")

    def test_corte_superior_header_prevents_false_normative_family(self):
        blocks = [Block("CORTE SUPERIOR DE JUSTICIA DE LIMA"),
                  Block("PRIMERA SALA CONSTITUCIONAL"),
                  Block("Expediente : N.º 19340-2025-0-1801-JR-DC-06"),
                  Block("VISTOS"), Block("La Constitución protege el derecho."),
                  Block("CONSIDERANDO"), Block("PRIMERO.- Análisis de la causa."),
                  Block("RESUELVE"), Block("Declarar improcedente la demanda.")]
        source = ExtractedDocument("En_mayoria_habeas_corpus.pdf", "pdf", blocks, "b" * 64)
        with patch("app.legal_ingestion.service.extract", return_value=source):
            staged = stage_file("En_mayoria_habeas_corpus.pdf")
        self.assertEqual(staged.metadata["family"], "jurisprudence")
        self.assertEqual(staged.metadata["court"], "Corte Superior")
        self.assertEqual([u.unit_type for u in staged.units],
                         ["antecedent", "foundation", "decision"])

    def test_compound_ordinal_foundations_are_separate(self):
        units = JurisprudenceParser().parse([
            Block("FUNDAMENTOS"), Block("Duodécimo. Razón previa.", page=1),
            Block("Decimotercero. Nueva razón.", page=2),
            Block("Decimocuarto. Razón final.", page=2),
            Block("DECISIÓN", page=3), Block("Declararon fundado el recurso.", page=3)])
        self.assertEqual([u.unit_number for u in units[:3]],
                         ["Duodécimo", "Decimotercero", "Decimocuarto"])
        self.assertEqual([u.page_start for u in units[:3]], [1, 2, 2])

    def test_wrapped_case_reference_does_not_start_new_foundation(self):
        units = JurisprudenceParser().parse([
            Block("ATENDIENDO A QUE"), Block("8. Se cita el Auto", page=2),
            Block("5 - 00004-2024-PCC/TC, fundamento 6).", page=3),
            Block("9. Corresponde resolver el pedido.", page=3),
            Block("RESUELVE", page=4), Block("Admitir la solicitud.", page=4)])
        self.assertEqual([u.unit_number for u in units[:2]], ["8", "9"])
        self.assertIn("00004-2024-PCC/TC", units[0].text)
        self.assertEqual((units[0].page_start, units[0].page_end), (2, 3))

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

    def test_promulgating_instrument_is_bounded_before_separate_tuo_annex(self):
        lines = ["Decreto Supremo que aprueba el texto único ordenado",
                 "DECRETO SUPREMO N° 006-2026-JUS", "EL PRESIDENTE DE LA REPÚBLICA",
                 "DECRETA:", "Artículo 1. Objeto", "Se aprueba el texto único ordenado.",
                 "DISPOSICIÓN COMPLEMENTARIA DEROGATORIA", "ÚNICA. Derogación",
                 "Derogar el decreto anterior.",
                 "Dado en la Casa de Gobierno, en Lima, el día de hoy.",
                 "Presidente de la República", "TEXTO ÚNICO ORDENADO DE LA LEY",
                 "TÍTULO PRELIMINAR", "Artículo I. Anexo", "El anexo tiene reglas distintas."]
        blocks = [Block(line, index=i) for i, line in enumerate(lines)]
        source = ExtractedDocument("norma.docx", "docx", blocks, "a" * 64)
        with patch("app.legal_ingestion.service.extract", return_value=source):
            decree = stage_file("norma.docx", segment="promulgating_instrument")
            whole = stage_file("norma.docx")
        self.assertEqual(decree.document_type, "regulation")
        self.assertEqual(decree.metadata["number"], "006-2026-JUS")
        self.assertIn("Casa de Gobierno", decree.metadata["issued_date_text"])
        self.assertEqual(decree.metadata["source_segment"]["annex_start_block_index"], 11)
        self.assertEqual([u.unit_type for u in decree.units], ["article", "disposition"])
        self.assertNotIn("Artículo I. Anexo", str(decree.to_dict()))
        self.assertIn("I", [u.unit_number for u in whole.units if u.unit_type == "article"])
        self.assertNotEqual(decree.document_hash, whole.document_hash)
        self.assertEqual(decree.ingestion_status, "staged")

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
