"""Canonical, presentation-safe contract for synchronous case analysis."""

from typing import Any, Dict, List
from copy import deepcopy
from uuid import uuid4


def _as_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _as_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def normalize_case_result(result: Dict[str, Any]) -> Dict[str, Any]:
    """Add stable names without discarding the CaseService response."""
    if not isinstance(result, dict):
        return {}

    result = deepcopy(result)
    normalized = deepcopy(result)
    if not result.get("success"):
        return normalized

    metadata = deepcopy(_as_dict(result.get("metadata")))
    metadata.update({
        "contract_version": "1.0",
        "analysis_statistics": _as_dict(result.get("analysis_statistics")),
        "strategy_summary": _as_dict(result.get("strategy_summary")),
        "strategy_statistics": _as_dict(result.get("strategy_statistics")),
    })

    normalized.update({
        "analysis": _as_dict(result.get("analysis")),
        "summary": _as_dict(result.get("summary") or result.get("analysis_summary")),
        "strategy": _as_dict(result.get("strategy")),
        "research": _as_dict(result.get("research")),
        "arguments": _as_dict(result.get("arguments") or result.get("legal_arguments")),
        "evidence": _as_dict(result.get("evidence") or result.get("evidence_analysis")),
        "risks": _as_dict(result.get("risks") or result.get("risk_analysis")),
        "counter_arguments": _as_dict(result.get("counter_arguments")),
        "timeline": _as_list(result.get("timeline")),
        "report": result.get("report") if result.get("report") is not None else "",
        "citations": _as_list(result.get("citations")),
        "sources": _as_list(result.get("sources")),
        "metadata": metadata,
    })
    normalized['case_id'] = result.get('case_id') or metadata.get('case_id') or str(uuid4())
    normalized['metadata']['case_id'] = normalized['case_id']
    analysis = normalized['analysis']
    evidence = normalized['evidence']
    risks = normalized['risks']
    counter = normalized['counter_arguments']
    strategy = normalized['strategy']
    documents = _as_list(normalized['research'].get('documents'))
    mappings = (
        (analysis, {'facts':'hechos', 'issues':'problemas_juridicos', 'law':'normas_probables', 'observations':'informacion_faltante'}),
        (evidence, {'documents':'documentary_evidence', 'testimonies':'testimonial_evidence', 'expertReports':'expert_evidence', 'digitalEvidence':'digital_evidence', 'summary':'evidence_strength'}),
        (risks, {'procedural':'procedural_risks', 'evidentiary':'evidentiary_risks', 'legal':'legal_risks', 'strategic':'critical_risks', 'summary':'risk_level'}),
        (counter, {'procedural':'procedural_exceptions', 'evidence':'attacks_on_evidence', 'legal':'legal_defenses', 'jurisprudence':'attacks_on_jurisprudence', 'summary':'main_counterarguments'}),
        (strategy, {'strategy':'claim_strategy', 'actions':'recommended_actions', 'execution':'procedural_risks', 'recommendations':'recommended_actions', 'summary':'claim_strategy'}),
    )
    for target, aliases in mappings:
        for alias, original in aliases.items():
            if alias not in target:
                target[alias] = target.get(original, [])
    analysis.setdefault('summary', normalized['summary'])
    analysis.setdefault('jurisprudence', [d for d in documents if 'jurisprud' in str(d.get('tipo_documento', '')).lower()])
    strategy.setdefault('objective', analysis.get('pretension_principal', ''))
    normalized['summary'].setdefault('proceso', analysis.get('tipo_proceso', ''))
    normalized['summary'].setdefault('riesgo', risks.get('risk_level', ''))
    normalized['summary'].setdefault('evidencia', evidence.get('evidence_strength', ''))
    normalized['summary'].setdefault('documentos', len(documents))
    return normalized
