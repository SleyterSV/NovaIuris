"""Case-scoped legal graph built from processed CaseResult data."""
from __future__ import annotations

import hashlib
import json
import re
import time
import logging
from collections import Counter
from .cancellation import CancellationToken, OperationCancelled

logger = logging.getLogger(__name__)

ENTITY_TYPES = ("CASE", "PARTY", "CLAIM", "LEGAL_ISSUE", "FACT", "EVIDENCE", "LAW",
                "JURISPRUDENCE", "ARGUMENT", "COUNTERARGUMENT", "RISK", "PROCEDURAL_ACT", "DOCUMENT",
                "JUDGE_ANALYSIS", "DECISION")
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
    "EVALUATES": (("JUDGE_ANALYSIS", "LEGAL_ISSUE"),),
    "LEADS_TO": (("JUDGE_ANALYSIS", "DECISION"),),
}
RELATION_TYPES = tuple(_RELATION_PAIRS)
LEGAL_ONTOLOGY = {
    "entity_types": [{"name": name, "description": f"Elemento jurídico {name}."}
                     for name in ENTITY_TYPES],
    "edge_types": [{"name": name, "description": name.replace("_", " ").title(),
                    "source_targets": [{"source": src, "target": dst} for src, dst in pairs]}
                   for name, pairs in _RELATION_PAIRS.items()],
}
PROVIDER_ENTITY_LIMIT = 10
PROVIDER_EDGE_LIMIT = 10
_RESERVED_ZEP_FIELDS = {"uuid", "name", "graph_id", "group_id", "name_embedding", "summary", "created_at"}
_ZEP_ENTITY_NAME = re.compile(r"^[A-Z][a-z][A-Za-z0-9]*$")
_ZEP_EDGE_NAME = re.compile(r"^[A-Z]+(?:_[A-Z]+)*$")
PROVIDER_TYPE_BY_CANONICAL = {
    "CASE": "Case", "PARTY": "Party", "CLAIM": "Argument",
    "LEGAL_ISSUE": "LegalIssue", "FACT": "Fact", "EVIDENCE": "Evidence",
    "LAW": "LegalSource", "JURISPRUDENCE": "LegalSource",
    "ARGUMENT": "Argument", "COUNTERARGUMENT": "Argument",
    "RISK": "Risk", "PROCEDURAL_ACT": "LegalIssue", "DOCUMENT": "Evidence",
    "JUDGE_ANALYSIS": "JudgeAnalysis", "DECISION": "Decision",
}
PROVIDER_TYPE_ORDER = ("Case", "Party", "Fact", "Evidence", "LegalSource",
                       "LegalIssue", "Argument", "Risk", "JudgeAnalysis", "Decision")
PROVIDER_EDGE_BY_CANONICAL = {name: name for name in _RELATION_PAIRS}


def validate_provider_ontology(ontology):
    """Reject an invalid provider projection before creating a remote graph."""
    entities = ontology.get("entity_types")
    edges = ontology.get("edge_types")
    if not isinstance(entities, list) or not isinstance(edges, list) or not entities:
        raise ValueError("COURT_ONTOLOGY_INVALID_STRUCTURE")
    if len(entities) > PROVIDER_ENTITY_LIMIT:
        raise ValueError("COURT_ONTOLOGY_ENTITY_LIMIT")
    if len(edges) > PROVIDER_EDGE_LIMIT:
        raise ValueError("COURT_ONTOLOGY_EDGE_LIMIT")
    entity_names = [item.get("name") for item in entities if isinstance(item, dict)]
    edge_names = [item.get("name") for item in edges if isinstance(item, dict)]
    if (len(entity_names) != len(entities) or len(edge_names) != len(edges)
            or any(not isinstance(name, str) or not _ZEP_ENTITY_NAME.fullmatch(name)
                   for name in entity_names)
            or any(not isinstance(name, str) or not _ZEP_EDGE_NAME.fullmatch(name)
                   for name in edge_names)):
        raise ValueError("COURT_ONTOLOGY_INVALID_NAME")
    if len(set(entity_names)) != len(entity_names):
        raise ValueError("COURT_ONTOLOGY_DUPLICATE_ENTITY")
    if len(set(edge_names)) != len(edge_names):
        raise ValueError("COURT_ONTOLOGY_DUPLICATE_EDGE")
    allowed = set(entity_names)
    for item in entities + edges:
        fields = item.get("attributes", [])
        if not isinstance(fields, list) or len(fields) > 10:
            raise ValueError("COURT_ONTOLOGY_FIELD_LIMIT")
        if any(not isinstance(field, dict) or str(field.get("name", "")).lower() in _RESERVED_ZEP_FIELDS
               for field in fields):
            raise ValueError("COURT_ONTOLOGY_RESERVED_FIELD")
    for edge in edges:
        pairs = edge.get("source_targets")
        if not isinstance(pairs, list) or not pairs or len(pairs) > 100:
            raise ValueError("COURT_ONTOLOGY_PAIR_LIMIT")
        if any(not isinstance(pair, dict) or pair.get("source") not in allowed
               or pair.get("target") not in allowed for pair in pairs):
            raise ValueError("COURT_ONTOLOGY_ORPHAN_TARGET")
    return ontology


