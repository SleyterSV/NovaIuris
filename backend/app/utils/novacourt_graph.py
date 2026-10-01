"""Case-scoped legal graph built from processed CaseResult data."""
from __future__ import annotations

import hashlib
import json
import re
import time
from collections import Counter
from .cancellation import CancellationToken, OperationCancelled

ENTITY_TYPES = ("CASE", "PARTY", "CLAIM", "LEGAL_ISSUE", "FACT", "EVIDENCE", "LAW",
                "JURISPRUDENCE", "ARGUMENT", "COUNTERARGUMENT", "RISK", "PROCEDURAL_ACT", "DOCUMENT")
_RELATION_PAIRS = {
    "ASSERTS": (("CASE", "PARTY"), ("CASE", "CLAIM"), ("CASE", "LEGAL_ISSUE"),
                ("CASE", "FACT"), ("CASE", "PROCEDURAL_ACT")),
    "SUPPORTS": (("FACT", "ARGUMENT"), ("EVIDENCE", "LEGAL_ISSUE")),
    "PROVES": (("EVIDENCE", "FACT"),),
    "CITES": (("ARGUMENT", "LAW"), ("ARGUMENT", "JURISPRUDENCE")),
    "COUNTERS": (("COUNTERARGUMENT", "ARGUMENT"),),
    "CREATES_RISK": (("RISK", "LEGAL_ISSUE"), ("RISK", "ARGUMENT")),
    "CONTAINED_IN": (("EVIDENCE", "DOCUMENT"),),
    "ARGUES": (("ARGUMENT", "LEGAL_ISSUE"), ("COUNTERARGUMENT", "LEGAL_ISSUE")),
}
RELATION_TYPES = tuple(_RELATION_PAIRS)
LEGAL_ONTOLOGY = {
    "entity_types": [{"name": name, "description": f"Elemento jurídico {name}."}
                     for name in ENTITY_TYPES],
    "edge_types": [{"name": name, "description": name.replace("_", " ").title(),
                    "source_targets": [{"source": src, "target": dst} for src, dst in pairs]}
                   for name, pairs in _RELATION_PAIRS.items()],
}
LEGACY_TYPES = {"Parte": "PARTY", "Hecho": "FACT", "Pretension": "CLAIM",
                "Pretensión": "CLAIM", "Norma": "LAW", "Argumento": "ARGUMENT",
                "Evidencia": "EVIDENCE", "Riesgo": "RISK",
                "Actuacion": "PROCEDURAL_ACT", "Actuación": "PROCEDURAL_ACT"}


def normalize_entity_type(value):
    """Exact legacy ontology aliases only; no semantic or fuzzy inference."""
    return value if value in ENTITY_TYPES else LEGACY_TYPES.get(value)


SOURCE_FIELDS = ("document_id", "chunk_id", "page_start", "page_end", "section",
                 "court", "case_number", "date", "article", "legal_basis", "official_url",
                 "excerpt", "paragraph")


def _items(value):
    return value if isinstance(value, list) else []


def _text(value):
    return " ".join(str(value or "").split()).rstrip(". ;")


def _key(value):
    return re.sub(r"^(el|la|los|las)\s+", "", _text(value).casefold())


def _id(prefix, *parts):
    content = "\x1f".join(str(part or "") for part in parts)
    return f"{prefix}-{hashlib.sha256(content.encode()).hexdigest()[:24]}"


def _label(item):
    if isinstance(item, str):
        return _text(item)
    if isinstance(item, dict):
        for key in ("text", "title", "description", "name", "argument", "risk", "evidence"):
            if item.get(key):
                return _text(item[key])
    return ""


