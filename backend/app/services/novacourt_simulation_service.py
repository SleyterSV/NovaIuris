"""Integración diferida de LegalDebateSimulator para NovaCourt."""

import logging
from typing import Any, Callable, Dict, Optional

from ..config import Config
from ..utils.novacourt_simulation import NovaCourtSimulationOrchestrator


logger = logging.getLogger(__name__)


def get_legal_debate_simulator():
    """Importa el simulador existente sólo cuando NovaCourt lo necesita."""
    from .court_simulation import LegalDebateSimulator
    return LegalDebateSimulator


class NovaCourtSimulationService:
    def __init__(self, simulator_factory: Optional[Callable[[], Any]] = None):
        self.simulator_factory = simulator_factory or get_legal_debate_simulator

    def simulate_for_case(
        self, case_result: Dict[str, Any], case_text: str, cancellation_token=None
    ) -> Dict[str, Any]:
        orchestrator = NovaCourtSimulationOrchestrator(
            self.simulator_factory,
            enabled=Config.NOVACOURT_SIMULATION_ENABLED,
            timeout=Config.NOVACOURT_SIMULATION_TIMEOUT_SECONDS,
        )
        simulation = orchestrator.simulate(case_result, case_text, cancellation_token=cancellation_token)
        if simulation["status"] in {"failed", "timeout"}:
            logger.warning(
                "NovaCourt simulation finished with status=%s",
                simulation["status"],
            )
        return simulation
