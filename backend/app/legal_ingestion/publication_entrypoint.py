"""Manual, two-document V2 publication CLI. Importing this module has no I/O."""
from __future__ import annotations

import argparse
from collections import Counter
from contextlib import contextmanager
import json
import os
from pathlib import Path
import sys

from .service import stage_file
from .units import embedding_batches

from .publication import PublicationAdapter, _vector, postgres_connection_factory

PROJECT_REF = "emelxkoztshmzukydqzj"
MODEL = "text-embedding-3-small"
DIMENSION = 1536
SEARCH_COLUMNS = ("unit_id", "document_id", "document_title", "document_type",
                  "unit_type", "unit_number", "heading", "excerpt", "page_start",
                  "page_end", "similarity", "lexical_score", "official_url")
ROOT = Path(__file__).resolve().parents[3]
PILOT = {
    "decree": ("raw_docs/LEY DEL PROCEDIMIENTO ADMINISTRATIVO GENERAL.docx",
               "promulgating_instrument", "4d4b33500e017cf5055e50a5812ea13cba25209310c85d99e5a85b076cf2b65a", 5),
    "auto": ("backend/raw_docs/jurisprudencia/_Auto__No_todos_los_casos_que_conozca_el_TC__vía_RAC____.pdf",
             None, "0c2a1e064a9929036b002bd0b5e555f8959143c5399fba62c3e8335ecce76988", 10),
}


class PilotError(RuntimeError):
    """A fixed, safe error code; provider and database exceptions stay private."""


def _dsn():
    dsn = os.environ.get("MYKE_LEGAL_DATABASE_URL")
    if not dsn:
        raise PilotError("DATABASE_NOT_CONFIGURED")
    # A Supabase direct host contains the ref; a pooler embeds it in the user.
    try:
        from psycopg2.extensions import parse_dsn
        parts = parse_dsn(dsn)
    except Exception as exc:
        raise PilotError("DATABASE_DSN_INVALID") from exc
    if PROJECT_REF not in parts.get("host", "") and PROJECT_REF not in parts.get("user", ""):
        raise PilotError("DATABASE_TARGET_UNVERIFIED")
    return dsn


def _embedding_configured():
    if not os.environ.get("OPENAI_API_KEY"):
        raise PilotError("EMBEDDING_PROVIDER_NOT_CONFIGURED")
    if os.environ.get("OPENAI_EMBEDDING_MODEL", MODEL) != MODEL:
        raise PilotError("EMBEDDING_MODEL_MISMATCH")
    # The existing provider imports dotenv; pin this process before that import.
    os.environ.setdefault("OPENAI_EMBEDDING_MODEL", MODEL)


def _stage(which):
    source, segment, expected_hash, expected_units = PILOT[which]
    document = stage_file(ROOT / source, segment=segment)
    if (document.ingestion_status != "staged" or document.ocr_required or
            document.document_hash != expected_hash or len(document.units) != expected_units):
        raise PilotError("PILOT_QUALITY_OR_IDENTITY_CHANGED")
    if which == "decree" and (document.document_type != "regulation" or
                              document.metadata.get("number") != "006-2026-JUS"):
        raise PilotError("PILOT_IDENTITY_CHANGED")
    if which == "auto" and (document.document_type != "order" or
                            document.metadata.get("expediente") != "04810-2024-PA/TC"):
        raise PilotError("PILOT_IDENTITY_CHANGED")
    return document


@contextmanager
def _database(adapter, *, read_only=False):
    connection = adapter.connection_factory()
    try:
        if connection.autocommit:
            raise PilotError("DATABASE_AUTOCOMMIT_FORBIDDEN")
        if read_only:
            connection.set_session(readonly=True)
        cursor = connection.cursor()
        cursor.execute("""select
            to_regclass('public.legal_documents') is not null,
            to_regclass('public.legal_units') is not null,
            to_regclass('public.legal_relations') is not null,
            to_regclass('public.legal_ingestion_runs') is not null,
            exists (select 1 from pg_proc p join pg_namespace n on n.oid=p.pronamespace
                    where n.nspname='public' and p.proname='match_legal_knowledge_v2'),
            exists (select 1 from pg_extension where extname='vector')""")
        if cursor.fetchone() != (True,) * 6:
            raise PilotError("DATABASE_V2_SCHEMA_MISSING")
        yield connection, cursor
    finally:
        connection.rollback()  # all CLI reads remain read-only
        connection.close()


