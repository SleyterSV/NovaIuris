"""Deterministic labels from the case's stated legal area."""

def resolve_court_roles(case_result):
    analysis = case_result.get("analysis") if isinstance(case_result.get("analysis"), dict) else {}
    summary = case_result.get("summary") if isinstance(case_result.get("summary"), dict) else {}
    area = " ".join(str(value or "") for value in (
        analysis.get("tipo_proceso"), analysis.get("legal_area"),
        summary.get("materia"), summary.get("rama"))).lower()
    if any(word in area for word in ("penal", "criminal")):
        return {"position_a": "Fiscalía", "position_b": "Defensa"}
    if any(word in area for word in ("civil", "laboral", "comercial", "arbitral")):
        return {"position_a": "Parte demandante", "position_b": "Parte demandada"}
    if "constitucional" in area:
        return {"position_a": "Parte recurrente", "position_b": "Parte recurrida"}
    if "administrativ" in area:
        return {"position_a": "Administrado", "position_b": "Entidad"}
    return {"position_a": "Parte promotora", "position_b": "Parte contraria"}
