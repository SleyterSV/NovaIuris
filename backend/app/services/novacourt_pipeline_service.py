"""Process-local jobs; every new task has an explicit, isolated case identity."""
import threading
import re
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
from time import perf_counter
from uuid import uuid4
from copy import deepcopy
from ..models.task import TaskManager, TaskStatus
from ..utils.case_contract import normalize_case_result
from ..utils.cancellation import OperationCancelled, check_cancelled
from ..utils.cancellation import CancellationToken
from ..config import Config
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
    def __init__(self, case_service, graph_service, simulation_service, task_manager=None):
        self.case_service = case_service
        self.graph_service = graph_service
        self.simulation_service = simulation_service
        self.tasks = task_manager or TaskManager()

    def start(self, case_text, case_id=None, tool="court", document_ids=None, reuse_task_id=None, owner_id=None):
        case_id = case_id or str(uuid4())
        self.tasks.cleanup_old_tasks()
        previous = None
        if reuse_task_id:
            previous = self.tasks.get_task(reuse_task_id)
            if (tool != "court" or previous is None or previous.task_type != "legal_analysis"
                    or previous.status != TaskStatus.COMPLETED or previous.metadata.get("tool") != "case"
                    or previous.metadata.get("owner_id") != owner_id
                    or previous.metadata.get("case_id") != case_id or not isinstance(previous.result, dict)
                    or not previous.result.get("success") or previous.result.get("case_id") != case_id
                    or previous.result.get("case") != case_text
                    or set(previous.result.get("document_ids") or []) != set(document_ids or [])):
                raise ValueError("El análisis previo no corresponde al caso y documentos solicitados.")
        task_id = self.tasks.create_task("legal_analysis", {"case_id": case_id, "tool": tool,
            "document_ids": list(document_ids or []), "reuse_task_id": reuse_task_id, "owner_id": owner_id})
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
                    owner_id=data["metadata"].get("owner_id"),
                    stage=detail.get("current_stage"), stages=detail.get("stages", []),
                    partial_result=detail.get("partial_result", {}), final_result=data["result"],
                    warnings=detail.get("warnings", []))
        return data

    def _run(self, task_id, case_text, reused_result=None):
        task = self.tasks.get_task(task_id)
        task_token = self.tasks.cancellation_token(task_id)
        case_id, tool = task.metadata["case_id"], task.metadata["tool"]
        token = CancellationToken(parent=task_token, timeout=Config.NOVACOURT_TASK_TIMEOUT_SECONDS) if tool == "court" else task_token
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
            case_started = started
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
                timings = {"case": round((perf_counter() - case_started) * 1000)}
                snapshot_version = -1
                def graph_snapshot(snapshot):
                    nonlocal snapshot_version
                    check_cancelled(token)
                    if snapshot.get("case_id") != case_id:
                        raise ValueError("Graph snapshot case identity mismatch")
                    with lock:
                        version = snapshot.get("version", 0)
                        if version <= snapshot_version:
                            return
                        snapshot_version = version
                        partial["graph"] = deepcopy(snapshot)
                        update("graph_build", "running")
                # Both branches only read the normalized CaseResult. Neither receives
                # the mutable aggregate that the coordinator publishes to TaskManager.
                branches = (
                    ("graph_build", "graph", lambda input_result: self.graph_service.build_for_case(
                        input_result, cancellation_token=token, snapshot_callback=graph_snapshot)),
                    ("simulation", "simulation", lambda input_result: self.simulation_service.simulate_for_case(
                        input_result, case_text, cancellation_token=token)))
                executor = ThreadPoolExecutor(max_workers=2)
                pending = {}
                try:
                    for stage, field, action in branches:
                        check_cancelled(token)
                        branch_input = deepcopy(result)
                        started_branch = perf_counter()
                        future = executor.submit(action, branch_input)
                        pending[future] = (stage, field, started_branch)
                        update(stage, "running")
                    while pending:
                        check_cancelled(token)
                        completed, _ = wait(pending, timeout=0.05, return_when=FIRST_COMPLETED)
                        for future in completed:
                            stage, field, started_branch = pending.pop(future)
                            try:
                                value = future.result()
                            except OperationCancelled:
                                raise
                            except Exception:
                                value = None
                            check_cancelled(token)
                            timings[stage] = round((perf_counter() - started_branch) * 1000)
                            if not isinstance(value, dict) or value.get("status") not in {
                                    "ready", "empty", "failed", "timeout", "not_requested"}:
                                if field == "graph" and isinstance(partial.get("graph"), dict):
                                    previous = partial["graph"]
                                    value = graph_result("failed", graph_id=previous.get("graph_id"),
                                        case_id=case_id, version=previous.get("version", 0) + 1,
                                        stage="failed", nodes=previous.get("nodes"), edges=previous.get("edges"),
                                        message="No fue posible completar esta etapa.",
                                        warnings=[{"code": "FAILED", "message": "Grafo parcial"}])
                                else:
                                    value = (graph_result if field == "graph" else simulation_result)(
                                        "failed", message="No fue posible completar esta etapa.",
                                        metadata={"failed_stage": stage, "reason": "unexpected_branch_result"})
                            if value.get("case_id") not in (None, case_id):
                                value = (graph_result if field == "graph" else simulation_result)(
                                    "failed", message="Identidad de caso no válida.")
                            value["case_id"] = case_id
                            result[field] = value
                            status = value["status"]
                            if status in {"failed", "timeout"}:
                                warnings.append({"stage": stage, "code": status,
                                                 "message": "Esta etapa no pudo finalizar."})
                            partial[field] = deepcopy(value)
                            update(stage, "completed" if status in {"ready", "empty"} else
                                   "skipped" if status == "not_requested" else "failed")
                finally:
                    executor.shutdown(wait=False, cancel_futures=True)
                update("court_citations", "running")
                check_cancelled(token)
                citation_started = perf_counter()
                simulation = result["simulation"]
                citation_failed = False
                if simulation["status"] != "ready":
                    simulation = simulation_result(simulation["status"], message=simulation.get("message"),
                                                   metadata=simulation.get("metadata"))
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
                                         "message": "La simulación no pudo verificarse."})
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
                report_started = perf_counter()
                result["court_report_document"] = {"document_type": "court_simulation", "case_id": case_id,
                    "title": "Simulación jurídica argumentativa", "sections": [
                        {"id": section, "title": simulation.get(section, {}).get("role_label", title),
                         "content": simulation.get(section, {}).get("content", ""),
                         "citation_ids": [item["citation_id"] for item in simulation.get(section, {}).get("citations", [])]}
                        for section, title in (("prosecutor", "Posición promotora"), ("defense", "Posición contraria"),
                                               ("judge", "Decisión simulada")) if simulation.get(section, {}).get("content")],
                    "citations": simulation.get("citations", []), "sources": simulation.get("sources", [])}
                court_report_status = "ready" if result["court_report_document"]["sections"] and simulation["status"] == "ready" else "partial"
                result.setdefault("metadata", {}).update({"case_reused": bool(reused_result), "graph_status": result["graph"]["status"],
                    "simulation_status": simulation["status"], "sources_count": len(simulation.get("sources", [])),
                    "citations_count": len(simulation.get("citations", [])), "court_timings_ms": timings,
                    "case_duration_ms": timings["case"], "graph_duration_ms": timings["graph_build"],
                    "simulation_duration_ms": timings["simulation"],
                    "citation_duration_ms": round((perf_counter() - citation_started) * 1000),
                    "simulation_provider_call_count": simulation.get("metadata", {}).get("provider_call_count"),
                    "graph_operation_count": result["graph"].get("metadata", {}).get("operation_count"),
                    "graph_poll_count": result["graph"].get("metadata", {}).get("poll_count"),
                    "graph_wait_duration_ms": result["graph"].get("metadata", {}).get("graph_wait_duration_ms"),
                    "graph_batch_count": result["graph"].get("metadata", {}).get("batch_count"),
                    "graph_stage": result["graph"].get("stage"),
                    "simulation_retry_count": simulation.get("metadata", {}).get("retry_count"),
                    "simulation_failed_stage": simulation.get("metadata", {}).get("failed_stage"),
                    "court_report_status": court_report_status,
                    "report_duration_ms": round((perf_counter() - report_started) * 1000),
                    "graph_snapshot_count": result["graph"].get("metadata", {}).get("snapshot_count"),
                    "simulation_context_characters": simulation.get("metadata", {}).get("context_characters"),
                    "graph_input_characters": result["graph"].get("metadata", {}).get("input_characters"),
                    "case_source_count": sum(1 for source in result.get("sources", [])
                                             if isinstance(source, dict) and source.get("source_scope") == "case"),
                    "court_total_duration_ms": round((perf_counter() - started) * 1000)})
                result["warnings"] = list(warnings)
                partial.update(deepcopy(result))
                update("court_citations", "failed" if citation_failed else
                       "completed" if simulation["status"] == "ready" else "skipped")
            check_cancelled(token)
            self.tasks.complete_task(task_id, result)
        except OperationCancelled:
            if task_token.is_cancelled() or token._event.is_set():
                self.tasks.cancel_task(task_id)
            elif tool == "court" and isinstance(locals().get("result"), dict) and result.get("success"):
                result["graph"] = result.get("graph") or partial.get("graph") or graph_result("timeout", case_id=case_id)
                simulation_at_deadline = result.get("simulation") or simulation_result("timeout")
                if simulation_at_deadline.get("status") == "ready" and "citations" not in simulation_at_deadline:
                    simulation_at_deadline = simulation_result("timeout", message="No se completó la verificación de citas.")
                result["simulation"] = simulation_at_deadline
                result["court_status"] = "partial"
                result["court_report_document"] = {"document_type": "court_simulation", "case_id": case_id,
                                                   "title": "Simulación jurídica argumentativa", "sections": [],
                                                   "citations": [], "sources": []}
                result.setdefault("warnings", []).append({"code": "COURT_TIMEOUT", "message": "La tarea superó el tiempo disponible."})
                self.tasks.complete_task(task_id, result)
            else:
                self.tasks.fail_task(task_id, {"code": "COURT_TIMEOUT", "message": "La tarea superó el tiempo disponible."})
        except Exception:
            self.tasks.fail_task(task_id, {"code": "ANALYSIS_FAILED", "message": "No fue posible completar el análisis jurídico."})
