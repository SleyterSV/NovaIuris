"""Request-local NovaCase work reduction and safe measurements."""
from __future__ import annotations

from copy import deepcopy
from threading import Lock
from time import perf_counter

from app.services.source_contracts import normalize_public_legal_v2_source
from app.utils.cancellation import check_cancelled


PUBLIC_CONTEXT_CHAR_BUDGET = 48000
PUBLIC_UNIT_CHAR_LIMIT = 24000


def resolve_public_v2_hits(repository, hits, *, max_chars=PUBLIC_CONTEXT_CHAR_BUDGET,
                           max_unit_chars=PUBLIC_UNIT_CHAR_LIMIT, cancellation_token=None):
    """Resolve whole V2 units once, rejecting invalid identity and omitting oversized units."""
    selected, sources, warnings = [], [], []
    seen = set()
    remaining = max_chars
    for hit in hits:
        check_cancelled(cancellation_token)
        if not isinstance(hit, dict):
            raise ValueError("V2_SEARCH_RESULT_INVALID")
        key = (hit.get("document_id"), hit.get("unit_id"))
        if not all(key):
            raise ValueError("V2_SEARCH_IDENTITY_MISSING")
        if key in seen:
            continue
        seen.add(key)
        detail = repository.get_unit(key[1], document_id=key[0])
        if detail is None:
            raise ValueError("V2_CANONICAL_UNIT_NOT_FOUND")
        source = normalize_public_legal_v2_source(hit, detail)
        length = len(source["excerpt"])
        if length > max_unit_chars or length > remaining:
            warnings.append({"code": "PUBLIC_UNIT_CONTEXT_BUDGET_EXCEEDED",
                             "document_id": key[0], "unit_id": key[1]})
            continue
        remaining -= length
        selected.append({**hit, "source_id": source["source_id"], "source": source})
        sources.append(source)
    return selected, sources, warnings


def research_queries(values, limit, *, fallback=None):
    """Deduplicate model queries; use case analysis only when it supplied none."""
    seen, queries = set(), []
    safe_limit = max(1, min(int(limit), 12))
    for value in values if isinstance(values, list) else []:
        if not isinstance(value, str):
            continue
        query = " ".join(value.split())
        key = query.casefold()
        if not query or key in seen:
            continue
        seen.add(key)
        queries.append(query)
        if len(queries) >= safe_limit:
            break
    if not queries and isinstance(fallback, dict):
        parts = [fallback.get("pretension_principal")]
        issues = fallback.get("problemas_juridicos")
        if isinstance(issues, list):
            parts.extend(item.get("text") or item.get("issue") if isinstance(item, dict)
                         else item for item in issues[:2])
        grounded = " ".join(str(part).strip() for part in parts if isinstance(part, str) and part.strip())
        if grounded:
            queries.append(" ".join(grounded.split())[:500].rstrip())
    return queries


def research_status(queries, results, public_sources, warnings):
    """Describe source availability separately from pipeline completion."""
    if public_sources:
        return "VERIFIED_SOURCES"
    if any(item.get("result_status") == "search_unavailable" for item in results):
        return "UNAVAILABLE"
    if any(item.get("result_status") == "search_failed" for item in results):
        return "ERROR"
    if any(item.get("code") in {"PUBLIC_LEGAL_SOURCE_UNAVAILABLE",
                                  "PUBLIC_UNIT_CONTEXT_BUDGET_EXCEEDED"} for item in warnings):
        return "UNAVAILABLE"
    return "NO_RESULTS" if queries else "UNAVAILABLE"


def prompt_documents(documents):
    """Project retrieved hits once, retaining the exact excerpt and locator."""
    fields = ("id", "source_id", "source_scope", "source_type", "tipo_documento",
              "title", "display_title", "document_title", "article", "legal_basis",
              "court", "issuer", "entity", "case_number", "expediente", "number",
              "document_number", "date", "document_id", "unit_id", "unit_type",
              "unit_number", "provenance_version", "case_id", "chunk_id",
              "page_start", "page_end", "section", "paragraph", "official_url",
              "score", "similarity", "vector_similarity", "reranker_score",
              "sumilla", "sala", "norma", "numero_expediente", "fundamento")
    projected = []
    for document in documents:
        if not isinstance(document, dict):
            continue
        source = document.get("source") if isinstance(document.get("source"), dict) else {}
        item = {}
        for key in fields:
            value = document.get(key)
            if value in (None, ""):
                value = source.get(key)
            if value not in (None, ""):
                item[key] = value
        excerpt = (source.get("excerpt") or document.get("extracto_exacto")
                   or document.get("texto") or document.get("content") or "")
        item["texto"] = excerpt
        projected.append(item)
    return projected


class CaseExecutionContext:
    """Memoize only within one case task; never publish private data globally."""
    def __init__(self, case_id, document_versions=()):
        self.case_id = case_id
        self.document_versions = tuple(sorted(document_versions))
        self._lock = Lock()
        self._contexts = {}
        self._research = {}

    def _remember(self, cache, key, compute):
        with self._lock:
            if key in cache:
                return deepcopy(cache[key])
        value = compute()
        with self._lock:
            cache.setdefault(key, value)
        return value

    def case_context(self, query, compute):
        return self._remember(self._contexts,
                              (self.case_id, self.document_versions, query), compute)

    def research(self, query, filters, compute):
        filter_key = tuple(sorted((str(key), str(value)) for key, value in filters.items()))
        return self._remember(self._research,
                              (self.case_id, query, filter_key), compute)


class CaseExecutionMetrics:
    """Lives for one analyze_case invocation; contains counts, never content."""
    def __init__(self):
        self.started = perf_counter()
        self._lock = Lock()
        self._active = {}
        self.timings_ms = {}
        self.counts = {"llm_service_call_count": 0, "embedding_call_count": 0,
                       "retrieval_call_count": 0, "case_context_lookup_count": 0}

    def stage(self, name, status):
        name = "case_context" if name == "documents" else name
        now = perf_counter()
        with self._lock:
            if status == "running":
                self._active[name] = now
            elif status in {"completed", "failed", "skipped"}:
                started = self._active.pop(name, None)
                self.timings_ms[name] = round((now - started) * 1000, 2) if started else 0.0

    def increment(self, name):
        with self._lock:
            self.counts[name] = self.counts.get(name, 0) + 1

    def snapshot(self):
        with self._lock:
            return {"timings_ms": {**self.timings_ms,
                                   "total": round((perf_counter() - self.started) * 1000, 2)},
                    "counts": dict(self.counts)}