def build_graph_input(case_result):
    """Only grounded source IDs enter the compact graph input."""
    case_id = str(case_result.get("case_id") or "")
    if not case_id:
        raise ValueError("case_id is required")
    sources = {}
    research = case_result.get("research") or {}
    candidates = (_items(case_result.get("sources")) + _items(case_result.get("sources_used"))
                  + _items(research.get("sources") if isinstance(research, dict) else None))
    for source in candidates:
        if not isinstance(source, dict) or not source.get("source_id"):
            continue
        if source.get("source_scope") == "case" and source.get("case_id") != case_id:
            continue
        if source.get("source_scope") in {"case", "public"}:
            sources[source["source_id"]] = source
    nodes, edges, keys = {}, {}, {}

    def sids(item):
        return sorted({sid for sid in _items(item.get("source_ids")) if sid in sources})

    def node(kind, title, identity=None, source_ids=(), data=None):
        if kind not in ENTITY_TYPES:
            return None
        title = _text(title)
        if not title:
            return None
        signature = (kind, str(identity) if identity is not None else _key(title))
        if signature in keys:
            existing = nodes[keys[signature]]
            existing["source_ids"] = sorted(set(existing["source_ids"]) | set(source_ids))
            return existing["node_id"]
        nid = _id("NODE", case_id, *signature)
        entry = {"node_id": nid, "uuid": nid, "entity_type": kind, "title": title,
                 "name": title, "source_ids": sorted(set(source_ids)),
                 "origin": "source" if source_ids else "analysis",
                 "metadata": {"origin": "source" if source_ids else "case_analysis"},
                 "importance": "core" if kind in {"CASE", "PARTY", "CLAIM", "LEGAL_ISSUE", "FACT"}
                 else "supporting"}
        entry.update({k: v for k, v in (data or {}).items() if v not in (None, "", [], {})})
        nodes[nid], keys[signature] = entry, nid
        return nid

    def edge(src, dst, relation, source_ids=(), metadata=None):
        if not src or not dst or src == dst or src not in nodes or dst not in nodes:
            return
        if (nodes[src]["entity_type"], nodes[dst]["entity_type"]) not in _RELATION_PAIRS.get(relation, ()):
            return
        eid = _id("EDGE", case_id, src, dst, relation)
        if eid in edges:
            edges[eid]["source_ids"] = sorted(set(edges[eid]["source_ids"]) | set(source_ids))
            return
        edges[eid] = {"edge_id": eid, "uuid": eid, "source_node_id": src,
                      "target_node_id": dst, "source_node_uuid": src, "target_node_uuid": dst,
                      "relation_type": relation, "label": relation.replace("_", " ").title(),
                      "source_ids": sorted(set(source_ids)), "metadata": metadata or {}}

    summary = case_result.get("summary") or {}
    root = node("CASE", (summary.get("materia") if isinstance(summary, dict) else None)
                or "Caso jurídico", identity=case_id)
    analysis = case_result.get("analysis") or {}
    if not isinstance(analysis, dict):
        analysis = {}
    roles = {"demandante": "claimant", "demandado": "respondent", "fiscal": "prosecution",
             "defensa": "defense", "tribunal": "court", "juez": "court"}
    parties = analysis.get("partes")
    if isinstance(parties, dict):
        for role, value in parties.items():
            title = _label(value)
            edge(root, node("PARTY", title, data={"legal_role": roles.get(role)}), "ASSERTS")
    edge(root, node("CLAIM", analysis.get("pretension_principal")), "ASSERTS")

    issue_ids, fact_ids, argument_ids = {}, {}, {}
    for item in _items(case_result.get("issues")):
        if isinstance(item, dict):
            nid = node("LEGAL_ISSUE", _label(item), identity=item.get("issue_id"))
            if nid:
                issue_ids[item.get("issue_id")] = nid
                edge(root, nid, "ASSERTS")
    for item in _items(case_result.get("facts")):
        if isinstance(item, dict):
            source_ids = sids(item)
            nid = node("FACT", _label(item), identity=item.get("fact_id"),
                       source_ids=source_ids, data={"fact_id": item.get("fact_id"),
                       "status": item.get("status"), "date": item.get("date")})
            if nid:
                fact_ids[item.get("fact_id")] = nid
                edge(root, nid, "ASSERTS", source_ids)

    for source in sources.values():
        kind = ("LAW" if source.get("source_type") in {"legislation", "article"} else
                "JURISPRUDENCE" if source.get("source_type") in {"jurisprudence", "precedent"} else
                "DOCUMENT" if source.get("source_scope") == "case" else None)
        if kind and (kind == "DOCUMENT" or source.get("source_scope") == "public"):
            node(kind, source.get("title") or "Fuente", identity=source["source_id"],
                 source_ids=[source["source_id"]],
                 data={key: source.get(key) for key in SOURCE_FIELDS})

    evidence = case_result.get("evidence") or {}
    for item in _items(evidence.get("evidence_links") if isinstance(evidence, dict) else None):
        if not isinstance(item, dict):
            continue
        source_ids = sids(item)
        if not source_ids:
            continue
        source = sources[source_ids[0]]
        title = _label(item) or source.get("title") or "Evidencia documental"
        data = {key: item.get(key, source.get(key)) for key in SOURCE_FIELDS}
        nid = node("EVIDENCE", title, identity=(item.get("evidence_id") or source_ids[0], _key(title)),
                   source_ids=source_ids, data=data)
        for sid in source_ids:
            edge(nid, keys.get(("DOCUMENT", sid)), "CONTAINED_IN", [sid], data)
        edge(nid, fact_ids.get(item.get("fact_id")), "PROVES", source_ids, data)
        edge(nid, issue_ids.get(item.get("issue_id")), "SUPPORTS", source_ids, data)

    arguments = case_result.get("arguments") or case_result.get("legal_arguments") or {}
    for item in _items(arguments.get("main_arguments") if isinstance(arguments, dict) else None):
        payload = item if isinstance(item, dict) else {"text": item}
        source_ids = sids(payload)
        nid = node("ARGUMENT", _label(payload), identity=payload.get("argument_id"),
                   source_ids=source_ids, data={"argument_id": payload.get("argument_id"),
                                                "issue_id": payload.get("issue_id"),
                                                "fact_ids": payload.get("supporting_fact_ids") or payload.get("fact_ids"),
                                                "position": payload.get("position")})
        if not nid:
            continue
        if payload.get("argument_id"):
            argument_ids[payload["argument_id"]] = nid
        edge(nid, issue_ids.get(payload.get("issue_id")), "ARGUES", source_ids)
        for fid in _items(payload.get("supporting_fact_ids") or payload.get("fact_ids")):
            edge(fact_ids.get(fid), nid, "SUPPORTS", source_ids)
        for sid in source_ids:
            edge(nid, keys.get(("LAW", sid)) or keys.get(("JURISPRUDENCE", sid)), "CITES", [sid])

    counter = case_result.get("counter_arguments") or {}
    for item in _items(counter.get("main_counterarguments") if isinstance(counter, dict) else None):
        payload = item if isinstance(item, dict) else {"text": item}
        source_ids = sids(payload)
        nid = node("COUNTERARGUMENT", _label(payload), identity=payload.get("counterargument_id"),
                   source_ids=source_ids, data={"counterargument_id": payload.get("counterargument_id"),
                                                "argument_id": payload.get("argument_id"),
                                                "issue_id": payload.get("issue_id")})
        edge(nid, issue_ids.get(payload.get("issue_id")), "ARGUES", source_ids)
        edge(nid, argument_ids.get(payload.get("argument_id")), "COUNTERS", source_ids)

    risks = case_result.get("risks") or case_result.get("risk_analysis") or {}
    if isinstance(risks, dict):
        for field in ("critical_risks", "procedural_risks", "evidentiary_risks", "legal_risks"):
            for item in _items(risks.get(field)):
                payload = item if isinstance(item, dict) else {"text": item}
                source_ids = sids(payload)
                nid = node("RISK", _label(payload), source_ids=source_ids)
                edge(nid, issue_ids.get(payload.get("issue_id")), "CREATES_RISK", source_ids)
                edge(nid, argument_ids.get(payload.get("argument_id")), "CREATES_RISK", source_ids)

    # The normal timeline merely projects dated facts, so it creates no duplicate nodes.
    for item in _items(case_result.get("timeline")):
        if isinstance(item, dict) and item.get("act_id") and not item.get("fact_id"):
            source_ids = sids(item)
            nid = node("PROCEDURAL_ACT", _label(item), identity=item["act_id"],
                       source_ids=source_ids, data={"date": item.get("date")})
            edge(root, nid, "ASSERTS", source_ids)
    return {"case_id": case_id, "entities": sorted(nodes.values(), key=lambda n: n["node_id"]),
            "relations": sorted(edges.values(), key=lambda e: e["edge_id"]),
            "provenance": sorted(sources)}


