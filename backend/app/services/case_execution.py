"""Request-local NovaCase work reduction and safe measurements."""
from __future__ import annotations

from copy import deepcopy
from threading import Lock
from time import perf_counter


def research_queries(values, limit):
    """Deduplicate whitespace/case variants without rewriting the first query."""
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
    return queries


def prompt_documents(documents):
    """Project retrieved hits once, retaining the exact excerpt and locator."""
    fields = ("id", "source_id", "source_scope", "source_type", "tipo_documento",
              "title", "article", "legal_basis", "court", "entity", "case_number",
              "document_number", "date", "document_id", "case_id", "chunk_id",
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
