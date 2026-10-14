"""Read-only MYKE Legal V2 unit retrieval for NovaSearch and the CLI probe."""

from uuid import UUID

from app.legal_ingestion.publication import _vector, postgres_connection_factory
from app.legal_ingestion.publication_entrypoint import _dsn
from app.services.legal_repository import LegalSearchError


SEARCH_COLUMNS = (
    "unit_id", "document_id", "document_title", "document_type", "unit_type",
    "unit_number", "heading", "excerpt", "page_start", "page_end",
    "similarity", "lexical_score", "official_url",
)

SEARCH_SQL = """select unit_id, document_id, document_title, document_type,
                       unit_type, unit_number, heading, excerpt, page_start,
                       page_end, similarity, lexical_score, official_url
                from public.match_legal_knowledge_v2(
                    query_embedding => %s::extensions.vector(1536),
                    query_text => %s, match_count => %s,
                    filter_document_type => %s, filter_rama => %s,
                    filter_expediente => %s)"""

DOCUMENT_METADATA_COLUMNS = (
    "id", "short_title", "number", "expediente", "court", "chamber",
    "materia", "sumilla", "issuer", "resolution_type", "rama",
)
DOCUMENT_METADATA_SQL = """select id, short_title, number, expediente, court, chamber,
                                  materia, sumilla, issuer, resolution_type, rama
                           from public.legal_documents where id = any(%s::uuid[])"""

UNIT_DETAIL_COLUMNS = (
    "unit_id", "document_id", "text", "unit_type", "unit_number", "heading",
    "page_start", "page_end", "document_title", "document_type", "short_title",
    "number", "expediente", "court", "chamber", "issuer", "official_url",
    "resolution_type", "materia", "sumilla",
)
UNIT_DETAIL_SQL = """select u.id, d.id, u.text, u.unit_type, u.unit_number, u.heading,
                            u.page_start, u.page_end, d.title, d.document_type,
                            d.short_title, d.number, d.expediente, d.court, d.chamber,
                            d.issuer, d.official_url, d.resolution_type, d.materia, d.sumilla
                     from public.legal_units u
                     join public.legal_documents d on d.id = u.document_id
                     where u.id = %s::uuid and u.is_current
                       and d.ingestion_status in ('ready', 'ready_with_warnings')"""

EXACT_UNIT_SQL = """select u.id, d.id, u.text, u.unit_type, u.unit_number, u.heading,
                           u.page_start, u.page_end, d.title, d.document_type,
                           d.short_title, d.number, d.expediente, d.court, d.chamber,
                           d.issuer, d.official_url, d.resolution_type, d.materia, d.sumilla
                    from public.legal_units u
                    join public.legal_documents d on d.id = u.document_id
                    where d.expediente = %s and u.unit_type = %s
                      and u.is_current
                      and d.ingestion_status in ('ready', 'ready_with_warnings')"""


def search_cursor(cursor, *, embedding, query_text, match_count=20,
                  filter_document_type=None, filter_rama=None, filter_expediente=None):
    """Execute the single V2 RPC query; keep the database's hybrid rank order."""
    if not isinstance(query_text, str) or not query_text.strip():
        raise ValueError("SEARCH_QUERY_EMPTY")
    if isinstance(match_count, bool) or not isinstance(match_count, int) or not 1 <= match_count <= 50:
        raise ValueError("SEARCH_TOP_K_INVALID")
    for value in (filter_document_type, filter_rama, filter_expediente):
        if value is not None and (not isinstance(value, str) or not value.strip()):
            raise ValueError("SEARCH_FILTER_INVALID")
    cursor.execute(SEARCH_SQL, (_vector(embedding), query_text.strip(), match_count,
                                filter_document_type, filter_rama, filter_expediente))
    results = []
    for row in cursor.fetchall():
        if len(row) != len(SEARCH_COLUMNS):
            raise ValueError("SEARCH_RESULT_SHAPE_INVALID")
        result = dict(zip(SEARCH_COLUMNS, row))
        result["unit_id"] = str(result["unit_id"])
        result["document_id"] = str(result["document_id"])
        results.append(result)
    return results


