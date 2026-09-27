"""Canonical, presentation-safe contract for synchronous case analysis."""

from typing import Any, Dict, List


def _as_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _as_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def normalize_case_result(result: Dict[str, Any]) -> Dict[str, Any]:
    """Add stable names without discarding the CaseService response."""
    if not isinstance(result, dict):
        return {}

    normalized = dict(result)
    if not result.get("success"):
        return normalized

    metadata = _as_dict(result.get("metadata"))
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
        "metadata": metadata,
    })
    return normalized
