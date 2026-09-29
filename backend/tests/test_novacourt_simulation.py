import importlib.util
from pathlib import Path
import time
import unittest


from app.utils import novacourt_simulation as SIMULATION


def make_orchestrator(factory, enabled=True, timeout=1):
    return SIMULATION.NovaCourtSimulationOrchestrator(
        factory,
        enabled=enabled,
        timeout=timeout,
    )


class ReadySimulator:
    def __init__(self):
        self.context = ""

    def simulate_case(self, context, cancellation_token=None):
        self.context = context
        return {
            "session_id": "audiencia-1",
            "base_legal": "Artículo aplicable",
            "fiscal": "Postura de Fiscalía",
            "defensa": "Postura de Defensa",
            "juez": "Resolución del Juzgado",
            "metricas": {"riesgo_procesal": 40},
        }


class NovaCourtSimulationTests(unittest.TestCase):
    def setUp(self):
        self.case = {
            "success": True,
            "summary": {"materia": "laboral"},
            "arguments": {"principal": "reposición"},
            "evidence": {"documento": "contrato"},
            "graph": {
                "status": "ready",
                "graph_id": "zep-1",
                "nodes": [{"uuid": "n-1"}],
                "edges": [{"uuid": "e-1"}],
            },
            "internal_only": "no debe llegar al simulador",
        }
        self.case_text = "El trabajador solicita reposición por despido sin causa suficiente."

    def test_canonical_contract_is_adapted_and_simulator_output_is_structured(self):
        simulator = ReadySimulator()
        result = make_orchestrator(lambda: simulator).simulate(
            self.case, self.case_text
        )

        self.assertEqual(result["status"], "ready")
        self.assertEqual(result["prosecutor"]["content"], "Postura de Fiscalía")
        self.assertEqual(result["defense"]["content"], "Postura de Defensa")
        self.assertEqual(result["judge"]["content"], "Resolución del Juzgado")
        self.assertEqual(result["projection"], {})
        self.assertEqual(result["decision"]["label"], "Decisión simulada")
        self.assertEqual(result["decision"]["content"], "Resolución del Juzgado")
        self.assertEqual(result["prosecutor"]["role_label"], "Parte demandante")
        self.assertEqual(result["defense"]["role_label"], "Parte demandada")
        self.assertEqual(result["metadata"]["metrics"], {})
        self.assertEqual(result["metadata"]["session_id"], "audiencia-1")
        self.assertIn("Grafo jurídico disponible", simulator.context)
        self.assertIn("Argumentos", simulator.context)
        self.assertNotIn("internal_only", simulator.context)

    def test_simulation_failure_keeps_existing_case_and_graph_data(self):
        def failing_factory():
            raise RuntimeError("detalle interno secreto")

        result = make_orchestrator(failing_factory).simulate(
            self.case, self.case_text
        )

        self.assertEqual(result["status"], "failed")
        self.assertNotIn("secreto", result["message"])
        self.assertEqual(self.case["graph"]["graph_id"], "zep-1")
        self.assertEqual(self.case["arguments"]["principal"], "reposición")

    def test_failed_graph_does_not_block_simulation(self):
        simulator = ReadySimulator()
        self.case["graph"] = {"status": "failed", "nodes": [], "edges": []}

        result = make_orchestrator(lambda: simulator).simulate(
            self.case, self.case_text
        )

        self.assertEqual(result["status"], "ready")
        self.assertNotIn("Grafo jurídico disponible", simulator.context)

    def test_timeout_is_controlled(self):
        class SlowSimulator:
            @staticmethod
            def simulate_case(context, cancellation_token=None):
                time.sleep(0.05)
                return {}

        result = make_orchestrator(SlowSimulator, timeout=0.001).simulate(
            self.case, self.case_text
        )

        self.assertEqual(result["status"], "timeout")
        self.assertEqual(result["prosecutor"], {})

    def test_disabled_simulation_is_not_requested(self):
        result = make_orchestrator(ReadySimulator, enabled=False).simulate(
            self.case, self.case_text
        )
        self.assertEqual(result["status"], "not_requested")


if __name__ == "__main__":
    unittest.main()
