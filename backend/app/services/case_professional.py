"""Deterministic case provenance and report structure; no provider calls."""
from __future__ import annotations

import hashlib
import re
from datetime import datetime, timezone


SOURCE_MARKER = re.compile(r"\[(SRC-[A-Za-z0-9_-]{6,80})\]")
ISO_DATE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")
PERU_DATE = re.compile(r"\b\d{1,2}/\d{1,2}/\d{4}\b")
SPANISH_DATE = re.compile(
    r"\b(\d{1,2})\s+de\s+"
    r"(enero|febrero|marzo|abril|mayo|junio|julio|agosto|"
    r"septiembre|setiembre|octubre|noviembre|diciembre)\s+de\s+(\d{4})\b",
    re.IGNORECASE,
)
SPANISH_MONTHS = {
    "enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5,
    "junio": 6, "julio": 7, "agosto": 8, "septiembre": 9,
    "setiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12,
}
HEADING = re.compile(r"^##\s+(.+?)\s*$")


def _identity(prefix, *parts):
    content = "\x1f".join(str(part or "") for part in parts)
    return f"{prefix}-{hashlib.sha256(content.encode('utf-8')).hexdigest()[:24]}"


def explicit_date(value):
    """Normalize only dates explicitly present in a fact or supplied field."""
    text = str(value or "")
    for pattern, date_format in ((ISO_DATE, "%Y-%m-%d"), (PERU_DATE, "%d/%m/%Y")):
        match = pattern.search(text)
        if match:
            try:
                return datetime.strptime(match.group(), date_format).date().isoformat()
            except ValueError:
                continue
    match = SPANISH_DATE.search(text)
    if match:
        try:
            day, month, year = match.groups()
            return datetime(int(year), SPANISH_MONTHS[month.lower()], int(day)).date().isoformat()
        except ValueError:
            return None
    return None


def case_facts(analysis, sources, case_id):
    private_ids = {source["source_id"] for source in sources
                   if source.get("source_scope") == "case" and source.get("case_id") == case_id}
    raw = analysis.get("hechos_estructurados") or analysis.get("hechos") or []
    records = []
    occurrences = {}
    for entry in raw if isinstance(raw, list) else []:
        item = entry if isinstance(entry, dict) else {"text": entry}
        original = str(item.get("text") or item.get("hecho") or item.get("description") or "").strip()
        if not original:
            continue
        requested = item.get("source_ids") if isinstance(item.get("source_ids"), list) else []
        source_ids = list(dict.fromkeys(source_id for source_id in
            [*requested, *SOURCE_MARKER.findall(original)] if source_id in private_ids))
        text = SOURCE_MARKER.sub("", original).strip()
        occurrences[text] = occurrences.get(text, 0) + 1
        status = item.get("status") if item.get("status") in {"alleged", "supported", "disputed", "unclear"} else "alleged"
        if status == "supported" and not source_ids:
            status = "alleged"
        records.append({"fact_id": _identity("FACT", case_id, text, occurrences[text]), "text": text,
                        "status": status, "source_ids": source_ids,
                        "date": explicit_date(item.get("date") or text),
                        "actors": item.get("actors") if isinstance(item.get("actors"), list) else []})
    return records


def case_issues(analysis, case_id):
    records = []
    raw = analysis.get("problemas_juridicos") or []
    occurrences = {}
    for entry in raw if isinstance(raw, list) else []:
        item = entry if isinstance(entry, dict) else {"text": entry}
        text = str(item.get("text") or item.get("issue") or "").strip()
        if text:
            occurrences[text] = occurrences.get(text, 0) + 1
            records.append({"issue_id": _identity("ISSUE", case_id, text, occurrences[text]), "text": text})
    return records


def case_timeline(facts):
    return [{"date": fact["date"], "description": fact["text"],
             "fact_id": fact["fact_id"], "source_ids": list(fact["source_ids"])}
            for fact in sorted(facts, key=lambda fact: fact.get("date") or "9999") if fact.get("date")]