def provider_ontology(entities):
    """Project canonical Court types to stable Zep PascalCase extraction hints."""
    present = {item.get("entity_type") for item in entities}
    selected = {PROVIDER_TYPE_BY_CANONICAL[kind] for kind in present
                if kind in PROVIDER_TYPE_BY_CANONICAL}
    entity_types = [{"name": name, "description": f"Elemento jurídico {name}."}
                    for name in PROVIDER_TYPE_ORDER if name in selected]
    edge_types = []
    for relation, pairs in _RELATION_PAIRS.items():
        projected = []
        for source, target in pairs:
            if source not in present or target not in present:
                continue
            pair = {"source": PROVIDER_TYPE_BY_CANONICAL[source],
                    "target": PROVIDER_TYPE_BY_CANONICAL[target]}
            if pair not in projected:
                projected.append(pair)
        if projected:
            edge_types.append({"name": PROVIDER_EDGE_BY_CANONICAL[relation],
                               "description": relation.replace("_", " ").title(),
                               "source_targets": projected})
    return validate_provider_ontology({"entity_types": entity_types, "edge_types": edge_types})
LEGACY_TYPES = {"Parte": "PARTY", "Hecho": "FACT", "Pretension": "CLAIM",
                "Pretensión": "CLAIM", "Norma": "LAW", "Argumento": "ARGUMENT",
                "Evidencia": "EVIDENCE", "Riesgo": "RISK",
                "Actuacion": "PROCEDURAL_ACT", "Actuación": "PROCEDURAL_ACT"}


def normalize_entity_type(value):
    """Exact legacy ontology aliases only; no semantic or fuzzy inference."""
    return value if value in ENTITY_TYPES else LEGACY_TYPES.get(value)


SOURCE_FIELDS = ("source_scope", "provenance_version", "source_id", "document_id", "unit_id", "chunk_id", "page_start", "page_end", "section",
                 "court", "case_number", "date", "article", "legal_basis", "official_url",
                 "excerpt", "paragraph", "unit_type", "unit_number", "title")


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
        if source.get("source_scope") in {"case", "private_case"} and source.get("case_id") != case_id:
            continue
        if source.get("source_scope") in {"case", "public", "private_case", "public_legal"}:
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
            source_ids = [sid for sid in sids(item)
                          if sources[sid].get("source_scope") in {"case", "private_case"}]
            nid = node("FACT", _label(item), identity=item.get("fact_id"),
                       source_ids=source_ids, data={"fact_id": item.get("fact_id"),
                       "status": item.get("status"), "date": item.get("date")})
            if nid:
                fact_ids[item.get("fact_id")] = nid
                edge(root, nid, "ASSERTS", source_ids)

    for source in sources.values():
        kind = ("LAW" if source.get("source_type") in {"legislation", "article"} else
                "JURISPRUDENCE" if source.get("source_type") in {"jurisprudence", "precedent"} else
                "DOCUMENT" if source.get("source_scope") in {"case", "private_case"} else None)
        if kind and (kind == "DOCUMENT" or source.get("source_scope") in {"public", "public_legal"}):
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
        source_ids = [sid for sid in source_ids if sources[sid].get("source_scope") in {"case", "private_case"}]
        if not source_ids:
            continue
        source = sources[source_ids[0]]
        title = _label(item) or source.get("title") or "Evidencia documental"
        data = {key: source.get(key) for key in SOURCE_FIELDS}
        nid = node("EVIDENCE", title, identity=(item.get("evidence_id") or source_ids[0], _key(title)),
                   source_ids=source_ids, data=data)
        for sid in source_ids:
            edge(nid, keys.get(("DOCUMENT", sid)), "CONTAINED_IN", [sid], data)
        edge(nid, fact_ids.get(item.get("fact_id")), "PROVES", source_ids, data)
        edge(nid, issue_ids.get(item.get("issue_id")), "SUPPORTS", source_ids, data)

    proven_facts = {edge["target_node_id"] for edge in edges.values()
                    if edge["relation_type"] == "PROVES"}
    for fact_id in fact_ids.values():
        fact = nodes[fact_id]
        if fact.get("status") in {"supported", "accredited", "proven"} and fact_id not in proven_facts:
            fact["status"] = "alleged"

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
                                                "issue_id": payload.get("issue_id"),
                                                "position": payload.get("position")})
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


