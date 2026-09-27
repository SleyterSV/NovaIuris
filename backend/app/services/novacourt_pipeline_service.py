"""Process-local jobs; every new task has an explicit, isolated case identity."""
import threading
from uuid import uuid4
from copy import deepcopy
from ..models.task import TaskManager, TaskStatus
from ..utils.case_contract import normalize_case_result
from ..utils.cancellation import OperationCancelled, check_cancelled
from ..utils.novacourt_graph import graph_result
from ..utils.novacourt_simulation import simulation_result

CASE_STAGES = (("intake", "Recepción"), ("documents", "Corpus documental del caso"), ("facts", "Hechos"),
    ("strategy", "Estrategia inicial"), ("research", "Investigación"),
    ("arguments", "Argumentos"), ("evidence", "Evidencia"),
    ("risks", "Riesgos"), ("counter_arguments", "Contraargumentos"), ("report", "Informe"))
COURT_STAGES = (("graph_build", "Grafo jurídico"), ("simulation", "Simulación"))

class NovaCourtPipelineService:
    def __init__(self, case_service, graph_service, simulation_service):
        self.case_service = case_service
        self.graph_service = graph_service
        self.simulation_service = simulation_service
        self.tasks = TaskManager()

    def start(self, case_text, case_id=None, tool="court", document_ids=None):
        case_id = case_id or str(uuid4())
        self.tasks.cleanup_old_tasks()
        task_id = self.tasks.create_task("legal_analysis", {"case_id": case_id, "tool": tool,
            "document_ids": list(document_ids or []), "owner": None})
        threading.Thread(target=self._run, args=(task_id, case_text), daemon=True).start()
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

    def _run(self, task_id, case_text):
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
            result = self.case_service.analyze_case(case_text, progress_callback=update,
                cancellation_token=token, case_id=case_id,
                document_ids=task.metadata.get("document_ids", []))
            check_cancelled(token)
            if not result.get("success"):
                raise RuntimeError("Case analysis failed")
            result = normalize_case_result(result)
            if result["case_id"] != case_id:
                raise ValueError("Case identity mismatch")
            partial.update(deepcopy(result))
            if tool == "court":
                for stage, field, action in (
                    ("graph_build", "graph", lambda: self.graph_service.build_for_case(result, cancellation_token=token)),
                    ("simulation", "simulation", lambda: self.simulation_service.simulate_for_case(result, case_text, cancellation_token=token))):
                    update(stage, "running")
                    try:
                        result[field] = action()
                    except OperationCancelled:
                        raise
                    except Exception:
                        result[field] = (graph_result if field == "graph" else simulation_result)("failed", message="No fue posible completar esta etapa.")
                    check_cancelled(token)
                    status = result[field]["status"]
                    if status in {"failed", "timeout"}:
                        warnings.append({"stage": stage, "code": status, "message": "El análisis principal permanece disponible."})
                    partial.update(deepcopy(result))
                    update(stage, "completed" if status == "ready" else "skipped" if status == "not_requested" else "failed")
            self.tasks.complete_task(task_id, result)
        except OperationCancelled:
            self.tasks.cancel_task(task_id)
        except Exception:
            self.tasks.fail_task(task_id, {"code": "ANALYSIS_FAILED", "message": "No fue posible completar el análisis jurídico."})
