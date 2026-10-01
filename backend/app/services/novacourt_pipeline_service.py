"""Process-local jobs; every new task has an explicit, isolated case identity."""
import threading
import re
from time import perf_counter
from uuid import uuid4
from copy import deepcopy
from ..models.task import TaskManager, TaskStatus
from ..utils.case_contract import normalize_case_result
from ..utils.cancellation import OperationCancelled, check_cancelled
from ..utils.novacourt_graph import graph_result
from ..utils.novacourt_simulation import simulation_result
from ..services.source_contracts import resolve_citations

CASE_STAGES = (("intake", "Recepción"), ("documents", "Corpus documental del caso"), ("facts", "Hechos"),
    ("strategy", "Estrategia inicial"), ("research", "Investigación"),
    ("arguments", "Argumentos"), ("evidence", "Evidencia"),
    ("risks", "Riesgos"), ("counter_arguments", "Contraargumentos"),
    ("final_strategy", "Estrategia final"), ("report", "Informe"),
    ("citations", "Verificación de citas"))
COURT_STAGES = (("graph_build", "Grafo jurídico"), ("simulation", "Simulación argumentativa"),
                ("court_citations", "Verificación de citas"))

class NovaCourtPipelineService:
    def __init__(self, case_service, graph_service, simulation_service):
        self.case_service = case_service
        self.graph_service = graph_service
        self.simulation_service = simulation_service
        self.tasks = TaskManager()

    def start(self, case_text, case_id=None, tool="court", document_ids=None, reuse_task_id=None):
        case_id = case_id or str(uuid4())
        self.tasks.cleanup_old_tasks()
        previous = None
        if reuse_task_id:
            previous = self.tasks.get_task(reuse_task_id)
            if (tool != "court" or previous is None or previous.task_type != "legal_analysis"
                    or previous.status != TaskStatus.COMPLETED or previous.metadata.get("tool") != "case"
                    or previous.metadata.get("case_id") != case_id or not isinstance(previous.result, dict)
                    or not previous.result.get("success") or previous.result.get("case_id") != case_id
                    or previous.result.get("case") != case_text
                    or set(previous.result.get("document_ids") or []) != set(document_ids or [])):
                raise ValueError("El análisis previo no corresponde al caso y documentos solicitados.")
        task_id = self.tasks.create_task("legal_analysis", {"case_id": case_id, "tool": tool,
            "document_ids": list(document_ids or []), "reuse_task_id": reuse_task_id, "owner": None})
        reused_result = deepcopy(previous.result) if previous else None
        threading.Thread(target=self._run, args=(task_id, case_text, reused_result), daemon=True).start()
        return task_id

    def status(self, task_id):
        task = self.tasks.get_task(task_id)
        if not task or task.task_type != "legal_analysis":
            return None
        data = task.to_dict()
        detail = data["progress_detail"]
        data.update(case_id=data["metadata"]["case_id"], tool=data["metadata"]["tool"],
                    stage=detail.get("current_stage"), stages=detail.get("stages", []),
                    partial_result=detail.get("partial_result", {}), final_result=data["result"],
                    warnings=detail.get("warnings", []))
        return data

    def _run(self, task_id, case_text, reused_result=None):
        task = self.tasks.get_task(task_id)
        token = self.tasks.cancellation_token(task_id)
        case_id, tool = task.metadata["case_id"], task.metadata["tool"]
        stages = [{"id": key, "label": label, "status": "pending"}
                  for key, label in CASE_STAGES + (COURT_STAGES if tool == "court" else ())]
        lookup = {item["id"]: item for item in stages}
        lock = threading.RLock()
        partial, warnings = {}, []
        def update(stage, status):
            check_cancelled(token)
            with lock:
                lookup[stage]["status"] = status
                done = sum(item["status"] in {"completed", "failed", "skipped"} for item in stages)
                self.tasks.update_task(task_id, status=TaskStatus.PROCESSING,
                    progress=int(done * 100 / len(stages)), message=lookup[stage]["label"],
                    progress_detail={"stages": deepcopy(stages), "current_stage": stage,
                                     "partial_result": deepcopy(partial), "warnings": list(warnings),
                                     "progress_kind": "completed_stages"})
        try:
            started = perf_counter()
            if reused_result:
                result = reused_result
                for stage, _ in CASE_STAGES:
                    update(stage, "skipped")
            else:
                result = self.case_service.analyze_case(case_text, progress_callback=update,
                    cancellation_token=token, case_id=case_id,
                    document_ids=task.metadata.get("document_ids", []))
            check_cancelled(token)
            if not result.get("success"):
                raise RuntimeError("Case analysis failed")
            result = normalize_case_result(result)
            if result["case_id"] != case_id:
                raise ValueError("Case identity mismatch")
            if set(result.get("document_ids") or []) != set(task.metadata.get("document_ids") or []):
                raise ValueError("Document identity mismatch")
            if any(source.get("source_scope") == "case" and source.get("case_id") != case_id
                   for source in result.get("sources", []) + result.get("sources_used", []) if isinstance(source, dict)):
                raise ValueError("Private source identity mismatch")
            warnings.extend(result.get("warnings", []))
            partial.update(deepcopy(result))
            if tool == "court":
                timings = {}
                def graph_snapshot(snapshot):
                    check_cancelled(token)
                    if snapshot.get("case_id") != case_id:
                        raise ValueError("Graph snapshot case identity mismatch")
                    with lock:
                        partial["graph"] = deepcopy(snapshot)
                    update("graph_build", "running")
                for stage, field, action in (
                    ("graph_build", "graph", lambda: self.graph_service.build_for_case(
                        result, cancellation_token=token, snapshot_callback=graph_snapshot)),
                    ("simulation", "simulation", lambda: self.simulation_service.simulate_for_case(result, case_text, cancellation_token=token))):
                    update(stage, "running")
                    stage_started = perf_counter()
                    try:
                        result[field] = action()
                    except OperationCancelled:
                        raise
                    except Exception:
                        if field == "graph" and isinstance(partial.get("graph"), dict):
                            previous = partial["graph"]
                            result[field] = graph_result("failed", graph_id=previous.get("graph_id"),
                                case_id=case_id, version=previous.get("version", 0) + 1,
                                stage="failed", nodes=previous.get("nodes"), edges=previous.get("edges"),
                                message="No fue posible completar esta etapa.",
                                warnings=[{"code": "FAILED", "message": "Grafo parcial"}])
                        else:
                            result[field] = (graph_result if field == "graph" else simulation_result)(
                                "failed", message="No fue posible completar esta etapa.")
                    check_cancelled(token)
                    timings[stage] = round((perf_counter() - stage_started) * 1000)
                    if not isinstance(result[field], dict) or result[field].get("status") not in {
                            "ready", "failed", "timeout", "not_requested"}:
                        result[field] = (graph_result if field == "graph" else simulation_result)(
                            "failed", message="La etapa no produjo un resultado válido.")
                    if result[field].get("case_id") not in (None, case_id):
                        result[field] = (graph_result if field == "graph" else simulation_result)("failed", message="Identidad de caso no válida.")
                    result[field]["case_id"] = case_id
                    status = result[field]["status"]
                    if status in {"failed", "timeout"}:
                        warnings.append({"stage": stage, "code": status, "message": "El análisis principal permanece disponible."})
                    partial.update(deepcopy(result))
                    update(stage, "completed" if status == "ready" else "skipped" if status == "not_requested" else "failed")
                update("court_citations", "running")
                simulation = result["simulation"]
                citation_failed = False
                if simulation["status"] != "ready":
                    simulation = simulation_result(simulation["status"], message=simulation.get("message"))
                    simulation["case_id"] = case_id
                    result["simulation"] = simulation
                if simulation["status"] == "ready":
                    available = result.get("sources", []) + result.get("sources_used", [])
                    separator = f"\n\nCOURT_SECTION_BOUNDARY_{uuid4().hex}\n\n"
                    sections = ("prosecutor", "defense", "judge")
                    if any(not isinstance(simulation.get(section), dict) or
                           not isinstance(simulation[section].get("content"), str) or
                           not simulation[section]["content"].strip() for section in sections):
                        simulation = simulation_result("failed", message="La simulación no produjo posiciones válidas.")
                        simulation["case_id"] = case_id
                        result["simulation"] = simulation
                if simulation["status"] == "ready":
                    markers = {section: set(re.findall(r"\[(SRC-[A-Za-z0-9_-]{6,80})\]",
                        simulation.get(section, {}).get("content", ""))) for section in sections}
                    joined = separator.join(simulation.get(section, {}).get("content", "") for section in sections)
                    try:
                        resolved = resolve_citations(joined, available, case_id=case_id)
                    except Exception:
                        citation_failed = True
                        simulation = simulation_result("failed", message="No fue posible verificar las citas de la simulación.")
                        simulation["case_id"] = case_id
                        result["simulation"] = simulation
                        warnings.append({"stage": "court_citations", "code": "CITATION_VALIDATION_FAILED",
                                         "message": "La simulación no pudo verificarse; el análisis principal permanece disponible."})
                if simulation["status"] == "ready":
                    for section, content in zip(sections, resolved["answer"].split(separator)):
                        simulation.setdefault(section, {})["content"] = content
                    for section in sections:
                        simulation[section]["citations"] = [citation for citation in resolved["citations"]
                            if citation["source_id"] in markers[section]]
                    simulation["sources"] = resolved["sources_used"]
                    simulation["citations"] = resolved["citations"]
                    simulation["warnings"] = resolved["warnings"]
                    warnings.extend(resolved["warnings"])
                    simulation["projection"] = {}
                    simulation["judicial_analysis"] = dict(simulation.get("judge", {}))
                    simulation["decision"] = {"label": "Decisión simulada", "content": simulation.get("judge", {}).get("content", "")}
                    simulation["position_a"] = dict(simulation.get("prosecutor", {}))
                    simulation["position_b"] = dict(simulation.get("defense", {}))
                    simulation["roles"] = {"position_a": simulation["position_a"].get("role_label", "Parte promotora"),
                                           "position_b": simulation["position_b"].get("role_label", "Parte contraria")}
                result["court_status"] = "completed" if all(result[field]["status"] == "ready" for field in ("graph", "simulation")) else "partial"
                result["court_report_document"] = {"document_type": "court_simulation", "case_id": case_id,
                    "title": "Simulación jurídica argumentativa", "sections": [
                        {"id": section, "title": simulation.get(section, {}).get("role_label", title),
                         "content": simulation.get(section, {}).get("content", ""),
                         "citation_ids": [item["citation_id"] for item in simulation.get(section, {}).get("citations", [])]}
                        for section, title in (("prosecutor", "Posición promotora"), ("defense", "Posición contraria"),
                                               ("judge", "Decisión simulada")) if simulation.get(section, {}).get("content")],
                    "citations": simulation.get("citations", []), "sources": simulation.get("sources", [])}
                result.setdefault("metadata", {}).update({"case_reused": bool(reused_result), "graph_status": result["graph"]["status"],
                    "simulation_status": simulation["status"], "sources_count": len(simulation.get("sources", [])),
                    "citations_count": len(simulation.get("citations", [])), "court_timings_ms": timings,
                    "court_total_duration_ms": round((perf_counter() - started) * 1000)})
                result["warnings"] = list(warnings)
                partial.update(deepcopy(result))
                update("court_citations", "failed" if citation_failed else
                       "completed" if simulation["status"] == "ready" else "skipped")
            check_cancelled(token)
            self.tasks.complete_task(task_id, result)
        except OperationCancelled:
            self.tasks.cancel_task(task_id)
        except Exception:
            self.tasks.fail_task(task_id, {"code": "ANALYSIS_FAILED", "message": "No fue posible completar el análisis jurídico."})
