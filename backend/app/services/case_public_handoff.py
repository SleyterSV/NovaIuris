"""Explicit, task-local Search to Case references. No browser text is authoritative."""
from uuid import UUID

from app.services.case_execution import resolve_public_v2_hits


MAX_HANDOFF_UNITS = 12


def normalize_handoff_references(value):
    if not isinstance(value, list) or not 1 <= len(value) <= MAX_HANDOFF_UNITS:
        raise ValueError("PUBLIC_SOURCE_REFERENCES_INVALID")
    normalized, seen = [], set()
    for item in value:
        if not isinstance(item, dict) or item.get("source_scope") != "public_legal":
            raise ValueError("PUBLIC_SOURCE_SCOPE_INVALID")
        try:
            document_id = str(UUID(str(item["document_id"])))
            unit_id = str(UUID(str(item["unit_id"])))
        except (KeyError, TypeError, ValueError) as error:
            raise ValueError("PUBLIC_SOURCE_IDENTITY_INVALID") from error
        key = (document_id, unit_id)
        if key not in seen:
            normalized.append({"source_scope": "public_legal",
                               "document_id": document_id, "unit_id": unit_id})
            seen.add(key)
    return normalized


def resolve_handoff_references(repository, references, *, cancellation_token=None):
    """Resolve only exact current V2 units; reject partial or oversized handoffs."""
    canonical = normalize_handoff_references(references)
    documents, sources, warnings = resolve_public_v2_hits(
        repository, canonical, cancellation_token=cancellation_token)
    if warnings or len(sources) != len(canonical):
        raise ValueError("PUBLIC_SOURCE_CONTEXT_UNAVAILABLE")
    return documents, sources