def add_judicial_projection(graph, simulation):
    """Append only a verified simulated judicial section to a case-scoped graph snapshot."""
    if not isinstance(graph, dict) or graph.get("case_id") != simulation.get("case_id"):
        raise ValueError("Graph case identity mismatch")
    if simulation.get("status") != "ready" or not simulation.get("judge", {}).get("content", "").strip():
        return graph
    result = {**graph, "nodes": list(graph.get("nodes") or []), "edges": list(graph.get("edges") or [])}
    case_id = graph["case_id"]
    issues = [node for node in result["nodes"] if node.get("entity_type") == "LEGAL_ISSUE"]
    judge_id, decision_id = _id("NODE", case_id, "JUDGE_ANALYSIS"), _id("NODE", case_id, "DECISION")
    judge = {"node_id": judge_id, "uuid": judge_id, "entity_type": "JUDGE_ANALYSIS",
             "title": "Evaluación judicial simulada", "name": "Evaluación judicial simulada",
             "description": simulation["judge"]["content"], "source_ids": [],
             "origin": "simulation", "metadata": {"origin": "simulation"}, "importance": "core"}
    decision = {"node_id": decision_id, "uuid": decision_id, "entity_type": "DECISION",
                "title": "Resultado de la simulación", "name": "Resultado de la simulación",
                "description": simulation["judge"]["content"], "simulation": True,
                "source_ids": [], "origin": "simulation", "metadata": {"origin": "simulation"},
                "importance": "core"}
    result["nodes"] = [node for node in result["nodes"] if node.get("node_id") not in {judge_id, decision_id}]
    result["nodes"].extend((judge, decision))
    targets = [(issue["node_id"], "EVALUATES") for issue in issues] + [(decision_id, "LEADS_TO")]
    result["edges"] = [edge for edge in result["edges"] if edge.get("source_node_id") != judge_id]
    for target, relation in targets:
        eid = _id("EDGE", case_id, judge_id, target, relation)
        result["edges"].append({"edge_id": eid, "uuid": eid, "source_node_id": judge_id,
                                "target_node_id": target, "source_node_uuid": judge_id,
                                "target_node_uuid": target, "relation_type": relation,
                                "label": relation, "source_ids": [], "metadata": {}})
    result["counts"] = {"node_count": len(result["nodes"]), "edge_count": len(result["edges"]),
                        "by_type": dict(sorted(Counter(node["entity_type"] for node in result["nodes"]).items()))}
    result["node_count"], result["edge_count"] = len(result["nodes"]), len(result["edges"])
    result["version"] = result.get("version", 0) + 1
    return result


def build_legal_context(case_result):
    return json.dumps(build_graph_input(case_result), ensure_ascii=False, separators=(",", ":"))