def ground_links(items, issues, facts, sources, case_id):
    """Keep only issue/fact/source identifiers that belong to this result."""
    issue_ids = {item["issue_id"] for item in issues}
    fact_ids = {item["fact_id"] for item in facts}
    source_ids = {item["source_id"] for item in sources
                  if item.get("source_scope") == "public"
                  or (item.get("source_scope") == "case" and item.get("case_id") == case_id)}
    grounded = []
    for value in items if isinstance(items, list) else []:
        if not isinstance(value, dict):
            grounded.append(value)
            continue
        item = dict(value)
        if item.get("issue_id") not in issue_ids:
            item.pop("issue_id", None)
        for key, allowed in (("fact_ids", fact_ids), ("supporting_fact_ids", fact_ids),
                             ("source_ids", source_ids)):
            item[key] = [identifier for identifier in item.get(key, [])
                         if isinstance(identifier, str) and identifier in allowed] if isinstance(item.get(key), list) else []
        grounded.append(item)
    return grounded


def final_strategy(analysis, initial, arguments, evidence, risks, counterarguments):
    """Project existing findings into a final plan without a second LLM call."""
    fields = {
        "objective": analysis.get("pretension_principal"),
        "principal_line": initial.get("claim_strategy"),
        "supporting_arguments": arguments.get("main_arguments"),
        "priority_evidence": evidence.get("documentary_evidence") or evidence.get("available_evidence"),
        "risks_to_mitigate": risks.get("critical_risks") or risks.get("procedural_risks"),
        "opposing_positions": counterarguments.get("main_counterarguments"),
        "recommended_actions": initial.get("recommended_actions"),
        "missing_information": initial.get("missing_information") or analysis.get("informacion_faltante"),
    }
    return {key: value for key, value in fields.items() if value not in (None, "", [])}


def select_report_sources(public_sources, private_sources, case_id, limit=16, excerpt_chars=1800):
    """Reserve room for case documents and preserve the exact prompt excerpt."""
    limit = max(1, int(limit))
    private = [source for source in private_sources if source.get("case_id") == case_id]
    public = [source for source in public_sources if source.get("source_scope") == "public"]
    reserved = min(len(private), max(1, limit // 3))
    ordered = public[:limit - reserved] + private[:reserved]
    ordered += (public[limit - reserved:] + private[reserved:])[:max(0, limit - len(ordered))]
    selected, seen = [], set()
    for source in ordered:
        source_id = source.get("source_id")
        if not source_id or source_id in seen:
            continue
        seen.add(source_id)
        selected.append({**source, "excerpt": str(source.get("excerpt") or "")[:excerpt_chars]})
    return selected


def build_report_document(markdown, case_id, citations, sources, generated_at=None):
    """Parse the single generated report into a format-neutral document."""
    sections, title, heading, body = [], "INFORME JURÍDICO", None, []
    citation_by_label = {item.get("label"): item for item in citations if item.get("label")}

    def append_section():
        content = "\n".join(body).strip()
        if heading and content:
            present = [item for label, item in citation_by_label.items()
                       if re.search(rf"(?<!\w){re.escape(label)}(?!\w)", content)]
            sections.append({"id": _identity("SECTION", case_id, len(sections) + 1, heading),
                             "title": heading, "content": content,
                             "citation_ids": [item["citation_id"] for item in present]})

    for line in str(markdown or "").splitlines():
        if line.startswith("# ") and heading is None:
            title = line[2:].strip() or title
            continue
        match = HEADING.match(line)
        if match:
            append_section()
            heading, body = match.group(1), []
        elif heading is not None:
            body.append(line)
    append_section()
    if str(markdown or "").strip() and not sections:
        sections.append({"id": _identity("SECTION", case_id, 1, "Informe"),
                         "title": "Informe", "content": str(markdown).strip(),
                         "citation_ids": [item["citation_id"] for label, item in citation_by_label.items()
                                          if re.search(rf"(?<!\w){re.escape(label)}(?!\w)", str(markdown))]})
    cited_ids = {item["source_id"] for item in citations}
    return {"document_type": "analysis_report", "document_profile": "analysis_report",
            "title": title, "case_id": case_id,
            "generated_at": generated_at or datetime.now(timezone.utc).isoformat(),
            "sections": sections, "citations": list(citations),
            "sources": [source for source in sources if source.get("source_id") in cited_ids]}