def display_title(row):
    """Use verified document metadata; keep the editorial title as fallback."""
    kind = row["document_type"]
    number = row.get("number")
    expediente = row.get("expediente")
    if kind == "cassation" and (number or expediente):
        return f"Casación {number or expediente}"
    if kind == "regulation" and number and "decreto supremo" in (row.get("resolution_type") or "").casefold():
        return f"Decreto Supremo N.º {number}"
    if kind == "judgment" and expediente:
        court = (row.get("court") or "").casefold()
        return f"STC Exp. {expediente}" if "tribunal constitucional" in court else f"Sentencia Exp. {expediente}"
    if kind == "order" and expediente:
        return f"Auto Exp. {expediente}"
    return row.get("short_title") or row["document_title"]


def map_runtime_unit(row):
    """Adapt a V2 unit to the existing NovaSearch document contract without invented data."""
    unit_type = row["unit_type"]
    unit_number = row.get("unit_number")
    source_type = "legislation" if row["document_type"] in {"regulation", "statute", "law"} else "jurisprudence"
    title = display_title(row)
    return {
        "id": row["unit_id"], "unit_id": row["unit_id"],
        "document_id": row["document_id"], "chunk_id": row["unit_id"],
        "titulo": title, "fuente": row["document_title"],
        "tipo_documento": row["document_type"], "source_type": source_type,
        "unit_type": unit_type, "unit_number": unit_number,
        "heading": row.get("heading"), "texto": row.get("excerpt") or "",
        "section": row.get("heading"),
        "expediente": row.get("expediente"), "numero": row.get("number"),
        "court": row.get("court"), "chamber": row.get("chamber"),
        "organo_emisor": row.get("court") or row.get("issuer"),
        "materia": row.get("materia"), "sumilla": row.get("sumilla"),
        "rama": row.get("rama"), "resolution_type": row.get("resolution_type"),
        "articulo": f"Artículo {unit_number}" if unit_type == "article" and unit_number else None,
        "fundamento": f"Fundamento {unit_number}" if unit_type == "foundation" and unit_number else None,
        "page_start": row.get("page_start"), "page_end": row.get("page_end"),
        "official_url": row.get("official_url"),
        "similarity": row.get("similarity"), "lexical_score": row.get("lexical_score"),
        "metadata": {"unit_type": unit_type, "unit_number": unit_number,
                     "document_type": row["document_type"],
                     "heading": row.get("heading"), "lexical_score": row.get("lexical_score"),
                     "editorial_title": row["document_title"],
                     "chamber": row.get("chamber"), "resolution_type": row.get("resolution_type")},
    }


