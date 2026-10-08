"""Manifest-bound, resumable V2 batch CLI. Importing has no provider or DB I/O."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys

from .corpus_audit import ROOT, OUTPUT as QUALIFICATION
from .publication import PublicationAdapter, postgres_connection_factory
from .publication_entrypoint import (_database, _dsn, _embedding_configured,
                                     _identity, MODEL)
from .service import stage_file
from .units import embedding_batches


MANIFEST = ROOT / "docs/LEGAL_KNOWLEDGE_V2_BATCH_001.json"


class BatchError(RuntimeError):
    """Safe public error code; underlying provider/SQL errors remain private."""


def _load_manifest(path: str) -> list[dict]:
    if Path(path).resolve() != MANIFEST.resolve():
        raise BatchError("UNAPPROVED_MANIFEST_PATH")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    entries = manifest.get("documents")
    if manifest.get("batch_id") != "001" or not isinstance(entries, list) or not 1 <= len(entries) <= 30:
        raise BatchError("MANIFEST_INVALID")
    qualification = json.loads(QUALIFICATION.read_text(encoding="utf-8"))
    approved = {row["source_path"]: row for row in qualification["records"]
                if row["category"] == "PUBLISHABLE"}
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
    document = stage_file(source)
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


def _inspect(entries, *, adapter=None):
    for index, entry in enumerate(entries, 1):
        document = _stage_entry(entry)
        state = _presence(adapter, document) if adapter is not None else "UNVERIFIED_OFFLINE"
        print(f"BATCH=001 ITEM={index} ID={document.document_id} STATUS=PUBLISHABLE "
              f"TYPE={document.document_type} UNITS={len(document.units)} "
              f"EMBEDDINGS_REQUIRED={0 if state == 'ALREADY_PRESENT_AND_IDENTICAL' else len(document.units)} "
              f"HASH={document.document_hash[:12]} PRESENCE={state}")
        if state == "CONFLICT":
            raise BatchError("DOCUMENT_CONFLICT")


def _publish(entries, adapter):
    # Validate every manifest entry and source before paying for any embedding.
    documents = [_stage_entry(entry) for entry in entries]
    provider = None
    for index, document in enumerate(documents, 1):
        state = _presence(adapter, document)
        if state == "ALREADY_PRESENT_AND_IDENTICAL":
            print(f"BATCH=001 ITEM={index} STATUS=ALREADY_PRESENT_AND_IDENTICAL EMBEDDINGS=0")
            continue
        if state != "NOT_PRESENT":
            raise BatchError("DOCUMENT_CONFLICT")
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
        if result.duplicates_skipped:
            print(f"BATCH=001 ITEM={index} STATUS=ALREADY_PRESENT_AND_IDENTICAL EMBEDDINGS={len(vectors)}")
        else:
            print(f"BATCH=001 ITEM={index} STATUS=COMPLETED UNITS={result.units_created} "
                  f"RELATIONS={result.relations_created} DOCUMENT_ID={result.document_id} "
                  f"RUN_ID={result.run_id}")
        # The next item starts only after PublicationAdapter committed this one.


def main(argv=None):
    parser = argparse.ArgumentParser(description="Approved Legal Knowledge V2 Batch 001")
    commands = parser.add_subparsers(dest="command", required=True)
    for command in ("inspect-batch", "publish-batch"):
        commands.add_parser(command).add_argument("manifest")
    args = parser.parse_args(argv)
    try:
        entries = _load_manifest(args.manifest)
        if args.command == "inspect-batch":
            adapter = _adapter() if os.environ.get("MYKE_LEGAL_DATABASE_URL") else None
            _inspect(entries, adapter=adapter)
        else:
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