def _counts(cursor):
    cursor.execute("""select
        (select count(*) from public.legal_documents),
        (select count(*) from public.legal_units),
        (select count(*) from public.legal_relations),
        (select count(*) from public.legal_ingestion_runs)""")
    return cursor.fetchone()


def _identity(cursor, document, adapter):
    """Read-only comparison with exact unit identities; never creates a retry run."""
    expected, expected_units, _ = adapter.prepare(document)
    cursor.execute("""select d.id, d.title, d.document_type, d.number, d.expediente,
                          d.ingestion_status, r.status
                   from public.legal_documents d
                   left join public.legal_ingestion_runs r on r.id=d.ingestion_run_id
                   where d.document_hash=%s and d.parser_version=%s""",
                   (document.document_hash, document.parser_version))
    found = cursor.fetchall()
    if not found:
        return "NOT_PRESENT"
    if len(found) != 1:
        return "CONFLICT"
    row = found[0]
    if (str(row[0]), row[1], row[2], row[3], row[4]) != (
            expected["id"], expected["title"], expected["document_type"],
            expected["number"], expected["expediente"]):
        return "CONFLICT"
    if row[5] not in {"ready", "ready_with_warnings"} or row[6] != "completed":
        return "CONFLICT"
    cursor.execute("""select id, sequence, content_hash, unit_type, unit_number,
                          page_start, page_end, extensions.vector_dims(embedding)
                   from public.legal_units where document_id=%s order by sequence""",
                   (expected["id"],))
    actual_units = cursor.fetchall()
    if len(actual_units) != len(expected_units):
        return "CONFLICT"
    for actual, unit in zip(actual_units, expected_units):
        if (str(actual[0]), *actual[1:7], actual[7]) != (
                unit["id"], unit["sequence"], unit["content_hash"], unit["unit_type"],
                unit["unit_number"], unit["page_start"], unit["page_end"], DIMENSION):
            return "CONFLICT"
    return "ALREADY_PRESENT_AND_IDENTICAL"


def _inspect(which):
    document = _stage(which)
    types = ",".join(f"{key}:{count}" for key, count in
                     sorted(Counter(unit.unit_type for unit in document.units).items()))
    identity = document.metadata.get("number") or document.metadata.get("expediente")
    print(f"DOCUMENT={which} IDENTITY={identity} STATUS=PUBLISHABLE TYPE={document.document_type} "
          f"UNITS={len(document.units)} UNIT_TYPES={types} HASH={document.document_hash[:12]} "
          f"REVIEW_REQUIRED=false OCR_REQUIRED=false WARNINGS={','.join(document.warnings) or 'none'}")


def _search(args):
    query = args.query.strip()
    if not query:
        raise PilotError("SEARCH_QUERY_EMPTY")
    if not 1 <= args.top_k <= 50:
        raise PilotError("SEARCH_TOP_K_INVALID")
    _dsn()
    _embedding_configured()
    from app.services.embedding_service import EmbeddingService
    provider = EmbeddingService()
    if provider.MODEL != MODEL:
        raise PilotError("EMBEDDING_MODEL_MISMATCH")
    vector = _vector(provider.generate_embedding(query))
    adapter = configured_publication_adapter()
    with _database(adapter, read_only=True) as (_, cursor):
        cursor.execute("""select unit_id, document_id, document_title, document_type,
                              unit_type, unit_number, heading, excerpt, page_start,
                              page_end, similarity, lexical_score, official_url
                       from public.match_legal_knowledge_v2(
                           query_embedding => %s::extensions.vector(1536),
                           query_text => %s, match_count => %s,
                           filter_document_type => %s, filter_rama => %s,
                           filter_expediente => %s)""",
                       (vector, query, args.top_k, args.document_type,
                        args.rama, args.expediente))
        rows = cursor.fetchall()
    results = []
    for rank, row in enumerate(rows, 1):
        if len(row) != len(SEARCH_COLUMNS):
            raise PilotError("SEARCH_RESULT_SHAPE_INVALID")
        result = dict(zip(SEARCH_COLUMNS, row))
        result["rank"] = rank
        result["unit_id"] = str(result["unit_id"])
        result["document_id"] = str(result["document_id"])
        result["excerpt"] = (result["excerpt"] or "")[:240]
        results.append(result)
    if args.json:
        print(json.dumps({"model": MODEL, "dimension": DIMENSION, "results": results},
                         ensure_ascii=False, allow_nan=False))
    else:
        print(f"MODEL={MODEL} DIMENSION={DIMENSION} RESULTS={len(results)}")
        for result in results:
            print(" ".join(f"{key.upper()}={json.dumps(result[key], ensure_ascii=False)}"
                           for key in ("rank", *SEARCH_COLUMNS)))


