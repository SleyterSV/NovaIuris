"""Integración del grafo jurídico de Zep exclusivamente para NovaCourt."""

import logging
from typing import Any, Callable, Dict, Optional

from ..config import Config
from ..utils.novacourt_graph import NovaCourtGraphOrchestrator
from .graph_builder import GraphBuilderService


logger = logging.getLogger(__name__)


class NovaCourtGraphService:
    """Construye el grafo sin convertir un fallo de Zep en fallo del análisis."""

    def __init__(self, builder_factory: Optional[Callable[[], Any]] = None):
        self.builder_factory = builder_factory or GraphBuilderService

    def build_for_case(self, case_result: Dict[str, Any], cancellation_token=None) -> Dict[str, Any]:
        orchestrator = NovaCourtGraphOrchestrator(
            self.builder_factory,
            enabled=Config.NOVACOURT_GRAPH_ENABLED,
            timeout=Config.NOVACOURT_GRAPH_TIMEOUT_SECONDS,
            poll_interval=Config.NOVACOURT_GRAPH_POLL_INTERVAL_SECONDS,
            chunk_size=Config.DEFAULT_CHUNK_SIZE,
            chunk_overlap=Config.DEFAULT_CHUNK_OVERLAP,
            batch_size=Config.NOVACOURT_GRAPH_BATCH_SIZE,
        )
        graph = orchestrator.build(case_result, cancellation_token=cancellation_token)
        if graph["status"] in {"failed", "timeout"}:
            logger.warning("NovaCourt graph finished with status=%s", graph["status"])
        return graph
