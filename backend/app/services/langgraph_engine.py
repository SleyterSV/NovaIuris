from app.utils.cancellation import check_cancelled
import os
from typing import TypedDict, Annotated, Sequence, Dict
from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
import logging

logger = logging.getLogger(__name__)

# 1. Definición estricta de la Memoria del Tribunal (El Estado)
class TribunalState(TypedDict):
    caso: str
    dossier_rag: str  # Evidencia recuperada de Supabase
    argumento_fiscal: str
    argumento_defensa: str
    veredicto_juez: str
    mensajes: Annotated[Sequence[BaseMessage], "add_messages"]

# Inicializamos el modelo con baja temperatura para evitar alucinaciones
def get_llm():
    return ChatOpenAI(model="gpt-4o", temperature=0.1, max_retries=0, api_key=os.getenv("OPENAI_API_KEY"))

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
    respuesta = get_llm().invoke([HumanMessage(content=prompt)])
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
    respuesta = get_llm().invoke([HumanMessage(content=prompt)])
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
    respuesta = get_llm().invoke([HumanMessage(content=prompt)])
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