class LegalRepositoryV2:
    """Use only the verified MYKE Legal DSN; never fall back to V1/Fiscal.IA."""

    def __init__(self, connection_factory=None):
        try:
            self.connection_factory = connection_factory or postgres_connection_factory(_dsn())
        except Exception as error:
            raise LegalSearchError("MYKE Legal V2 is unavailable") from error

    def search(self, *, embedding, query_text, match_count=20,
               filter_document_type=None, filter_rama=None, filter_expediente=None):
        connection = None
        try:
            connection = self.connection_factory()
            if connection.autocommit:
                raise ValueError("DATABASE_AUTOCOMMIT_FORBIDDEN")
            connection.set_session(readonly=True)
            cursor = connection.cursor()
            rows = search_cursor(cursor, embedding=embedding, query_text=query_text,
                                 match_count=match_count, filter_document_type=filter_document_type,
                                 filter_rama=filter_rama, filter_expediente=filter_expediente)
            if rows:
                document_ids = list(dict.fromkeys(row["document_id"] for row in rows))
                cursor.execute(DOCUMENT_METADATA_SQL, (document_ids,))
                metadata = {}
                for values in cursor.fetchall():
                    if len(values) != len(DOCUMENT_METADATA_COLUMNS):
                        raise ValueError("DOCUMENT_METADATA_SHAPE_INVALID")
                    document = dict(zip(DOCUMENT_METADATA_COLUMNS, values))
                    metadata[str(document["id"])] = document
                for row in rows:
                    row.update(metadata.get(row["document_id"], {}))
                if filter_expediente and any(row.get("expediente") != filter_expediente for row in rows):
                    raise ValueError("EXACT_CASE_IDENTITY_MISMATCH")
            return [map_runtime_unit(row) for row in rows]
        except Exception as error:
            raise LegalSearchError("MYKE Legal V2 search failed") from error
        finally:
            if connection is not None:
                connection.rollback()
                connection.close()

    def get_unit(self, unit_id, *, document_id=None):
        """Fetch only one published, current canonical legal unit; no vector or corpus write."""
        identifier = str(UUID(str(unit_id)))
        expected_document = str(UUID(str(document_id))) if document_id is not None else None
        connection = None
        try:
            connection = self.connection_factory()
            if connection.autocommit:
                raise ValueError("DATABASE_AUTOCOMMIT_FORBIDDEN")
            connection.set_session(readonly=True)
            cursor = connection.cursor()
            sql = UNIT_DETAIL_SQL + (" and d.id = %s::uuid" if expected_document else "")
            params = (identifier, expected_document) if expected_document else (identifier,)
            cursor.execute(sql, params)
            row = cursor.fetchone()
            if row is None:
                return None
            if len(row) != len(UNIT_DETAIL_COLUMNS):
                raise ValueError("UNIT_DETAIL_SHAPE_INVALID")
            detail = dict(zip(UNIT_DETAIL_COLUMNS, row))
            detail["unit_id"] = str(detail["unit_id"])
            detail["document_id"] = str(detail["document_id"])
            detail["display_title"] = display_title(detail)
            return detail
        except Exception as error:
            raise LegalSearchError("MYKE Legal V2 unit detail failed") from error
        finally:
            if connection is not None:
                connection.rollback()
                connection.close()

    def find_exact_unit(self, expediente, unit_type, unit_number=None):
        """Resolve a published unit by verified case identity, independent of vector rank."""
        if not isinstance(expediente, str) or not expediente.strip() or unit_type not in {
                "foundation", "article", "decision", "separate_opinion"}:
            raise ValueError("EXACT_UNIT_FILTER_INVALID")
        if unit_type in {"foundation", "article"} and not (str(unit_number or "").isdigit()):
            raise ValueError("EXACT_UNIT_NUMBER_INVALID")
        connection = None
        try:
            connection = self.connection_factory()
            if connection.autocommit:
                raise ValueError("DATABASE_AUTOCOMMIT_FORBIDDEN")
            connection.set_session(readonly=True)
            cursor = connection.cursor()
            sql = EXACT_UNIT_SQL
            params = [expediente, unit_type]
            if unit_number is not None:
                sql += " and u.unit_number = %s"
                params.append(str(unit_number))
            sql += " order by u.sequence, u.id limit 2"
            cursor.execute(sql, tuple(params))
            rows = cursor.fetchall()
            if not rows:
                return None
            if unit_number is not None and len(rows) != 1:
                raise ValueError("AMBIGUOUS_EXACT_UNIT")
            if any(len(row) != len(UNIT_DETAIL_COLUMNS) for row in rows):
                raise ValueError("UNIT_DETAIL_SHAPE_INVALID")
            detail = dict(zip(UNIT_DETAIL_COLUMNS, rows[0]))
            if detail["expediente"] != expediente or detail["unit_type"] != unit_type or (
                    unit_number is not None and detail["unit_number"] != str(unit_number)):
                raise ValueError("EXACT_UNIT_IDENTITY_MISMATCH")
            detail["unit_id"] = str(detail["unit_id"])
            detail["document_id"] = str(detail["document_id"])
            mapped = map_runtime_unit({**detail, "excerpt": detail["text"][:240],
                                       "similarity": None, "lexical_score": None})
            mapped["canonical_text"] = detail["text"]
            return mapped
        except Exception as error:
            raise LegalSearchError("MYKE Legal V2 exact unit failed") from error
        finally:
            if connection is not None:
                connection.rollback()
                connection.close()
