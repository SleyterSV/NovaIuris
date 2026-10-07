"""Server-side, transactional PostgreSQL publication for staged V2 material.

No connection is created on import. The caller supplies a DB-API connection
factory; a single connection/transaction owns each document and its audit run.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import json
import math
import re
from uuid import UUID, uuid4, uuid5


@dataclass(frozen=True)
class LegalRelation:
    source_sequence: int
    relation_type: str
    target_sequence: int | None = None
    target_document_id: str | None = None
    citation_text: str | None = None
    metadata: dict = field(default_factory=dict)


@dataclass(frozen=True)
class PublicationResult:
    document_id: str
    run_id: str
    documents_created: int
    units_created: int
    relations_created: int
    duplicates_skipped: int


DOCUMENT_COLUMNS = ("id", "ingestion_run_id", "document_hash", "title", "document_type",
                    "rama", "hierarchy", "issuer", "court", "chamber", "number",
                    "expediente", "resolution_type", "publication_date", "resolution_date",
                    "valid_from", "valid_to", "status", "precedent_binding", "materia",
                    "instancia", "ponente", "sumilla", "official_url", "source_file_name",
                    "source_format", "parser_version", "ingestion_status", "extraction_quality",
                    "ocr_required", "metadata")
UNIT_COLUMNS = ("id", "document_id", "parent_unit_id", "unit_type", "unit_number",
                "heading", "sequence", "part_number", "part_count", "book", "section",
                "title", "chapter", "page_start", "page_end", "text", "normalized_text",
                "excerpt", "search_text", "is_current", "valid_from", "valid_to",
                "content_hash", "token_count", "embedding", "metadata")
RELATION_COLUMNS = ("id", "source_unit_id", "target_unit_id", "target_document_id",
                    "relation_type", "citation_text", "metadata")
RELATION_TYPES = {"CITES", "MODIFIES", "REPEALS", "SUPERSEDES", "INTERPRETS",
                  "CONCORDANT_WITH", "REFERENCES"}


def _insert_sql(table, columns, *, vector=False):
    placeholders = ["%s"] * len(columns)
    if "metadata" in columns:
        placeholders[columns.index("metadata")] = "%s::jsonb"
    if vector:
        placeholders[columns.index("embedding")] = "%s::extensions.vector"
    return f"insert into public.{table} ({', '.join(columns)}) values ({', '.join(placeholders)})"


def _insert_batch(cursor, table, columns, rows, *, vector=False):
    if not rows:
        return
    single = _insert_sql(table, columns, vector=vector)
    values = single.split(" values ", 1)[1]
    sql = single.split(" values ", 1)[0] + " values " + ", ".join([values] * len(rows))
    cursor.execute(sql, tuple(row[key] for row in rows for key in columns))


def _vector(value):
    if value is None:
        return None
    if len(value) != 1536 or any(isinstance(x, bool) or not isinstance(x, (float, int))
                                 or not math.isfinite(x) for x in value):
        raise ValueError("Each publishable unit needs a 1536-dimensional numeric embedding")
    return "[" + ",".join(str(float(x)) for x in value) + "]"


class PublicationAdapter:
    def __init__(self, connection_factory, *, batch_size=100):
        if batch_size < 1:
            raise ValueError("batch_size must be positive")
        self.connection_factory = connection_factory
        self.batch_size = batch_size

    def prepare(self, document, *, embeddings=None, relations=()):
        """Map offline. None embeddings are legal here, but not in publish()."""
        if document.ingestion_status == "review_required" or document.ocr_required:
            raise ValueError("Review-required or OCR material cannot be published")
        if document.ingestion_status != "staged":
            raise ValueError("Only quality-gated staged documents can be published")
        if not document.document_id:
            raise ValueError("Missing stable document identity")
        if not document.metadata.get("source_file_hash") or not document.metadata.get("parser_name"):
            raise ValueError("Missing source hash or parser audit metadata")
        if embeddings is not None and len(embeddings) != len(document.units):
            raise ValueError("Embedding count does not match unit count")
        if len({u.content_hash for u in document.units}) != len(document.units):
            raise ValueError("Unresolved duplicate content hashes")
        if [u.sequence for u in document.units] != list(range(1, len(document.units) + 1)):
            raise ValueError("Unit sequence must be contiguous")
        run_id = str(uuid4())
        doc_id = str(UUID(document.document_id))
        m = document.metadata
        row = {"id": doc_id, "ingestion_run_id": run_id, "document_hash": document.document_hash,
               "title": document.title, "document_type": document.document_type,
               "rama": m.get("rama"), "hierarchy": m.get("hierarchy"), "issuer": m.get("issuer"),
               "court": m.get("court"), "chamber": m.get("chamber"), "number": m.get("number"),
               "expediente": m.get("expediente"), "resolution_type": m.get("resolution_type"),
               "publication_date": m.get("publication_date"), "resolution_date": m.get("resolution_date"),
               "valid_from": m.get("valid_from"), "valid_to": m.get("valid_to"),
               "status": m.get("status", "unknown"), "precedent_binding": m.get("precedent_binding"),
               "materia": m.get("materia"), "instancia": m.get("instancia"), "ponente": m.get("ponente"),
               "sumilla": m.get("sumilla"), "official_url": m.get("official_url"),
               "source_file_name": document.source_file_name, "source_format": document.source_format,
               "parser_version": document.parser_version, "ingestion_status": "processing",
               "extraction_quality": document.extraction_quality, "ocr_required": document.ocr_required,
               "metadata": json.dumps(m, ensure_ascii=False)}
        unit_ids = {u.sequence: str(uuid5(UUID(doc_id), u.content_hash)) for u in document.units}
        unit_rows = []
        for index, unit in enumerate(document.units):
            vector = _vector(embeddings[index]) if embeddings is not None else None
            unit_rows.append({"id": unit_ids[unit.sequence], "document_id": doc_id,
                "parent_unit_id": unit_ids.get(unit.parent_sequence), "unit_type": unit.unit_type,
                "unit_number": unit.unit_number, "heading": unit.heading, "sequence": unit.sequence,
                "part_number": unit.part_number, "part_count": unit.part_count, "book": unit.book,
                "section": unit.section, "title": unit.title, "chapter": unit.chapter,
                "page_start": unit.page_start, "page_end": unit.page_end, "text": unit.text,
                "normalized_text": unit.normalized_text, "excerpt": unit.excerpt,
                "search_text": unit.search_text, "is_current": unit.metadata.get("is_current", True),
                "valid_from": unit.metadata.get("valid_from"), "valid_to": unit.metadata.get("valid_to"),
                "content_hash": unit.content_hash, "token_count": unit.token_count,
                "embedding": vector, "metadata": json.dumps(unit.metadata, ensure_ascii=False)})
        relation_rows = []
        for relation in relations:
            if relation.relation_type not in RELATION_TYPES or relation.source_sequence not in unit_ids:
                raise ValueError("Invalid explicit legal relation")
            if relation.target_sequence is not None and relation.target_sequence not in unit_ids:
                raise ValueError("Relation target sequence is absent")
            targets = sum(x is not None for x in (relation.target_sequence,
                                                  relation.target_document_id, relation.citation_text))
            if targets == 0 or (relation.target_sequence is not None and relation.target_document_id is not None):
                raise ValueError("Relation needs one target or citation")
            relation_rows.append({"id": str(uuid4()), "source_unit_id": unit_ids[relation.source_sequence],
                "target_unit_id": unit_ids.get(relation.target_sequence),
                "target_document_id": relation.target_document_id,
                "relation_type": relation.relation_type, "citation_text": relation.citation_text,
                "metadata": json.dumps(relation.metadata, ensure_ascii=False)})
        return row, unit_rows, relation_rows

    def publish(self, document, *, embeddings, relations=()):
        doc_row, unit_rows, relation_rows = self.prepare(document, embeddings=embeddings, relations=relations)
        if not unit_rows or any(row["embedding"] is None for row in unit_rows):
            raise ValueError("Final publication requires 1536-dimensional embeddings for every unit")
        run_id = doc_row["ingestion_run_id"]
        connection = self.connection_factory()
        try:
            cursor = connection.cursor()
            cursor.execute("select pg_advisory_xact_lock(hashtextextended(%s, 0))",
                           (document.document_hash + ":" + document.parser_version,))
            cursor.execute("select id, ingestion_status from public.legal_documents where document_hash = %s and parser_version = %s",
                           (document.document_hash, document.parser_version))
            existing = cursor.fetchone()
            cursor.execute("insert into public.legal_ingestion_runs (id, source_file_name, source_file_hash, parser_name, parser_version, status, warnings_count, summary) values (%s,%s,%s,%s,%s,'processing',%s,%s::jsonb)",
                           (run_id, document.source_file_name, document.metadata["source_file_hash"],
                            document.metadata["parser_name"], document.parser_version,
                            len(document.warnings), json.dumps({"warnings": document.warnings}, ensure_ascii=False)))
            if existing:
                if existing[1] not in {"ready", "ready_with_warnings"}:
                    raise RuntimeError("Existing document version is incomplete; manual reconciliation required")
                cursor.execute("update public.legal_ingestion_runs set status='completed', completed_at=now(), duplicates_skipped=1 where id=%s", (run_id,))
                connection.commit()
                return PublicationResult(str(existing[0]), run_id, 0, 0, 0, 1)
            cursor.execute(_insert_sql("legal_documents", DOCUMENT_COLUMNS),
                           tuple(doc_row[key] for key in DOCUMENT_COLUMNS))
            for start in range(0, len(unit_rows), self.batch_size):
                batch = unit_rows[start:start + self.batch_size]
                _insert_batch(cursor, "legal_units", UNIT_COLUMNS, batch, vector=True)
            for start in range(0, len(relation_rows), self.batch_size):
                batch = relation_rows[start:start + self.batch_size]
                _insert_batch(cursor, "legal_relations", RELATION_COLUMNS, batch)
            cursor.execute("update public.legal_documents set ingestion_status='ready', updated_at=now() where id=%s", (doc_row["id"],))
            cursor.execute("update public.legal_ingestion_runs set status='completed', completed_at=now(), documents_created=1, units_created=%s, relations_created=%s where id=%s",
                           (len(unit_rows), len(relation_rows), run_id))
            connection.commit()
            return PublicationResult(doc_row["id"], run_id, 1, len(unit_rows), len(relation_rows), 0)
        except Exception as exc:
            connection.rollback()
            # A failed attempt is audited separately; the document, units and
            # relations from the rolled-back transaction cannot appear ready.
            try:
                cursor = connection.cursor()
                cursor.execute("insert into public.legal_ingestion_runs (id, source_file_name, source_file_hash, parser_name, parser_version, status, completed_at, errors_count, warnings_count, summary) values (%s,%s,%s,%s,%s,'failed',now(),1,%s,%s::jsonb)",
                               (run_id, document.source_file_name, document.metadata["source_file_hash"],
                                document.metadata["parser_name"], document.parser_version,
                                len(document.warnings), json.dumps({"error_type": type(exc).__name__,
                                "error_message": re.sub(r"(?i)(password|token|api[_-]?key)\s*[=:]\s*\S+",
                                                        r"\1=[REDACTED]", str(exc).splitlines()[0])[:240],
                                "units_attempted": len(unit_rows), "relations_attempted": len(relation_rows)}, ensure_ascii=False)))
                connection.commit()
            except Exception:
                connection.rollback()
            raise
        finally:
            connection.close()


def postgres_connection_factory(dsn):
    """Construct a server-only connection factory; opening happens at publish()."""
    if not dsn:
        raise ValueError("A server-side PostgreSQL DSN is required")
    def connect():
        import psycopg2
        return psycopg2.connect(dsn)
    return connect
