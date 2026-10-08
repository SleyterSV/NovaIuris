"""The corpus audit must fail closed if approved material or its source changes."""
import hashlib
import tempfile
import unittest
from pathlib import Path

from app.legal_ingestion.corpus_audit import audit
from app.legal_ingestion.service import stage_file


class CorpusAuditTests(unittest.TestCase):
    def test_manual_approval_is_bound_to_source_parser_and_unit_count(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / "auto.txt"
            source.write_text(
                "TRIBUNAL CONSTITUCIONAL\nEXP. N.º 1234-2025-PA/TC\n"
                "AUTO DEL TRIBUNAL CONSTITUCIONAL\nLima, 1 de diciembre de 2025\n"
                "VISTO\nLa solicitud de la parte recurrente.\n"
                "ATENDIENDO A QUE\n1. La solicitud carece de sustento.\n"
                "RESUELVE\nDeclarar improcedente el pedido.\n", encoding="utf-8")
            staged = stage_file(source)
            digest = hashlib.sha256(source.read_bytes()).hexdigest()
            baseline = {"physical_originals": 1, "records": [{
                "source_path": "auto.txt", "filename": "auto.txt", "format": "txt",
                "source_file_hash": digest, "probable_type": "jurisprudence",
                "already_published": False, "category": "REVIEW_REQUIRED",
                "gate_status": "review_required"}],
                "duplicates": {"same_identity_different_source": []}}
            approval = {"approved": [{"source_path": "auto.txt", "source_file_hash": digest,
                                      "document_hash": staged.document_hash,
                                      "parser_version": staged.parser_version,
                                      "expected_unit_count": len(staged.units)}]}
            self.assertEqual(audit(root, baseline, approval)["records"][0]["category"], "PUBLISHABLE")
            approval["approved"][0]["expected_unit_count"] += 1
            self.assertEqual(audit(root, baseline, approval)["records"][0]["category"], "REVIEW_REQUIRED")
            source.write_text(source.read_text(encoding="utf-8") + "Cambio de fuente.\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Original source changed"):
                audit(root, baseline, approval)

    def test_html_disguised_as_pdf_has_no_gate_status_and_stays_invalid(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / "article.pdf"
            source.write_text("<html><body><p>Editorial summary of another document.</p></body></html>",
                              encoding="utf-8")
            digest = hashlib.sha256(source.read_bytes()).hexdigest()
            baseline = {"physical_originals": 1, "records": [{
                "source_path": "article.pdf", "filename": "article.pdf", "format": "pdf",
                "source_file_hash": digest, "probable_type": "jurisprudence",
                "already_published": False, "category": "INVALID_SOURCE"}],
                "duplicates": {"same_identity_different_source": []}}
            report = audit(root, baseline, {"approved": []})
            self.assertEqual(report["records"][0]["category"], "INVALID_SOURCE")
            self.assertEqual(report["records"][0]["source_format"], "html")


if __name__ == "__main__":
    unittest.main()
