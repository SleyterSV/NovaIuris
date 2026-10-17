"""Authorized, canonical context shared by the modern Court branches."""
from copy import deepcopy

from .legal_repository_v2 import LegalRepositoryV2
from .source_contracts import normalize_case_source, reopen_public_legal_v2_source


def prepare_court_context(case_result, *, owner_id, case_id, source_case_task_id=None,
                          legal_repository=None, case_corpus_repository=None):
    if not owner_id or case_result.get("case_id") != case_id:
        raise ValueError("COURT_CONTEXT_IDENTITY_INVALID")
    selected_documents = set(case_result.get("document_ids") or [])
    candidates = list(case_result.get("sources") or []) + list(case_result.get("sources_used") or [])
    research = case_result.get("research")
    if isinstance(research, dict):
        candidates += list(research.get("sources") or [])
    private, public = {}, {}
    for source in candidates:
        if not isinstance(source, dict):
            continue
        scope = source.get("source_scope")
        if scope in {"public", "public_legal"}:
            if scope == "public" and source.get("legal_source_scope") != "public_legal":
                raise ValueError("COURT_SOURCE_UNVERIFIED")
            if legal_repository is None:
                legal_repository = LegalRepositoryV2()
            verified = reopen_public_legal_v2_source(source, legal_repository)
            public[verified["source_id"]] = verified
        elif scope in {"case", "private_case"}:
            if source.get("case_id") != case_id or source.get("document_id") not in selected_documents:
                raise ValueError("COURT_PRIVATE_SOURCE_INVALID")
            if case_corpus_repository is None:
                raise ValueError("COURT_PRIVATE_CORPUS_UNAVAILABLE")
            case_corpus_repository.validate_documents(case_id, [source["document_id"]])
            chunk = case_corpus_repository.get_chunk(case_id, source["document_id"], source.get("chunk_id"))
            if not chunk:
                raise ValueError("COURT_PRIVATE_SOURCE_INVALID")
            verified = normalize_case_source(chunk)
            if verified["source_id"] != source.get("source_id"):
                raise ValueError("COURT_PRIVATE_SOURCE_INVALID")
            private[verified["source_id"]] = verified
        else:
            raise ValueError("COURT_SOURCE_UNVERIFIED")
    context = deepcopy(case_result)
    context.update(owner_id=owner_id, case_id=case_id, source_case_task_id=source_case_task_id,
                   private_sources=list(private.values()), public_legal_sources=list(public.values()))
    allowed = {**private, **public}
    context["sources"] = list(allowed.values())
    context["sources_used"] = [allowed[source["source_id"]] for source in case_result.get("sources_used", [])
                               if isinstance(source, dict) and source.get("source_id") in allowed]
    if isinstance(context.get("research"), dict):
        context["research"]["sources"] = list(public.values())
    for fact in context.get("facts") or []:
        if isinstance(fact, dict):
            fact["source_ids"] = [sid for sid in fact.get("source_ids", []) if sid in private]
    evidence = context.get("evidence")
    if isinstance(evidence, dict):
        evidence["evidence_links"] = [item for item in evidence.get("evidence_links", [])
                                     if isinstance(item, dict) and item.get("source_ids")
                                     and all(sid in private for sid in item["source_ids"])]
    return context
