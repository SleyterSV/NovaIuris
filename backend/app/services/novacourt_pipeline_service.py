import threading
from ..models.task import TaskManager, TaskStatus
from ..utils.case_contract import normalize_case_result

STAGES = (("intake","Recepción del expediente"),("facts","Análisis de hechos"),("legal_structure","Estructuración jurídica"),("research","Investigación jurídica"),("evidence","Análisis probatorio"),("risks","Análisis de riesgos"),("graph_build","Construcción del grafo jurídico"),("relations","Relaciones jurídicas"),("simulation","Simulación multiagente"),("projection","Proyección judicial"),("report","Informe final"))

class NovaCourtPipelineService:
    def __init__(self, case_service, graph_service, simulation_service):
        self.case_service, self.graph_service, self.simulation_service = case_service, graph_service, simulation_service
        self.tasks = TaskManager()
    def start(self, case_text):
        task_id = self.tasks.create_task("novacourt_analysis")
        threading.Thread(target=self._run, args=(task_id, case_text), daemon=True).start()
        return task_id
    def status(self, task_id):
        task = self.tasks.get_task(task_id)
        return task.to_dict() if task and task.task_type == "novacourt_analysis" else None
    def _run(self, task_id, case_text):
        stages = [{"id": key, "label": label, "status": "pending"} for key, label in STAGES]
        lookup = {item["id"]: item for item in stages}
        def update(stage, status):
            lookup[stage]["status"] = status
            done = sum(item["status"] in {"completed","failed","skipped"} for item in stages)
            progress = max(self.tasks.get_task(task_id).progress, int(done * 100 / len(stages)))
            self.tasks.update_task(task_id, status=TaskStatus.PROCESSING, progress=progress, message=lookup[stage]["label"], progress_detail={"stages": stages, "current_stage": stage})
        try:
            update("intake","running"); update("intake","completed")
            result = self.case_service.analyze_case(case_text, progress_callback=update)
            if not result.get("success"): raise RuntimeError()
            result = normalize_case_result(result)
            update("graph_build","running"); result["graph"] = self.graph_service.build_for_case(result)
            graph_ok = result["graph"]["status"] == "ready"
            update("graph_build","completed" if graph_ok else "failed"); update("relations","completed" if graph_ok else "skipped")
            update("simulation","running"); result["simulation"] = self.simulation_service.simulate_for_case(result, case_text)
            simulation_ok = result["simulation"]["status"] == "ready"
            update("simulation","completed" if simulation_ok else "failed"); update("projection","completed" if simulation_ok else "skipped")
            self.tasks.complete_task(task_id, result); self.tasks.update_task(task_id, progress_detail={"stages": stages, "current_stage": "report"})
        except Exception:
            self.tasks.fail_task(task_id, "No fue posible completar el procesamiento judicial."); self.tasks.update_task(task_id, progress_detail={"stages": stages})
