"""Canonical, provenance-preserving source and citation contracts."""

from __future__ import annotations

import hashlib
import json
import re
from copy import deepcopy
from urllib.parse import urlparse


SOURCE_TYPES = {
    "legislation", "article", "jurisprudence", "precedent", "resolution",
    "doctrine", "case_document", "evidence", "contract", "pleading",
    "expert_report", "other",
}
_MARKER = re.compile(r"\[SRC-([A-Za-z0-9_-]{6,80})\]")
_CITATION_ID = re.compile(r"^CIT-[a-f0-9]{24}$")


def _stable_id(prefix: str, *parts: object) -> str:
    value = "\x1f".join(str(part or "") for part in parts)
    return f"{prefix}-{hashlib.sha256(value.encode('utf-8')).hexdigest()[:24]}"


def _value(mapping: dict, *keys):
    for key in keys:
        value = mapping.get(key)
        if value not in (None, "", [], {}):
            return value
    return None


def _official_url(record: dict) -> str | None:
    metadata = record.get("metadata") if isinstance(record.get("metadata"), dict) else {}
    candidate = _value(record, "official_url") or _value(metadata, "official_url")
    if not isinstance(candidate, str):
        return None
    parsed = urlparse(candidate.strip())
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return None
    return candidate.strip()


def _source_type(*values) -> str:
    for value in values:
        if isinstance(value, str) and value.strip().lower() in SOURCE_TYPES:
            return value.strip().lower()
    text = " ".join(str(value or "").lower() for value in values)
    if any(word in text for word in ("jurisprud", "casación", "casacion", "sentencia", "tribunal")):
        return "jurisprudence"
    if "precedente" in text:
        return "precedent"
    if any(word in text for word in ("resolución", "resolucion")):
        return "resolution"
    if any(word in text for word in ("ley", "código", "codigo", "decreto", "constitución", "constitucion")):
        return "legislation"
    return "other"


def normalize_public_source(record: dict, excerpt: str | None = None) -> dict:
    """Normalize a recovered public record without inferring absent metadata."""
    record = record if isinstance(record, dict) else {}
    metadata = deepcopy(record.get("metadata")) if isinstance(record.get("metadata"), dict) else {}
    identifier = _value(record, "id", "record_id", "document_id") or metadata.get("id")
    locator = _value(record, "article", "articulo", "fundamento", "legal_basis")
    exact_excerpt = excerpt if excerpt is not None else str(_value(record, "texto", "text", "excerpt") or "")
    source_id = _stable_id("SRC", "public", identifier, locator,
                          hashlib.sha256(exact_excerpt.encode("utf-8")).hexdigest())
    title = _value(record, "titulo", "title", "articulo", "fuente") or "Fuente jurídica"
    source_type = _source_type(_value(record, "source_type", "tipo_documento"), title, locator)
    return {
        "source_id": source_id,
        "source_scope": "public",
        "source_type": source_type,
        "title": str(title),
        "display_title": str(title),
        "entity": _value(record, "entity", "entidad", "organo_emisor") or metadata.get("entity"),
        "court": _value(record, "court", "tribunal", "instancia") or metadata.get("court"),
        "case_number": _value(record, "case_number", "expediente") or metadata.get("case_number"),
        "document_number": _value(record, "document_number", "numero") or metadata.get("document_number"),
        "article": locator or metadata.get("article"),
        "legal_basis": _value(record, "legal_basis", "fundamento") or metadata.get("legal_basis"),
        "date": _value(record, "date", "fecha", "fecha_resolucion", "fecha_publicacion") or metadata.get("date"),
        "document_id": str(identifier) if identifier is not None else None,
        "case_id": None,
        "chunk_id": _value(record, "chunk_id") or metadata.get("chunk_id"),
        "page_start": _value(record, "page_start", "page"),
        "page_end": _value(record, "page_end"),
        "section": _value(record, "section", "seccion"),
        "paragraph": _value(record, "paragraph", "parrafo"),
        "excerpt": exact_excerpt,
        "official_url": _official_url(record),
        "source_url": _value(record, "source_url") or metadata.get("source_url"),
        "metadata": metadata,
    }