def graph_result(status, *, graph_id=None, case_id=None, version=0, stage=None,
                 nodes=None, edges=None, message=None, metadata=None, warnings=None, error_code=None):
    nodes, edges = _items(nodes), _items(edges)
    counts = {"node_count": len(nodes), "edge_count": len(edges),
              "by_type": dict(sorted(Counter(n.get("entity_type") for n in nodes).items()))}
    return {"status": status, "graph_id": graph_id, "case_id": case_id,
            "version": version, "stage": stage, "is_final": status in {"ready", "empty", "failed", "timeout"},
            "nodes": nodes, "edges": edges, "counts": counts, "node_count": len(nodes),
            "edge_count": len(edges), "warnings": warnings or [],
            "error": {"code": error_code or status.upper(), "message": message}
            if status in {"failed", "timeout"} else None,
            "message": message or "", "metadata": metadata or {}}


class NovaCourtGraphOrchestrator:
    def __init__(self, builder_factory, *, enabled, timeout, poll_interval,
                 chunk_size, chunk_overlap, batch_size, settle_seconds=30):
        self.builder_factory, self.enabled, self.timeout = builder_factory, enabled, timeout
        self.poll_interval, self.batch_size = poll_interval, batch_size
        self.settle_seconds = settle_seconds

    def build(self, case_result, cancellation_token=None, snapshot_callback=None):
        case_id = case_result.get("case_id")
        if not self.enabled:
            return graph_result("not_requested", case_id=case_id)
        started = time.monotonic()
        token = CancellationToken(parent=cancellation_token, timeout=self.timeout)
        graph_id, snapshot, batch_count = None, None, 0
        stage = "prepare"
        operation_count, input_characters = 0, 0
        poll_count = 0
        wait_duration_ms = 0
        try:
            token.check()
            contract = build_graph_input(case_result)
            if len(contract["entities"]) <= 1:
                return graph_result("not_requested", case_id=case_id)
            entities, relations = contract["entities"], contract["relations"]
            ontology = provider_ontology(entities)
            snapshot = graph_result("building", case_id=case_id, version=1,
                                    stage="core_entities", nodes=entities, edges=relations)
            if snapshot_callback:
                snapshot_callback(snapshot)
            token.check()
            builder = self.builder_factory()
            token.check()
            stage = "create_graph"
            graph_id = builder.create_graph("NovaCourt Legal Analysis")
            operation_count += 1
            token.check()
            stage = "set_ontology"
            logger.info("NovaCourt graph ontology graph_id=%s entity_count=%s entity_names=%s edge_count=%s edge_names=%s pairs=%s",
                        graph_id, len(ontology["entity_types"]),
                        [item["name"] for item in ontology["entity_types"]],
                        len(ontology["edge_types"]),
                        [item["name"] for item in ontology["edge_types"]],
                        [(item["name"], len(item["source_targets"]),
                          [(pair["source"], pair["target"]) for pair in item["source_targets"]])
                         for item in ontology["edge_types"]])
            builder.set_ontology(graph_id, ontology)
            operation_count += 1
            stage = "prepare_episodes"
            records = [{"entity_type": n["entity_type"], "node_id": n["node_id"],
                        "title": n["title"], "source_ids": n["source_ids"]} for n in entities]
            records += [{"relation_type": e["relation_type"],
                         "source_node_id": e["source_node_id"],
                         "target_node_id": e["target_node_id"],
                         "source_ids": e["source_ids"]} for e in relations]
            episodes = [json.dumps(item, ensure_ascii=False, separators=(",", ":"))
                        for item in records]
            if not episodes or any(not item.strip() or len(item) > 10000 for item in episodes):
                raise ValueError("Invalid graph episodes")
            logger.info("NovaCourt graph episodes graph_id=%s count=%s batches=%s max_characters=%s",
                        graph_id, len(episodes), (len(episodes) + self.batch_size - 1) // self.batch_size,
                        max(map(len, episodes)))
            batch_count = (len(episodes) + self.batch_size - 1) // self.batch_size
            input_characters = sum(map(len, episodes))
            token.check()
            stage = "send_batch"
            episode_ids = builder.add_text_batches(graph_id, episodes, self.batch_size,
                                                   cancellation_token=token)
            operation_count += batch_count
            token.check()
            if not episode_ids or len(episode_ids) != len(episodes):
                raise ValueError("Graph episode acknowledgement count mismatch")
            remaining = max(0, self.timeout - (time.monotonic() - started))
            if not remaining:
                raise OperationCancelled()
            stage = "poll_batch"
            wait_started = time.monotonic()
            builder._wait_for_episodes(episode_ids, timeout=remaining,
                                       poll_interval=self.poll_interval,
                                       cancellation_token=token)
            poll_count = getattr(builder, "last_poll_count", 0)
            wait_duration_ms = round((time.monotonic() - wait_started) * 1000)
            token.check()
            # Episode completion and graph materialization are separate states.
            stage = "fetch_nodes"
            settle_until = min(started + self.timeout, time.monotonic() + min(self.settle_seconds, self.timeout))
            while True:
                token.check()
                provider_graph = builder.get_graph_data(graph_id, cancellation_token=token)
                operation_count += 1
                if not isinstance(provider_graph, dict) or not isinstance(provider_graph.get("nodes"), list) or not isinstance(provider_graph.get("edges"), list):
                    raise ValueError("Invalid provider graph payload")
                if provider_graph["nodes"] and provider_graph["edges"] or time.monotonic() >= settle_until:
                    break
                time.sleep(min(self.poll_interval, max(0, settle_until - time.monotonic())))
            token.check()
            if not provider_graph["nodes"] or not provider_graph["edges"]:
                return graph_result("empty", graph_id=graph_id, case_id=case_id, version=2,
                                    stage="completed", nodes=[], edges=[],
                                    metadata={"graph_build_duration_ms": round((time.monotonic()-started)*1000),
                                              "snapshot_count": 2, "batch_count": batch_count,
                                              "episode_count": len(episodes), "poll_count": poll_count,
                                              "operation_count": operation_count, "graph_wait_duration_ms": wait_duration_ms,
                                              "empty_reason": "provider_completed_empty"})
            return graph_result("ready", graph_id=graph_id, case_id=case_id, version=2,
                                stage="completed", nodes=entities, edges=relations,
                                metadata={"graph_build_duration_ms": round((time.monotonic()-started)*1000),
                                          "snapshot_count": 2,
                                          "batch_count": batch_count, "episode_count": len(episodes),
                                          "input_characters": input_characters,
                                          "poll_count": poll_count,
                                          "graph_wait_duration_ms": wait_duration_ms,
                                          "operation_count": operation_count})
        except OperationCancelled:
            if cancellation_token is not None and cancellation_token.is_cancelled():
                raise
            error_code, error_type = "GRAPH_TIMEOUT", "DeadlineExceeded"
            status, message = "timeout", "La construcción del grafo superó el límite de espera."
        except Exception as error:
            status = "timeout" if error.__class__.__name__ == "GraphProcessingTimeoutError" else "failed"
            error_type = type(error).__name__
            error_code = ("GRAPH_TIMEOUT" if status == "timeout" else
                          "GRAPH_INVALID_PAYLOAD" if isinstance(error, ValueError) else "GRAPH_PROVIDER_ERROR")
            message = "No fue posible completar el grafo jurídico. El análisis del caso permanece disponible."
        logger.warning("NovaCourt graph terminal case_id=%s graph_id=%s stage=%s operation=%s batch_index=%s attempt=%s elapsed_ms=%s remaining_ms=%s provider_status=%s http_status=%s error_type=%s",
                       case_id, graph_id, stage, stage, getattr(locals().get("error"), "batch_index", None), 1,
                       round((time.monotonic()-started)*1000),
                       round(max(0, self.timeout-(time.monotonic()-started))*1000), status,
                       getattr(locals().get("error"), "http_status", None) or getattr(locals().get("error"), "status_code", None), error_type)
        return graph_result(status, graph_id=graph_id, case_id=case_id,
                            version=snapshot["version"] + 1 if snapshot else 0, stage=stage,
                            nodes=snapshot["nodes"] if snapshot else [],
                            edges=snapshot["edges"] if snapshot else [], message=message,
                            warnings=[{"code": status.upper(), "message": "Grafo parcial"}] if snapshot else [],
                            metadata={"graph_build_duration_ms": round((time.monotonic()-started)*1000),
                                      "snapshot_count": 1 if snapshot else 0,
                                      "batch_count": batch_count, "input_characters": input_characters,
                                      "poll_count": poll_count,
                                      "graph_wait_duration_ms": wait_duration_ms,
                                      "operation_count": operation_count, "failed_stage": stage,
                                      "error_type": error_type,
                                      "batch_index": getattr(locals().get("error"), "batch_index", None)}, error_code=error_code)
