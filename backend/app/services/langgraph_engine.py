from app.utils.cancellation import check_cancelled
import os
from typing import TypedDict, Annotated, Sequence, Dict
from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
import logging
import time
from email.utils import parsedate_to_datetime
from datetime import datetime, timezone
from app.config import Config
from openai import APIConnectionError, APITimeoutError

logger = logging.getLogger(__name__)


def _remaining_deadline(token):
    deadlines = []
    while token is not None:
        if getattr(token, "deadline", None) is not None:
            deadlines.append(token.deadline)
        token = getattr(token, "parent", None)
    return min(deadlines) - time.monotonic() if deadlines else None

# 1. Definición estricta de la Memoria del Tribunal (El Estado)
class TribunalState(TypedDict):
    caso: str
    dossier_rag: str  # Evidencia recuperada de Supabase
    argumento_fiscal: str
    argumento_defensa: str
    veredicto_juez: str
    mensajes: Annotated[Sequence[BaseMessage], "add_messages"]

# Inicializamos el modelo con baja temperatura para evitar alucinaciones
def get_llm(timeout=None):
    return ChatOpenAI(model="gpt-4o", temperature=0.1, max_retries=0,
                      timeout=timeout or Config.LLM_TIMEOUT_SECONDS, api_key=os.getenv("OPENAI_API_KEY"))


def _retry_delay(error, attempt):
    headers = getattr(getattr(error, "response", None), "headers", {}) or {}
    raw = headers.get("retry-after") or headers.get("Retry-After")
    if raw:
        try:
            return max(0.0, float(raw))
        except ValueError:
            try:
                return max(0.0, (parsedate_to_datetime(raw) - datetime.now(timezone.utc)).total_seconds())
            except (TypeError, ValueError, OverflowError):
                pass
    return min(Config.NOVACOURT_RETRY_MAX_DELAY_SECONDS, 2 ** attempt)


def invoke_court_llm(prompt, config, stage):
    token = (config or {}).get("configurable", {}).get("cancellation_token")
    for attempt in range(Config.NOVACOURT_PROVIDER_MAX_RETRIES + 1):
        check_cancelled(token)
        try:
            remaining = _remaining_deadline(token)
            provider_timeout = min(Config.LLM_TIMEOUT_SECONDS,
                                   max(0, remaining)) if remaining is not None else Config.LLM_TIMEOUT_SECONDS
            if provider_timeout <= 0:
                check_cancelled(token)
            return get_llm(timeout=provider_timeout).invoke([HumanMessage(content=prompt)])
        except Exception as error:
            code = getattr(error, "status_code", None)
            transient = code in {429, 500, 502, 503, 504} or isinstance(error, (TimeoutError, ConnectionError, APIConnectionError, APITimeoutError))
            if not transient or attempt >= Config.NOVACOURT_PROVIDER_MAX_RETRIES:
                error.novacourt_failed_stage = stage
                error.novacourt_retry_count = attempt
                error.novacourt_reason = "rate_limited" if code == 429 else "provider_error"
                logger.warning("NovaCourt simulation provider failed stage=%s retry_count=%s reason=%s error_type=%s",
                               stage, attempt, "rate_limited" if code == 429 else "provider_error", type(error).__name__)
                raise
            delay = min(_retry_delay(error, attempt), Config.NOVACOURT_RETRY_MAX_DELAY_SECONDS)
            remaining = _remaining_deadline(token)
            if remaining is not None:
                delay = min(delay, max(0, remaining))
            logger.info("NovaCourt simulation retry stage=%s retry_count=%s delay_ms=%s",
                        stage, attempt + 1, round(delay * 1000))
            metrics = (config or {}).get("configurable", {}).get("retry_metrics")
            if isinstance(metrics, dict):
                metrics["count"] = metrics.get("count", 0) + 1
            if delay <= 0:
                raise
            end = time.monotonic() + delay
            while time.monotonic() < end:
                check_cancelled(token)
                time.sleep(min(0.1, end - time.monotonic()))
    raise RuntimeError("Provider retry loop exhausted")