def build_legal_context(case_result):
    return json.dumps(build_graph_input(case_result), ensure_ascii=False, separators=(",", ":"))


def graph_result(status, *, graph_id=None, case_id=None, version=0, stage=None,
                 nodes=None, edges=None, message=None, metadata=None, warnings=None):
    nodes, edges = _items(nodes), _items(edges)
    counts = {"node_count": len(nodes), "edge_count": len(edges),
              "by_type": dict(sorted(Counter(n.get("entity_type") for n in nodes).items()))}
    return {"status": status, "graph_id": graph_id, "case_id": case_id,
            "version": version, "stage": stage, "is_final": status == "ready",
            "nodes": nodes, "edges": edges, "counts": counts, "node_count": len(nodes),
            "edge_count": len(edges), "warnings": warnings or [],
            "error": {"code": status.upper(), "message": message}
            if status in {"failed", "timeout"} else None,
            "message": message or "", "metadata": metadata or {}}


class NovaCourtGraphOrchestrator:
    def __init__(self, builder_factory, *, enabled, timeout, poll_interval,
                 chunk_size, chunk_overlap, batch_size):
        self.builder_factory, self.enabled, self.timeout = builder_factory, enabled, timeout
        self.poll_interval, self.batch_size = poll_interval, batch_size

    def build(self, case_result, cancellation_token=None, snapshot_callback=None):
        case_id = case_result.get("case_id")
        if not self.enabled:
            return graph_result("not_requested", case_id=case_id)
        started = time.monotonic()
        token = CancellationToken(parent=cancellation_token, timeout=self.timeout)
        graph_id, snapshot, batch_count = None, None, 0
        try:
            token.check()
            contract = build_graph_input(case_result)
            if len(contract["entities"]) <= 1:
                return graph_result("not_requested", case_id=case_id)
            entities, relations = contract["entities"], contract["relations"]
            snapshot = graph_result("building", case_id=case_id, version=1,
                                    stage="core_entities", nodes=entities, edges=relations)
            if snapshot_callback:
                snapshot_callback(snapshot)
            token.check()
            builder = self.builder_factory()
            token.check()
            graph_id = builder.create_graph("NovaCourt Legal Analysis")
            token.check()
            builder.set_ontology(graph_id, LEGAL_ONTOLOGY)
            records = [{"entity_type": n["entity_type"], "node_id": n["node_id"],
                        "title": n["title"], "source_ids": n["source_ids"]} for n in entities]
            records += [{"relation_type": e["relation_type"],
                         "source_node_id": e["source_node_id"],
                         "target_node_id": e["target_node_id"],
                         "source_ids": e["source_ids"]} for e in relations]
            episodes = [json.dumps(item, ensure_ascii=False, separators=(",", ":"))
                        for item in records]
            batch_count = (len(episodes) + self.batch_size - 1) // self.batch_size
            token.check()
            episode_ids = builder.add_text_batches(graph_id, episodes, self.batch_size,
                                                   cancellation_token=token)
            token.check()
            remaining = max(0, self.timeout - (time.monotonic() - started))
            if not remaining:
                raise OperationCancelled()
            builder._wait_for_episodes(episode_ids, timeout=remaining,
                                       poll_interval=self.poll_interval,
                                       cancellation_token=token)
            token.check()
            # Fetch once to verify Zep completion. Its extraction is not documentary authority.
            builder.get_graph_data(graph_id, cancellation_token=token)
            token.check()
            return graph_result("ready", graph_id=graph_id, case_id=case_id, version=2,
                                stage="completed", nodes=entities, edges=relations,
                                metadata={"graph_build_duration_ms": round((time.monotonic()-started)*1000),
                                          "snapshot_count": 2, "batch_count": batch_count})
        except OperationCancelled:
            if cancellation_token is not None and cancellation_token.is_cancelled():
                raise
            status, message = "timeout", "La construcción del grafo superó el límite de espera."
        except Exception as error:
            status = "timeout" if error.__class__.__name__ == "GraphProcessingTimeoutError" else "failed"
            message = "No fue posible completar el grafo jurídico. El análisis del caso permanece disponible."
        return graph_result(status, graph_id=graph_id, case_id=case_id,
                            version=snapshot["version"] + 1 if snapshot else 0, stage="failed",
                            nodes=snapshot["nodes"] if snapshot else [],
                            edges=snapshot["edges"] if snapshot else [], message=message,
                            warnings=[{"code": status.upper(), "message": "Grafo parcial"}] if snapshot else [],
                            metadata={"graph_build_duration_ms": round((time.monotonic()-started)*1000),
                                      "snapshot_count": 1 if snapshot else 0, "batch_count": batch_count})