def normalize_case_source(item: dict) -> dict:
    """Normalize one private corpus chunk; identity always includes its case."""
    item = item if isinstance(item, dict) else {}
    ref = item.get("source_reference") if isinstance(item.get("source_reference"), dict) else {}
    case_id = item.get("case_id") or ref.get("case_id")
    document_id = item.get("document_id") or ref.get("document_id")
    chunk_id = item.get("chunk_id") or ref.get("chunk_id")
    if not case_id or not document_id or not chunk_id:
        raise ValueError("Private source requires case_id, document_id and chunk_id")
    locator = ref.get("locator") if isinstance(ref.get("locator"), dict) else {}
    page_start = item.get("page_start", ref.get("page_start", locator.get("page")))
    page_end = item.get("page_end", ref.get("page_end", page_start))
    section = item.get("section") or ref.get("section") or locator.get("section")
    paragraph = item.get("paragraph") or ref.get("paragraph")
    excerpt = str(item.get("text") or item.get("excerpt") or "")
    source_id = _stable_id("SRC", "case", case_id, document_id, chunk_id)
    filename = ref.get("filename") or item.get("filename") or "Documento del expediente"
    return {
        "source_id": source_id, "source_scope": "case", "source_type": "case_document",
        "title": filename, "display_title": filename, "entity": None, "court": None,
        "case_number": None, "document_number": None, "article": ref.get("article"),
        "legal_basis": ref.get("legal_basis"), "date": ref.get("date"),
        "document_id": str(document_id), "case_id": str(case_id), "chunk_id": str(chunk_id),
        "page_start": page_start, "page_end": page_end, "section": section,
        "paragraph": paragraph, "excerpt": excerpt,
        "official_url": None, "metadata": deepcopy(ref.get("metadata", {})) if isinstance(ref.get("metadata"), dict) else {},
    }


def normalize_citation(citation: dict, source: dict) -> dict:
    citation = citation if isinstance(citation, dict) else {}
    source_id = source["source_id"]
    excerpt = str(citation.get("excerpt") if citation.get("excerpt") is not None else source.get("excerpt", ""))
    citation_id = citation.get("citation_id")
    if not isinstance(citation_id, str) or not _CITATION_ID.fullmatch(citation_id):
        citation_id = _stable_id("CIT", source_id, excerpt)
    label = citation.get("label") if isinstance(citation.get("label"), str) else ""
    locator = citation.get("locator") if isinstance(citation.get("locator"), dict) else {}
    locator = {key: value for key, value in {
        "page": locator.get("page", source.get("page_start")),
        "section": locator.get("section", source.get("section")),
        "article": locator.get("article", source.get("article")),
        "paragraph": locator.get("paragraph", source.get("paragraph")),
    }.items() if value not in (None, "")}
    return {"citation_id": citation_id, "label": label, "source_id": source_id,
            "claim_id": citation.get("claim_id"), "excerpt": excerpt, "locator": locator}


def resolve_citations(answer: str, context_sources: list[dict], case_id: str | None = None) -> dict:
    """Only source markers in the actual model context can resolve."""
    valid = {}
    for source in context_sources or []:
        if not isinstance(source, dict) or not source.get("source_id"):
            continue
        if source.get("source_scope") == "case" and (not case_id or source.get("case_id") != case_id):
            continue
        valid[source["source_id"]] = source
    used, citations, warnings = {}, [], []

    def replace(match):
        source_id = "SRC-" + match.group(1)
        source = valid.get(source_id)
        if source is None:
            warnings.append({"code": "INVALID_SOURCE_MARKER", "message": "Se descartó una referencia no verificable."})
            return ""
        if source_id not in used:
            label = f"[{len(used) + 1}]"
            used[source_id] = label
            citation = normalize_citation({"label": label, "excerpt": source.get("excerpt", "")}, source)
            citations.append(citation)
        return used[source_id]

    resolved_answer = _MARKER.sub(replace, str(answer or ""))
    sources_used = [deepcopy(valid[source_id]) for source_id in used]
    if not sources_used and answer:
        warnings.append({"code": "NO_VERIFIABLE_SOURCES", "message": "No se encontraron fuentes verificables para respaldar esta respuesta."})
    return {"answer": resolved_answer, "citations": citations, "sources_used": sources_used,
            "warnings": warnings}