# 2. Nodo del Fiscal
def nodo_fiscal(state: TribunalState, config: RunnableConfig = None) -> Dict:
    logger.info("👨‍⚖️ [LangGraph] Fiscal elaborando acusación...")
    role = (config or {}).get("configurable", {}).get("court_roles", {}).get("position_a", "Fiscalía")
    prompt = f"""Desarrolla la mejor posición jurídicamente plausible de {role} en esta simulación.
    Basado ESTRICTAMENTE en este dossier documental: {state['dossier_rag']}
    Presenta tesis, hechos alegados o respaldados, prueba disponible, fundamentos y limitaciones.
    Distingue prueba existente de prueba recomendada. Cita solo marcadores [SRC-...] presentes en el dossier.
    Si citas una ley, artículo o fecha, debe existir textualmente en el dossier."""
    
    check_cancelled((config or {}).get("configurable", {}).get("cancellation_token"))
    respuesta = invoke_court_llm(prompt, config, "position_a")
    return {
        "argumento_fiscal": respuesta.content, 
        "mensajes": [AIMessage(content=f"FISCAL:\n{respuesta.content}")]
    }

# 3. Nodo de la Defensa
def nodo_defensa(state: TribunalState, config: RunnableConfig = None) -> Dict:
    logger.info("🛡️ [LangGraph] Defensa analizando vacíos legales...")
    roles = (config or {}).get("configurable", {}).get("court_roles", {})
    role = roles.get("position_b", "Defensa")
    opposing_role = roles.get("position_a", "la parte promotora")
    prompt = f"""Desarrolla la mejor posición jurídicamente plausible de {role}.
    Basado ESTRICTAMENTE en este dossier documental: {state['dossier_rag']}
    {opposing_role} ha expuesto lo siguiente: {state['argumento_fiscal']}
    Formula una teoría propia y sustancial. Examina hechos, interpretación, procedimiento, prueba y límites.
    No inventes evidencia ni autoridad. Cita solo marcadores [SRC-...] presentes en el dossier."""
    
    check_cancelled((config or {}).get("configurable", {}).get("cancellation_token"))
    respuesta = invoke_court_llm(prompt, config, "position_b")
    return {
        "argumento_defensa": respuesta.content, 
        "mensajes": [AIMessage(content=f"DEFENSA:\n{respuesta.content}")]
    }

# 4. Nodo del Juez
def nodo_juez(state: TribunalState, config: RunnableConfig = None) -> Dict:
    logger.info("⚖️ [LangGraph] Juez deliberando...")
    roles = (config or {}).get("configurable", {}).get("court_roles", {})
    prompt = f"""Redacta una DECISIÓN SIMULADA, no una sentencia real ni una predicción estadística.
    Compara de forma independiente ambas posiciones:
    {roles.get('position_a', 'Parte promotora')}: {state['argumento_fiscal']}
    {roles.get('position_b', 'Parte contraria')}: {state['argumento_defensa']}
    
    Límites probatorios (Dossier): {state['dossier_rag']}
    
    Identifica controversias, distingue alegaciones de hechos respaldados, valora la prueba y las fuentes,
    expone límites y concluye con una decisión simulada razonada. Cita solo [SRC-...] disponibles.
    No inventes evidencia, autoridades ni probabilidades."""
    
    check_cancelled((config or {}).get("configurable", {}).get("cancellation_token"))
    respuesta = invoke_court_llm(prompt, config, "judge")
    return {
        "veredicto_juez": respuesta.content, 
        "mensajes": [AIMessage(content=f"JUEZ:\n{respuesta.content}")]
    }

# 5. Compilación del Grafo (Máquina de Estados)
def build_tribunal_graph():
    workflow = StateGraph(TribunalState)

    # Añadir nodos
    workflow.add_node("fiscal", nodo_fiscal)
    workflow.add_node("defensa", nodo_defensa)
    workflow.add_node("juez", nodo_juez)

    # Forzar el orden determinista (El flujo estricto del juicio)
    workflow.set_entry_point("fiscal")
    workflow.add_edge("fiscal", "defensa")
    workflow.add_edge("defensa", "juez")
    workflow.add_edge("juez", END)

    return workflow.compile()

# Instancia global lista para ser importada
nova_iuris_tribunal = build_tribunal_graph()
