"""Contrato y orquestación agnóstica para el grafo de NovaCourt."""

from __future__ import annotations

import json
from typing import Any, Callable, Dict


LEGAL_ONTOLOGY: Dict[str, Any] = {
    "entity_types": [
        {"name": "Parte", "description": "Persona, entidad u órgano que interviene en el caso."},
        {"name": "Hecho", "description": "Hecho relevante para la controversia."},
        {"name": "Pretension", "description": "Solicitud o pretensión jurídica de una parte."},
        {"name": "Norma", "description": "Norma, precedente o fuente jurídica invocada."},
        {"name": "Argumento", "description": "Argumento jurídico formulado en el análisis."},
        {"name": "Evidencia", "description": "Elemento probatorio o documento relevante."},
        {"name": "Riesgo", "description": "Riesgo, contingencia o punto débil identificado."},
        {"name": "Actuacion", "description": "Actuación procesal o hito temporal."},
    ],
    "edge_types": [
        {"name": "sustenta", "description": "Un elemento sustenta otro.", "source_targets": [{"source": "Evidencia", "target": "Argumento"}, {"source": "Norma", "target": "Argumento"}, {"source": "Hecho", "target": "Argumento"}]},
        {"name": "invoca", "description": "Una parte invoca una norma o argumento.", "source_targets": [{"source": "Parte", "target": "Norma"}, {"source": "Parte", "target": "Argumento"}]},
        {"name": "contradice", "description": "Un elemento contradice otro.", "source_targets": [{"source": "Argumento", "target": "Argumento"}, {"source": "Evidencia", "target": "Hecho"}]},
        {"name": "afecta", "description": "Un riesgo afecta una pretensión o argumento.", "source_targets": [{"source": "Riesgo", "target": "Pretension"}, {"source": "Riesgo", "target": "Argumento"}]},
        {"name": "relaciona", "description": "Relaciona actuaciones, hechos y pretensiones.", "source_targets": [{"source": "Actuacion", "target": "Hecho"}, {"source": "Hecho", "target": "Pretension"}]},
    ],
}

_CONTEXT_FIELDS = (
    ("Resumen", "summary"),
    ("Análisis", "analysis"),
    ("Estrategia", "strategy"),
    ("Investigación", "research"),
    ("Argumentos", "arguments"),
    ("Evidencia", "evidence"),
    ("Riesgos", "risks"),
    ("Contraargumentos", "counter_arguments"),
    ("Cronología", "timeline"),
    ("Citas", "citations"),
    ("Informe", "report"),
)


def build_legal_context(case_result: Dict[str, Any]) -> str:
    """Prepara sólo el contrato jurídico canónico para su indexación en Zep."""
    sections = []
    for label, field in _CONTEXT_FIELDS:
        value = case_result.get(field)
        if value in (None, "", [], {}):
            continue
        serialized = json.dumps(value, ensure_ascii=False, default=str, indent=2)
        sections.append(f"{label}:\n{serialized}")

    return "\n\n".join(sections).strip()


def graph_result(status: str, *, graph_id: str | None = None,
                 nodes: Any = None, edges: Any = None,
                 message: str | None = None) -> Dict[str, Any]:
    """Devuelve el único contrato público de estado del grafo."""
    result = {
        "status": status,
        "graph_id": graph_id,
        "nodes": nodes if isinstance(nodes, list) else [],
        "edges": edges if isinstance(edges, list) else [],
    }
    if message:
        result["message"] = message
    return result


class NovaCourtGraphOrchestrator:
    """Convierte el análisis canónico en una operación de grafo segura."""

    def __init__(
        self,
        builder_factory: Callable[[], Any],
        *,
        enabled: bool,
        timeout: int,
        poll_interval: int,
        chunk_size: int,
        chunk_overlap: int,
        batch_size: int,
    ) -> None:
        self.builder_factory = builder_factory
        self.enabled = enabled
        self.timeout = timeout
        self.poll_interval = poll_interval
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.batch_size = batch_size

    def build(self, case_result: Dict[str, Any]) -> Dict[str, Any]:
        if not self.enabled:
            return graph_result("not_requested")

        legal_context = build_legal_context(case_result)
        if not legal_context:
            return graph_result("not_requested")

        try:
            builder = self.builder_factory()
            graph = builder.build_graph_sync(
                text=legal_context,
                ontology=LEGAL_ONTOLOGY,
                graph_name="NovaCourt Legal Analysis",
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
                batch_size=self.batch_size,
                timeout=self.timeout,
                poll_interval=self.poll_interval,
            )
            return graph_result(
                "ready",
                graph_id=graph.get("graph_id"),
                nodes=graph.get("nodes"),
                edges=graph.get("edges"),
            )
        except Exception as error:
            if error.__class__.__name__ == "GraphProcessingTimeoutError":
                return graph_result(
                    "timeout",
                    message=(
                        "La generación del grafo superó el tiempo de espera. "
                        "El análisis jurídico permanece disponible."
                    ),
                )
            return graph_result(
                "failed",
                message=(
                    "No fue posible generar el grafo jurídico. "
                    "El análisis jurídico permanece disponible."
                ),
            )
