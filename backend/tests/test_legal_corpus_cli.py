"""Offline safety tests for the future manifest-only publication CLI."""
import io
import json
import tempfile
import unittest
from contextlib import contextmanager, redirect_stdout, redirect_stderr
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from app.legal_ingestion import corpus_cli


class CorpusCliTests(unittest.TestCase):
    def test_published_batch_001_manifest_remains_reproducible_with_legacy_parser(self):
        entries = corpus_cli._load_manifest(str(corpus_cli.MANIFEST))
        self.assertEqual(len(entries), 2)
        for entry in entries:
            self.assertEqual(entry["parser_version"], "legal-v2.1.0")
            document = corpus_cli._stage_entry(entry)
            self.assertEqual(document.document_hash, entry["document_hash"])
            self.assertEqual(document.document_id, entry["stable_identifier"])
            self.assertEqual(len(document.units), entry["expected_unit_count"])

    def test_batch_002_manifest_uses_new_parser_and_is_enabled(self):
        entries = corpus_cli._load_manifest(str(corpus_cli.MANIFEST_002))
        self.assertEqual(len(entries), 2)
        for entry in entries:
            self.assertEqual(entry["parser_version"], "legal-v2.1.1")
            document = corpus_cli._stage_entry(entry)
            self.assertEqual(document.document_hash, entry["document_hash"])
            self.assertEqual(len(document.units), entry["expected_unit_count"])
        with patch.object(corpus_cli, "_embedding_configured") as embedding, patch.object(
                corpus_cli, "_adapter") as adapter, patch.object(
                corpus_cli, "_publish") as publish:
            code = corpus_cli.main(["publish-batch", str(corpus_cli.MANIFEST_002)])
        self.assertEqual(code, 0)
        embedding.assert_called_once()
        adapter.assert_called_once()
        publish.assert_called_once_with(entries, adapter.return_value, batch_id="002")

    def test_batch_001_is_still_enabled(self):
        entries = corpus_cli._load_manifest(str(corpus_cli.MANIFEST))
        with patch.object(corpus_cli, "_embedding_configured") as embedding, patch.object(
                corpus_cli, "_adapter") as adapter, patch.object(
                corpus_cli, "_publish") as publish:
            code = corpus_cli.main(["publish-batch", str(corpus_cli.MANIFEST)])
        self.assertEqual(code, 0)
        embedding.assert_called_once()
        publish.assert_called_once_with(entries, adapter.return_value, batch_id="001")

    def test_unknown_batch_is_not_enabled(self):
        with patch.object(corpus_cli, "_stage_entry") as stage:
            with self.assertRaisesRegex(corpus_cli.BatchError, "BATCH_NOT_ENABLED_FOR_PUBLICATION"):
                corpus_cli._publish([{}], object(), batch_id="003")
        stage.assert_not_called()

    def test_batch_002_changed_manifest_hash_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            changed_manifest = Path(folder) / "batch_002.json"
            with patch.object(corpus_cli, "MANIFEST_002", changed_manifest):
                for field in ("document_hash", "source_file_hash"):
                    with self.subTest(field=field):
                        manifest_data = json.loads((corpus_cli.ROOT / "docs/LEGAL_KNOWLEDGE_V2_BATCH_002.json")
                                                   .read_text(encoding="utf-8"))
                        manifest_data["documents"][0][field] = "0" * 64
                        changed_manifest.write_text(json.dumps(manifest_data), encoding="utf-8")
                        with self.assertRaisesRegex(corpus_cli.BatchError, "MANIFEST_QUALIFICATION_MISMATCH"):
                            corpus_cli._load_manifest(str(changed_manifest))

    def test_batch_002_new_document_starts_from_confirmed_counts(self):
        document = SimpleNamespace(units=[SimpleNamespace(search_text="legal unit")] * 15,
                                   document_hash="a" * 64)
        adapter = Mock()
        adapter.publish.return_value = SimpleNamespace(duplicates_skipped=0, documents_created=1,
                                                       units_created=15, relations_created=0,
                                                       document_id="doc", run_id="run")
        provider = Mock()
        provider.MODEL = corpus_cli.MODEL
        with patch.object(corpus_cli, "_stage_entry", return_value=document), patch.object(
                corpus_cli, "_presence", return_value="NOT_PRESENT"), patch.object(
                corpus_cli, "_current_counts", side_effect=[(4, 38, 0, 4), (5, 53, 0, 5)]) as counts, patch.object(
                corpus_cli, "embedding_batches", return_value=[[0.0] * 1536] * 15), patch.object(
                corpus_cli, "_verify_published") as verify, patch(
                "app.services.embedding_service.EmbeddingService", return_value=provider):
            with redirect_stdout(io.StringIO()) as output:
                corpus_cli._publish([{}], adapter, batch_id="002")
        self.assertEqual(counts.call_count, 2)
        verify.assert_called_once()
        self.assertIn("COUNTS=5/53/0/5", output.getvalue())

    def test_batch_002_resume_uses_its_own_count_baseline_without_embeddings(self):
        documents = [SimpleNamespace(units=[None] * 15, document_hash="a" * 64),
                     SimpleNamespace(units=[None] * 11, document_hash="b" * 64)]
        with patch.object(corpus_cli, "_stage_entry", side_effect=documents), patch.object(
                corpus_cli, "_presence", return_value="ALREADY_PRESENT_AND_IDENTICAL"), patch.object(
                corpus_cli, "_current_counts", side_effect=[(5, 53, 0, 5), (6, 64, 0, 6)]):
            with redirect_stdout(io.StringIO()) as output:
                corpus_cli._publish([{}, {}], object(), batch_id="002")
        self.assertIn("BATCH=002 ITEM=2 STATUS=ALREADY_PRESENT_AND_IDENTICAL EMBEDDINGS=0",
                      output.getvalue())

    def test_manifest_must_match_approved_qualification(self):
        row = {"source_path": "backend/raw_docs/jurisprudencia/auto.pdf",
               "source_file_hash": "a" * 64, "document_hash": "b" * 64,
               "parser_version": "legal-v2.1.0", "document_type": "order",
               "total_units": 12, "category": "PUBLISHABLE"}
        entry = {**{key: row[key] for key in ("source_path", "source_file_hash",
                                                "document_hash", "parser_version", "document_type")},
                 "expected_unit_count": 12, "quality_status": "PUBLISHABLE",
                 "stable_identifier": "id"}
        with tempfile.TemporaryDirectory() as folder:
            manifest = Path(folder) / "manifest.json"
            qualification = Path(folder) / "qualification.json"
            qualification.write_text(json.dumps({"records": [row]}), encoding="utf-8")
            manifest.write_text(json.dumps({"batch_id": "001", "documents": [entry]}), encoding="utf-8")
            with patch.object(corpus_cli, "MANIFEST", manifest), patch.object(
                    corpus_cli, "QUALIFICATION", qualification):
                self.assertEqual(len(corpus_cli._load_manifest(str(manifest))), 1)
                entry["document_hash"] = "c" * 64
                manifest.write_text(json.dumps({"batch_id": "001", "documents": [entry]}), encoding="utf-8")
                with self.assertRaisesRegex(corpus_cli.BatchError, "MANIFEST_QUALIFICATION_MISMATCH"):
                    corpus_cli._load_manifest(str(manifest))

    def test_arbitrary_manifest_is_rejected_before_provider_or_db(self):
        with patch.object(corpus_cli, "_adapter") as adapter, patch.object(
                corpus_cli, "_embedding_configured") as embedding:
            with redirect_stderr(io.StringIO()) as output:
                code = corpus_cli.main(["publish-batch", "../other.json"])
        self.assertEqual(code, 1)
        self.assertIn("UNAPPROVED_MANIFEST_PATH", output.getvalue())
        adapter.assert_not_called()
        embedding.assert_not_called()

    def test_inspect_without_dsn_never_opens_db_or_provider(self):
        document = SimpleNamespace(document_id="doc-id", document_type="order", units=[1, 2],
                                   document_hash="f" * 64)
        with patch.dict("os.environ", {}, clear=True), patch.object(
                corpus_cli, "_load_manifest", return_value=[{}]), patch.object(
                corpus_cli, "_stage_entry", return_value=document), patch.object(
                corpus_cli, "_adapter") as adapter, patch.object(
                corpus_cli, "_presence") as presence:
            with redirect_stdout(io.StringIO()) as output:
                code = corpus_cli.main(["inspect-batch", str(corpus_cli.MANIFEST)])
        self.assertEqual(code, 0)
        self.assertIn("PRESENCE=UNVERIFIED_OFFLINE", output.getvalue())
        self.assertIn("EMBEDDINGS_REQUIRED=2", output.getvalue())
        adapter.assert_not_called()
        presence.assert_not_called()

    def test_resume_skips_identical_without_generating_embeddings(self):
        document = SimpleNamespace(units=[1], document_hash="f" * 64)
        with patch.object(corpus_cli, "_stage_entry", return_value=document), patch.object(
                corpus_cli, "_presence", return_value="ALREADY_PRESENT_AND_IDENTICAL"), patch.object(
                corpus_cli, "_current_counts", return_value=(3, 16, 0, 3)):
            with redirect_stdout(io.StringIO()) as output:
                corpus_cli._publish([{}], object())
        self.assertIn("EMBEDDINGS=0", output.getvalue())

    def test_conflict_stops_before_provider(self):
        document = SimpleNamespace(units=[1], document_hash="f" * 64)
        with patch.object(corpus_cli, "_stage_entry", return_value=document), patch.object(
                corpus_cli, "_presence", return_value="CONFLICT"):
            with self.assertRaisesRegex(corpus_cli.BatchError, "DOCUMENT_CONFLICT"):
                corpus_cli._publish([{}, {}], object())

    def test_new_document_uses_existing_adapter_and_one_embedding_per_unit(self):
        document = SimpleNamespace(units=[SimpleNamespace(search_text="legal unit")],
                                   document_hash="f" * 64)
        adapter = Mock()
        adapter.publish.return_value = SimpleNamespace(duplicates_skipped=0, documents_created=1, units_created=1,
                                                       relations_created=0, document_id="doc", run_id="run")
        provider = Mock()
        provider.MODEL = corpus_cli.MODEL
        provider.generate_embeddings.return_value = [[0.1] * 1536]
        with patch.object(corpus_cli, "_stage_entry", return_value=document), patch.object(
                corpus_cli, "_presence", return_value="NOT_PRESENT"), patch(
                "app.services.embedding_service.EmbeddingService", return_value=provider), patch.object(
                corpus_cli, "_current_counts", side_effect=[(2, 15, 0, 2), (3, 16, 0, 3)]), patch.object(
                corpus_cli, "_verify_published") as verify:
            with redirect_stdout(io.StringIO()) as output:
                corpus_cli._publish([{}], adapter)
        provider.generate_embeddings.assert_called_once_with(["legal unit"])
        self.assertEqual(len(adapter.publish.call_args.kwargs["embeddings"]), 1)
        verify.assert_called_once()
        self.assertIn("STATUS=COMPLETED_AND_VERIFIED", output.getvalue())

    def test_first_postpublication_failure_stops_before_second_embedding(self):
        documents = [SimpleNamespace(units=[SimpleNamespace(search_text=f"unit {i}")],
                                     document_hash=str(i) * 64) for i in (1, 2)]
        adapter = Mock()
        adapter.publish.return_value = SimpleNamespace(duplicates_skipped=0, documents_created=1,
                                                       units_created=1, relations_created=0,
                                                       document_id="doc", run_id="run")
        provider = Mock()
        provider.MODEL = corpus_cli.MODEL
        provider.generate_embeddings.return_value = [[0.1] * 1536]
        with patch.object(corpus_cli, "_stage_entry", side_effect=documents), patch.object(
                corpus_cli, "_presence", return_value="NOT_PRESENT"), patch.object(
                corpus_cli, "_current_counts", return_value=(2, 15, 0, 2)), patch.object(
                corpus_cli, "_verify_published", side_effect=corpus_cli.BatchError("POSTPUBLICATION_IDENTITY_FAILED")), patch(
                "app.services.embedding_service.EmbeddingService", return_value=provider):
            with self.assertRaisesRegex(corpus_cli.BatchError, "POSTPUBLICATION_IDENTITY_FAILED"):
                corpus_cli._publish([{}, {}], adapter)
        adapter.publish.assert_called_once()
        provider.generate_embeddings.assert_called_once()

    def test_postpublication_requires_completed_matching_run(self):
        document = SimpleNamespace(units=[1, 2])
        result = SimpleNamespace(document_id="doc", run_id="run")
        cursor = Mock()
        cursor.fetchone.return_value = ("run", "completed", 1, 2, 0)

        @contextmanager
        def database(*args, **kwargs):
            yield None, cursor

        with patch.object(corpus_cli, "_database", database), patch.object(
                corpus_cli, "_identity", return_value="ALREADY_PRESENT_AND_IDENTICAL"):
            corpus_cli._verify_published(object(), document, result)
            cursor.fetchone.return_value = ("other-run", "completed", 1, 2, 0)
            with self.assertRaisesRegex(corpus_cli.BatchError, "POSTPUBLICATION_RUN_FAILED"):
                corpus_cli._verify_published(object(), document, result)


if __name__ == "__main__":
    unittest.main()
