"""Offline transaction and mapping tests; no database connection is opened."""
import unittest
from dataclasses import replace
from uuid import UUID

from app.legal_ingestion.identity import content_hash, search_normalize, stable_document_id
from app.legal_ingestion.models import LegalUnit, StagedDocument
from app.legal_ingestion.publication import LegalRelation, PublicationAdapter


class FakeConnection:
    def __init__(self, existing=None, fail_batch=False, existing_status="ready"):
        self.existing = existing
        self.existing_status = existing_status
        self.fail_batch = fail_batch
        self.commands = []
        self.commits = 0
        self.rollbacks = 0
        self.closed = False

    def cursor(self):
        return self

    def execute(self, sql, params):
        self.commands.append((sql, params))
        if self.fail_batch and sql.startswith("insert into public.legal_units"):
            raise RuntimeError("unit batch rejected")

    def fetchone(self):
        return (self.existing, self.existing_status) if self.existing else None

    def commit(self):
        self.commits += 1

    def rollback(self):
        self.rollbacks += 1

    def close(self):
        self.closed = True


def fixture(unit_count=3):
    units = []
    for sequence in range(1, unit_count + 1):
        body = f"Artículo {sequence}. Regla completa {sequence}."
        normalized = search_normalize(body)
        units.append(LegalUnit("article", sequence, body, normalized,
            content_hash("article", str(sequence), None, normalized),
            unit_number=str(sequence), search_text=body, token_count=len(body.split()),
            page_start=sequence, page_end=sequence, metadata={"source_block_indexes": [sequence]}))
    digest = "a" * 64
    return StagedDocument("Ley de prueba", "law", digest, "ley.docx", "docx", "2.0-test",
        "high", "staged", False, {"source_file_hash": "b" * 64,
        "parser_name": "normative", "rama": "civil"}, units,
        document_id=stable_document_id(digest, "2.0-test"))


class PublicationTests(unittest.TestCase):
    def test_offline_mapping_keeps_pages_hashes_metadata_and_optional_vectors(self):
        doc = fixture(2)
        adapter = PublicationAdapter(lambda: None)
        document, units, relations = adapter.prepare(doc)
        self.assertEqual(document["document_hash"], doc.document_hash)
        self.assertEqual(document["parser_version"], doc.parser_version)
        self.assertEqual(document["rama"], "civil")
        self.assertEqual(units[0]["page_start"], 1)
        self.assertEqual(units[0]["content_hash"], doc.units[0].content_hash)
        self.assertIsNone(units[0]["embedding"])
        self.assertEqual(relations, [])

    def test_publish_uses_one_transaction_and_batched_units(self):
        doc = fixture(5)
        fake = FakeConnection()
        result = PublicationAdapter(lambda: fake, batch_size=2).publish(
            doc, embeddings=[[0.0] * 1536 for _ in doc.units],
            relations=[LegalRelation(1, "CITES", target_sequence=2)])
        self.assertEqual((result.documents_created, result.units_created, result.relations_created), (1, 5, 1))
        self.assertEqual(sum(sql.startswith("insert into public.legal_units") for sql, _ in fake.commands), 3)
        self.assertEqual(sum(sql.startswith("insert into public.legal_relations") for sql, _ in fake.commands), 1)
        self.assertEqual((fake.commits, fake.rollbacks, fake.closed), (1, 0, True))
        self.assertTrue(any("ingestion_status='ready'" in sql for sql, _ in fake.commands))

    def test_idempotent_retry_does_not_insert_document_or_units(self):
        doc = fixture(1)
        fake = FakeConnection(existing=doc.document_id)
        result = PublicationAdapter(lambda: fake).publish(doc, embeddings=[[0.0] * 1536])
        self.assertEqual((result.documents_created, result.duplicates_skipped), (0, 1))
        self.assertFalse(any(sql.startswith("insert into public.legal_units") for sql, _ in fake.commands))
        self.assertEqual(fake.commits, 1)

    def test_existing_incomplete_version_is_not_reported_as_success(self):
        doc = fixture(1)
        fake = FakeConnection(existing=doc.document_id, existing_status="processing")
        with self.assertRaisesRegex(RuntimeError, "incomplete"):
            PublicationAdapter(lambda: fake).publish(doc, embeddings=[[0.0] * 1536])
        self.assertEqual(fake.rollbacks, 1)
        self.assertFalse(any("duplicates_skipped=1" in sql for sql, _ in fake.commands))

    def test_failed_batch_rolls_back_and_audits_failure(self):
        doc = fixture(3)
        fake = FakeConnection(fail_batch=True)
        with self.assertRaisesRegex(RuntimeError, "unit batch rejected"):
            PublicationAdapter(lambda: fake, batch_size=2).publish(
                doc, embeddings=[[0.0] * 1536 for _ in doc.units])
        self.assertEqual(fake.rollbacks, 1)
        self.assertEqual(fake.commits, 1)  # separate failed-run audit
        self.assertTrue(any("'failed'" in sql for sql, _ in fake.commands))
        self.assertFalse(any("ingestion_status='ready'" in sql for sql, _ in fake.commands))

    def test_review_and_ocr_rejected_before_connection(self):
        doc = fixture(1)
        doc.ingestion_status = "review_required"
        with self.assertRaisesRegex(ValueError, "Review-required"):
            PublicationAdapter(lambda: self.fail("connection opened")).publish(doc, embeddings=[[0.0] * 1536])
        doc.ingestion_status, doc.ocr_required = "staged", True
        with self.assertRaises(ValueError):
            PublicationAdapter(lambda: self.fail("connection opened")).prepare(doc)

    def test_missing_or_wrong_embedding_rejected_before_connection(self):
        doc = fixture(1)
        adapter = PublicationAdapter(lambda: self.fail("connection opened"))
        with self.assertRaisesRegex(ValueError, "1536"):
            adapter.publish(doc, embeddings=[[0.0] * 10])
        with self.assertRaisesRegex(ValueError, "Final publication"):
            adapter.publish(doc, embeddings=[None])
        with self.assertRaisesRegex(ValueError, "1536"):
            adapter.publish(doc, embeddings=[[float("nan")] * 1536])

    def test_duplicate_hash_and_invalid_relation_rejected(self):
        doc = fixture(2)
        doc.units[1].content_hash = doc.units[0].content_hash
        adapter = PublicationAdapter(lambda: self.fail("connection opened"))
        with self.assertRaisesRegex(ValueError, "duplicate"):
            adapter.prepare(doc)
        doc = fixture(2)
        with self.assertRaisesRegex(ValueError, "target sequence"):
            adapter.prepare(doc, relations=[LegalRelation(1, "CITES", target_sequence=9)])

    def test_new_version_keeps_distinct_stable_identity(self):
        doc = fixture(1)
        other = replace(doc, parser_version="2.1-test",
                        document_id=stable_document_id(doc.document_hash, "2.1-test"))
        self.assertNotEqual(UUID(doc.document_id), UUID(other.document_id))


if __name__ == "__main__":
    unittest.main()
