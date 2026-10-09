"""Manifest-bound, resumable V2 batch CLI. Importing has no provider or DB I/O."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys

from .corpus_audit import ROOT, OUTPUT as QUALIFICATION
from .publication import PublicationAdapter, postgres_connection_factory
from .publication_entrypoint import (_counts, _database, _dsn, _embedding_configured,
                                     _identity, MODEL)
from .service import stage_file
from .units import embedding_batches


MANIFEST = ROOT / "docs/LEGAL_KNOWLEDGE_V2_BATCH_001.json"
MANIFEST_002 = ROOT / "docs/LEGAL_KNOWLEDGE_V2_BATCH_002.json"
REVIEW_001 = ROOT / "docs/LEGAL_KNOWLEDGE_V2_CORPUS_RECOVERY_REVIEW.json"


class BatchError(RuntimeError):
    """Safe public error code; underlying provider/SQL errors remain private."""


def _manifest_batch(path: str) -> str:
    resolved = Path(path).resolve()
    if resolved == MANIFEST.resolve():
        return "001"
    if resolved == MANIFEST_002.resolve():
        return "002"
    raise BatchError("UNAPPROVED_MANIFEST_PATH")


def _load_manifest(path: str) -> list[dict]:
    batch_id = _manifest_batch(path)
    manifest_path = MANIFEST if batch_id == "001" else MANIFEST_002
    if not manifest_path.is_file():
        raise BatchError("UNAPPROVED_MANIFEST_PATH")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    entries = manifest.get("documents")
    if manifest.get("batch_id") != batch_id or not isinstance(entries, list) or not 1 <= len(entries) <= 30:
        raise BatchError("MANIFEST_INVALID")
    qualification = json.loads(QUALIFICATION.read_text(encoding="utf-8"))
    approved = {row["source_path"]: row for row in qualification["records"]
                if row["category"] == "PUBLISHABLE"}
    if batch_id == "001" and REVIEW_001.is_file():
        for row in json.loads(REVIEW_001.read_text(encoding="utf-8"))["approved"]:
            approved.setdefault(row["source_path"], {**row, "total_units": row["expected_unit_count"]})
    seen = set()
    for entry in entries:
        if entry.get("quality_status") != "PUBLISHABLE":
            raise BatchError("MANIFEST_QUALITY_NOT_APPROVED")
        source = entry.get("source_path")
        if not isinstance(source, str) or source in seen or source not in approved:
            raise BatchError("MANIFEST_SOURCE_NOT_APPROVED")
        seen.add(source)
        expected = approved[source]
        for key in ("source_file_hash", "document_hash", "parser_version", "document_type"):
            if key == "document_type" and key not in expected:
                continue  # Historical review predates the type field; staging checks it below.
            if entry.get(key) != expected.get(key):
                raise BatchError("MANIFEST_QUALIFICATION_MISMATCH")
        if entry.get("expected_unit_count") != expected.get("total_units"):
            raise BatchError("MANIFEST_UNIT_COUNT_MISMATCH")
    return entries


def _stage_entry(entry: dict):
    relative = Path(entry["source_path"])
    source = (ROOT / relative).resolve()
    if not source.is_relative_to(ROOT) or not source.is_file():
        raise BatchError("SOURCE_OUT_OF_SCOPE")
    document = stage_file(source, parser_version=entry["parser_version"])
    if (document.ingestion_status != "staged" or document.ocr_required or
            document.document_hash != entry["document_hash"] or
            document.metadata.get("source_file_hash") != entry["source_file_hash"] or
            document.parser_version != entry["parser_version"] or
            document.document_type != entry["document_type"] or
            document.document_id != entry["stable_identifier"] or
            len(document.units) != entry["expected_unit_count"]):
        raise BatchError("SOURCE_OR_QUALITY_CHANGED")
    # Exercise the existing mapping contract with no embeddings or I/O.
    PublicationAdapter(lambda: None).prepare(document)
    return document


def _adapter():
    return PublicationAdapter(postgres_connection_factory(_dsn()), batch_size=100)


def _presence(adapter, document):
    with _database(adapter, read_only=True) as (_, cursor):
        return _identity(cursor, document, adapter)


def _current_counts(adapter):
    with _database(adapter, read_only=True) as (_, cursor):
        return tuple(_counts(cursor))


def _verify_published(adapter, document, result):
    """Reopen Postgres after commit; halt the batch if the committed row is incomplete."""
    with _database(adapter, read_only=True) as (_, cursor):
        if _identity(cursor, document, adapter) != "ALREADY_PRESENT_AND_IDENTICAL":
            raise BatchError("POSTPUBLICATION_IDENTITY_FAILED")
        cursor.execute("""select d.ingestion_run_id, r.status, r.documents_created,
                                 r.units_created, r.relations_created
                          from public.legal_documents d
                          join public.legal_ingestion_runs r on r.id=d.ingestion_run_id
                          where d.id=%s""", (result.document_id,))
        row = cursor.fetchone()
        if row is None or (str(row[0]), *row[1:]) != (
                result.run_id, "completed", 1, len(document.units), 0):
            raise BatchError("POSTPUBLICATION_RUN_FAILED")


def _inspect(entries, *, adapter=None, batch_id="001"):
    for index, entry in enumerate(entries, 1):
        document = _stage_entry(entry)
        state = _presence(adapter, document) if adapter is not None else "UNVERIFIED_OFFLINE"
        print(f"BATCH={batch_id} ITEM={index} ID={document.document_id} STATUS=PUBLISHABLE "
              f"TYPE={document.document_type} UNITS={len(document.units)} "
              f"PARSER={entry.get('parser_version', 'UNKNOWN')} "
              f"EMBEDDINGS_REQUIRED={0 if state == 'ALREADY_PRESENT_AND_IDENTICAL' else len(document.units)} "
              f"HASH={document.document_hash[:12]} PRESENCE={state}")
        if state == "CONFLICT":
            raise BatchError("DOCUMENT_CONFLICT")


def _publish(entries, adapter):
    # Validate every manifest entry and source before paying for any embedding.
    documents = [_stage_entry(entry) for entry in entries]
    provider = None
    prior_units = 0
    for index, document in enumerate(documents, 1):
        state = _presence(adapter, document)
        if state not in {"NOT_PRESENT", "ALREADY_PRESENT_AND_IDENTICAL"}:
            raise BatchError("DOCUMENT_CONFLICT")
        expected_before = (2 + index - 1, 15 + prior_units, 0, 2 + index - 1)
        expected_after = (expected_before[0] + 1, expected_before[1] + len(document.units),
                          0, expected_before[3] + 1)
        if state == "ALREADY_PRESENT_AND_IDENTICAL":
            if _current_counts(adapter) != expected_after:
                raise BatchError("DATABASE_COUNTS_UNEXPECTED")
            print(f"BATCH=001 ITEM={index} STATUS=ALREADY_PRESENT_AND_IDENTICAL EMBEDDINGS=0")
            prior_units += len(document.units)
            continue
        if _current_counts(adapter) != expected_before:
            raise BatchError("DATABASE_COUNTS_UNEXPECTED")
        if provider is None:
            from app.services.embedding_service import EmbeddingService
            provider = EmbeddingService()
            if provider.MODEL != MODEL:
                raise BatchError("EMBEDDING_MODEL_MISMATCH")
        vectors = embedding_batches(document.units, provider.generate_embeddings)
        adapter.prepare(document, embeddings=vectors)
        if len(vectors) != len(document.units):
            raise BatchError("EMBEDDING_COUNT_MISMATCH")
        result = adapter.publish(document, embeddings=vectors, relations=())
        if (result.duplicates_skipped or result.documents_created != 1 or
                result.units_created != len(document.units) or result.relations_created != 0):
            raise BatchError("POSTPUBLICATION_RESULT_UNEXPECTED")
        _verify_published(adapter, document, result)
        if _current_counts(adapter) != expected_after:
            raise BatchError("POSTPUBLICATION_COUNTS_FAILED")
        print(f"BATCH=001 ITEM={index} STATUS=COMPLETED_AND_VERIFIED UNITS={result.units_created} "
              f"RELATIONS={result.relations_created} DOCUMENT_ID={result.document_id} "
              f"RUN_ID={result.run_id} COUNTS={'/'.join(map(str, expected_after))}")
        prior_units += len(document.units)
        # Only a committed and read-back-verified document allows the next item.


def main(argv=None):
    parser = argparse.ArgumentParser(description="Approved Legal Knowledge V2 Batch 001")
    commands = parser.add_subparsers(dest="command", required=True)
    for command in ("inspect-batch", "publish-batch"):
        commands.add_parser(command).add_argument("manifest")
    args = parser.parse_args(argv)
    try:
        batch_id = _manifest_batch(args.manifest)
        entries = _load_manifest(args.manifest)
        if args.command == "inspect-batch":
            adapter = _adapter() if os.environ.get("MYKE_LEGAL_DATABASE_URL") else None
            _inspect(entries, adapter=adapter, batch_id=batch_id)
        else:
            if batch_id != "001":
                raise BatchError("BATCH_NOT_ENABLED_FOR_PUBLICATION")
            _embedding_configured()
            _publish(entries, _adapter())
    except BatchError as exc:
        print(f"ERROR={exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"ERROR={type(exc).__name__}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
