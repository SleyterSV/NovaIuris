"""LOCAL SYNTHETIC BENCHMARK; no external provider clients are created."""
import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.services.novacourt_pipeline_service import NovaCourtPipelineService
from app.utils.novacourt_graph import NovaCourtGraphOrchestrator
from app.utils.novacourt_simulation import build_simulation_context


class Case:
    calls = 0

    def analyze_case(self, text, *, progress_callback, cancellation_token, case_id, document_ids):
        self.calls += 1
        time.sleep(0.015)
        progress_callback("intake", "completed")
        count = int(text.split("-")[-1])
        source = {"source_id": "SRC-LOCAL001", "source_scope": "public", "source_type": "legislation",
                  "title": "Fuente local", "excerpt": "Extracto de prueba"}
        return {"success": True, "case_id": case_id, "case": text, "document_ids": document_ids,
                "facts": [{"fact_id": f"F-{i}", "text": f"Hecho {i}", "source_ids": ["SRC-LOCAL001"]}
                          for i in range(count)],
                "issues": [{"issue_id": "I-1", "text": "Cuestión"}],
                "evidence": {"evidence_links": [{"text": "Prueba", "fact_id": "F-0",
                                                "source_ids": ["SRC-LOCAL001"]}]},
                "arguments": {"main_arguments": [{"text": "Tesis", "issue_id": "I-1",
                                                  "source_ids": ["SRC-LOCAL001"]}]},
                "sources": [source], "sources_used": [source]}


class Builder:
    def __init__(self, metrics, delay):
        self.metrics, self.delay = metrics, delay

    def create_graph(self, name):
        self.metrics["graph_operations"] += 1
        return "synthetic-graph"

    def set_ontology(self, graph_id, ontology):
        self.metrics["graph_operations"] += 1

    def add_text_batches(self, graph_id, episodes, batch_size, cancellation_token=None):
        self.metrics["graph_operations"] += (len(episodes) + batch_size - 1) // batch_size
        self.metrics["graph_input_chars"] = sum(map(len, episodes))
        self.metrics["batches"] = (len(episodes) + batch_size - 1) // batch_size
        self.metrics["episodes"] = len(episodes)
        time.sleep(self.delay)
        return [f"episode-{i}" for i in range(len(episodes))]

    def _wait_for_episodes(self, episode_ids, **kwargs):
        self.metrics["graph_polls"] += len(episode_ids)

    def get_graph_data(self, graph_id, **kwargs):
        self.metrics["graph_operations"] += 1
        return {"nodes": [], "edges": []}


class Graph:
    def __init__(self, metrics, delay):
        self.metrics, self.delay = metrics, delay

    def build_for_case(self, result, cancellation_token=None, snapshot_callback=None):
        graph = NovaCourtGraphOrchestrator(lambda: Builder(self.metrics, self.delay), enabled=True,
            timeout=5, poll_interval=0.01, chunk_size=100, chunk_overlap=0, batch_size=3)
        def snapshot(value):
            self.metrics["snapshots"] += 1
            snapshot_callback(value)
        return graph.build(result, cancellation_token=cancellation_token, snapshot_callback=snapshot)


class Simulation:
    def __init__(self, metrics, delay):
        self.metrics, self.delay = metrics, delay

    def simulate_for_case(self, result, text, cancellation_token=None):
        context = build_simulation_context(result, text)
        self.metrics["simulation_context_chars"] = len(context)
        self.metrics["provider_logical_calls"] += 3
        time.sleep(self.delay)
        return {"status": "ready", "case_id": result["case_id"],
                "prosecutor": {"content": "Tesis [SRC-LOCAL001]"},
                "defense": {"content": "Objeción [SRC-LOCAL001]"},
                "judge": {"content": "Decisión [SRC-LOCAL001]"}}


def await_result(pipeline, task_id):
    polls = 0
    while True:
        task = pipeline.status(task_id)
        polls += 1
        if task["status"] in ("completed", "failed", "cancelled"):
            return task, polls
        time.sleep(0.002)


def run(delay):
    rows = []
    for label, count, reused in (("small_reused", 2, True), ("medium_reused", 12, True),
                                  ("document_reused", 32, True), ("new_case", 12, False)):
        metrics = {key: 0 for key in ("graph_operations", "graph_polls", "graph_input_chars",
            "batches", "episodes", "snapshots", "simulation_context_chars", "provider_logical_calls")}
        case = Case()
        pipeline = NovaCourtPipelineService(case, Graph(metrics, delay), Simulation(metrics, delay))
        text = f"fixture-{count}"
        case_id = f"BENCH-{label}"
        reuse_id = None
        if reused:
            reuse_id = pipeline.start(text, case_id, tool="case")
            prior, _ = await_result(pipeline, reuse_id)
            assert prior["status"] == "completed"
        before_calls = case.calls
        start = time.perf_counter()
        task_id = pipeline.start(text, case_id, reuse_task_id=reuse_id)
        task, polls = await_result(pipeline, task_id)
        assert task["status"] == "completed", task
        result = task["final_result"]
        rows.append({"scenario": label, "case_reused": reused,
                     "wall_ms": round((time.perf_counter() - start) * 1000, 1),
                     "case_calls": case.calls - before_calls, "status_polls": polls,
                     "court_timings_ms": result["metadata"].get("court_timings_ms"),
                     "court_total_duration_ms": result["metadata"].get("court_total_duration_ms"),
                     **metrics})
    return rows


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--delay", type=float, default=0.04)
    args = parser.parse_args()
    print("LOCAL SYNTHETIC BENCHMARK")
    print(json.dumps(run(args.delay), indent=2))