def _run(command, which=None):
    if command == "inspect":
        _inspect(which)
        return
    _dsn()
    if command in {"preflight", "publish"}:
        _embedding_configured()
    if command == "preflight":
        decree, auto = _stage("decree"), _stage("auto")
    elif command != "counts":
        document = _stage(which)
    adapter = configured_publication_adapter()
    if command == "preflight":
        with _database(adapter) as (_, cursor):
            counts = _counts(cursor)
        if counts != (0, 0, 0, 0):
            raise PilotError("DATABASE_NOT_EMPTY")
        print("DATABASE_CONFIGURED=true EMBEDDING_PROVIDER_CONFIGURED=true "
              f"PROJECT_REF={PROJECT_REF} MODEL={MODEL} DIMENSION={DIMENSION}")
        print(f"DECREE=PUBLISHABLE UNITS={len(decree.units)} AUTO=PUBLISHABLE UNITS={len(auto.units)}")
        print("COUNTS=" + "/".join(map(str, counts)) + " READY=true")
        return
    with _database(adapter) as (_, cursor):
        if command == "counts":
            values = _counts(cursor)
            for key, value in zip(("legal_documents", "legal_units", "legal_relations", "legal_ingestion_runs"), values):
                print(f"{key}={value}")
            return
        state = _identity(cursor, document, adapter)
    if command == "idempotency-check":
        print(f"DOCUMENT={which} IDEMPOTENCY={state}")
        return
    if state != "NOT_PRESENT":
        raise PilotError("DOCUMENT_ALREADY_PRESENT" if state == "ALREADY_PRESENT_AND_IDENTICAL" else "DOCUMENT_CONFLICT")
    # Only a quality-gated, absent, allowlisted document reaches the provider.
    from app.services.embedding_service import EmbeddingService
    provider = EmbeddingService()
    if provider.MODEL != MODEL:
        raise PilotError("EMBEDDING_MODEL_MISMATCH")
    vectors = embedding_batches(document.units, provider.generate_embeddings)
    adapter.prepare(document, embeddings=vectors)  # validates finite 1536-vectors before I/O
    if len(vectors) != len(document.units):
        raise PilotError("EMBEDDING_COUNT_MISMATCH")
    print(f"PREPUBLICATION DOCUMENT={which} UNITS={len(document.units)} EMBEDDINGS={len(vectors)}")
    result = adapter.publish(document, embeddings=vectors, relations=())
    status = "ALREADY_PRESENT" if result.duplicates_skipped else "COMPLETED"
    print(f"PUBLICATION DOCUMENT={which} STATUS={status} DOCUMENTS_CREATED={result.documents_created} "
          f"UNITS_CREATED={result.units_created} RELATIONS_CREATED={result.relations_created} "
          f"DUPLICATES_SKIPPED={result.duplicates_skipped} DOCUMENT_ID={result.document_id} RUN_ID={result.run_id}")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Allowlisted manual Legal Knowledge V2 pilot")
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("preflight", "counts"):
        commands.add_parser(name)
    for name in ("inspect", "publish", "idempotency-check"):
        commands.add_parser(name).add_argument("document", choices=tuple(PILOT))
    search = commands.add_parser("search")
    search.add_argument("query")
    search.add_argument("--top-k", type=int, default=5)
    search.add_argument("--document-type", choices=("regulation", "order"))
    search.add_argument("--rama")
    search.add_argument("--expediente")
    search.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.command == "search":
            _search(args)
        else:
            _run(args.command, getattr(args, "document", None))
    except PilotError as exc:
        print(f"ERROR={exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"ERROR={type(exc).__name__}", file=sys.stderr)
        return 1
    return 0


def configured_publication_adapter(*, batch_size: int = 100) -> PublicationAdapter:
    """Read the pilot DSN without opening a connection or exposing its value."""
    dsn = os.environ.get("MYKE_LEGAL_DATABASE_URL")
    if not dsn:
        raise RuntimeError("MYKE_LEGAL_DATABASE_URL is required for V2 publication")
    return PublicationAdapter(postgres_connection_factory(dsn), batch_size=batch_size)


if __name__ == "__main__":
    raise SystemExit(main())
