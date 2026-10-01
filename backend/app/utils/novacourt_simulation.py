"""Contrato estable y adaptador seguro para la simulación de NovaCourt."""

from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from typing import Any, Callable, Dict
from .cancellation import CancellationToken, OperationCancelled, check_cancelled
from .court_roles import resolve_court_roles


_CONTEXT_FIELDS = (
    ("Caso", "case"),
    ("Resumen", "summary"),
    ("Hechos", "facts"),
    ("Problemas", "issues"),
    ("Argumentos", "arguments"),
    ("Evidencia", "evidence"),
    ("Riesgos", "risks"),
    ("Contraargumentos", "counter_arguments"),
    ("Cronología", "timeline"),
    ("Estrategia final", "final_strategy"),
)


def _as_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def build_simulation_context(
    case_result: Dict[str, Any], case_text: str
) -> str:
    """Prepara el mínimo contexto canónico que el simulador existente acepta."""
    source = dict(case_result)
    # Structured facts/issues supersede the raw statement; never resend the
    # entire uploaded dossier when NovaCase has already extracted it.
    source["case"] = case_text if not source.get("facts") else None
    sections = []
    for label, field in _CONTEXT_FIELDS:
        value = source.get(field)
        if value in (None, "", [], {}):
            continue
        sections.append(
            f"{label}:\n{json.dumps(value, ensure_ascii=False, default=str, separators=(',', ':'))}"
        )

    sources = [item for item in source.get("sources", []) + source.get("sources_used", [])
               if isinstance(item, dict) and item.get("source_id") and
               (item.get("source_scope") != "case" or item.get("case_id") == source.get("case_id"))]
    for item in {entry["source_id"]: entry for entry in sources}.values():
        sections.append(f"[{item['source_id']}] {item.get('title') or ''}\n{item.get('excerpt') or ''}")

    return "\n\n".join(sections).strip()


def simulation_result(
    status: str,
    *,
    prosecutor: Any = None,
    defense: Any = None,
    judge: Any = None,
    projection: Any = None,
    metadata: Any = None,
    message: str | None = None,
) -> Dict[str, Any]:
    """Construye el único contrato público de simulación para NovaCourt."""
    result = {
        "status": status,
        "prosecutor": _as_dict(prosecutor),
        "defense": _as_dict(defense),
        "judge": _as_dict(judge),
        "projection": _as_dict(projection),
        "metadata": _as_dict(metadata),
        "error": {"code": status.upper(), "message": message} if status in {"failed", "timeout"} else None,
    }
    if message:
        result["message"] = message
    return result


def normalize_simulator_output(output: Any) -> Dict[str, Any]:
    """Normaliza campos reales del simulador sin modificar su razonamiento."""
    payload = _as_dict(output)
    fiscal = payload.get("fiscal")
    defensa = payload.get("defensa")
    juez = payload.get("juez")
    if not all(isinstance(value, str) and value.strip() for value in (fiscal, defensa, juez)):
        return simulation_result("failed", message="La simulación no produjo las posiciones requeridas.")

    return simulation_result(
        "ready",
        prosecutor={"content": fiscal} if isinstance(fiscal, str) and fiscal else {},
        defense={"content": defensa} if isinstance(defensa, str) and defensa else {},
        judge={"content": juez} if isinstance(juez, str) and juez else {},
        projection={},
        metadata={
            "session_id": payload.get("session_id"),
            "metrics": {},
            "base_legal": payload.get("base_legal") if isinstance(payload.get("base_legal"), str) else "",
        },
    )


class NovaCourtSimulationOrchestrator:
    """Ejecuta el simulador legado con un límite de espera del endpoint."""

    def __init__(
        self,
        simulator_factory: Callable[[], Any],
        *,
        enabled: bool,
        timeout: int,
    ) -> None:
        self.simulator_factory = simulator_factory
        self.enabled = enabled
        self.timeout = timeout

    def simulate(
        self, case_result: Dict[str, Any], case_text: str, cancellation_token=None
    ) -> Dict[str, Any]:
        if not self.enabled:
            return simulation_result("not_requested")

        context = build_simulation_context(case_result, case_text)
        if not context:
            return simulation_result("not_requested")

        token = CancellationToken(parent=cancellation_token, timeout=self.timeout)
        token.check()
        executor = ThreadPoolExecutor(max_workers=1)
        try:
            # La importación diferida y la ejecución del simulador comparten el
            # mismo límite para que una dependencia lenta no bloquee el endpoint.
            roles = resolve_court_roles(case_result)
            future = executor.submit(self._run_simulation, context, token, roles)
            output = future.result(timeout=self.timeout)
            result = normalize_simulator_output(output)
            result["metadata"]["context_characters"] = len(context)
            result["case_id"] = case_result.get("case_id")
            result["prosecutor"]["role_label"] = roles["position_a"]
            result["defense"]["role_label"] = roles["position_b"]
            result["judicial_analysis"] = result["judge"]
            result["decision"] = {"label": "Decisión simulada", "content": result["judge"].get("content", "")}
            return result
        except TimeoutError:
            token.cancel()
            return simulation_result(
                "timeout",
                message=(
                    "La simulación judicial superó el tiempo de espera. "
                    "El análisis y el grafo permanecen disponibles."
                ),
            )
        except OperationCancelled:
            if cancellation_token is not None and cancellation_token.is_cancelled():
                raise
            return simulation_result("timeout", message="La simulación superó el límite de espera.")
        except Exception:
            return simulation_result(
                "failed",
                message=(
                    "No fue posible completar la simulación judicial. "
                    "El análisis y el grafo permanecen disponibles."
                ),
            )
        finally:
            # No bloquea la respuesta si una dependencia remota continúa en el
            # hilo tras el timeout; el futuro se cancela si aún no inició.
            executor.shutdown(wait=False, cancel_futures=True)

    def _run_simulation(self, context: str, token, roles) -> Any:
        token.check()
        simulator = self.simulator_factory()
        token.check()
        if hasattr(simulator, "simulate_prepared_case"):
            return simulator.simulate_prepared_case(context, roles=roles, cancellation_token=token)
        return simulator.simulate_case(context, cancellation_token=token)
