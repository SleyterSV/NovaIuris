import os
import sys
import logging
import json
from uuid import uuid4
from typing import Dict, List
from openai import OpenAI
from dotenv import load_dotenv

# --- IMPORTACIONES CLOUD ---
from zep_cloud.client import Zep
from supabase import create_client, Client

# --- ENRUTAMIENTO ABSOLUTO ---
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from app.services.retriever import LegalRetriever
from app.utils.legal_roles import LegalPersonas
# --------------------------------------------

# Configuración de entorno y logs
load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

# Validación de seguridad de credenciales
REQUIRED_KEYS = ["OPENAI_API_KEY", "ZEP_API_KEY", "SUPABASE_URL", "SUPABASE_KEY"]
for key in REQUIRED_KEYS:
    if not os.getenv(key):
        logger.error(f"🚨 CRÍTICO: Falta la credencial {key} en el archivo .env.")
        sys.exit(1)

# Inicialización de clientes
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
zep_client = Zep(api_key=os.getenv("ZEP_API_KEY"))
supabase_client: Client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))


class LegalDebateSimulator:
    """Orquestador Multi-Agente con Arquitectura de Memoria Híbrida (Zep Graphs + Supabase Vector RAG)."""

    @staticmethod
    def _vectorizar_expediente_vivo(texto_completo: str, session_id: str) -> bool:
        """
        Fase de Ingesta: Divide el expediente completo en fragmentos semánticos,
        los convierte en vectores y los guarda en Supabase.
        """
        try:
            logger.info("🧠 Procesando expediente masivo (Chunking & Embedding)...")
            
            # 1. Chunking: Dividir en fragmentos manejables (~1500 caracteres)
            chunk_size = 1500
            chunks = [texto_completo[i:i+chunk_size] for i in range(0, len(texto_completo), chunk_size)]
            
            # 2. Vectorización y guardado
            for i, chunk in enumerate(chunks):
                # Omitir fragmentos muy pequeños sin valor semántico
                if len(chunk.strip()) < 50:
                    continue
                    
                response = openai_client.embeddings.create(
                    input=chunk,
                    model="text-embedding-3-small"
                )
                vector = response.data[0].embedding
                
                # Inserción en la tabla de Supabase creada previamente
                supabase_client.table('expedientes_chunks').insert({
                    "session_id": session_id,
                    "nombre_archivo": "expediente_acumulado.txt",
                    "chunk_texto": chunk,
                    "metadata": {"chunk_index": i},
                    "embedding": vector
                }).execute()
                
            logger.info(f"✅ Expediente vectorizado exitosamente: {len(chunks)} fragmentos en Supabase.")
            return True
        except Exception as e:
            logger.error(f"🚨 Error al vectorizar el expediente en Supabase: {e}")
            return False

    @staticmethod
    def _consultar_evidencia_documental(query: str, session_id: str, limit: int = 4) -> str:
        """
        Fase de Recuperación: Busca en los fragmentos del expediente los párrafos
        que responden a la estrategia del agente en turno.
        """
        try:
            # 1. Convertir la intención del agente a vector
            query_vector = openai_client.embeddings.create(
                input=query, 
                model="text-embedding-3-small"
            ).data[0].embedding
            
            # 2. Búsqueda de similitud en Supabase mediante RPC
            resultados_rag = supabase_client.rpc(
                'match_expediente_chunks',
                {
                    'query_embedding': query_vector, 
                    'match_threshold': 0.3, # Umbral de similitud
                    'match_count': limit, 
                    'p_session_id': session_id
                }
            ).execute()
            
            if not resultados_rag.data:
                return "No se encontraron detalles específicos en el expediente sobre este punto."
                
            # Ensamblar los fragmentos relevantes
            evidencia = "\n...\n".join([item['chunk_texto'] for item in resultados_rag.data])
            return evidencia
            
        except Exception as e:
            logger.error(f"🚨 Error consultando la evidencia vectorial: {e}")
            return "Error recuperando la evidencia documental."

    @staticmethod
    def _generar_respuesta_agente(rol_prompt: str, contexto_estructural_zep: str, evidencia_documental: str, contexto_leyes: str, input_actual: str) -> str:
        """
        El Cerebro Central: Llama al LLM inyectando el Grafo (Zep), el Expediente (Supabase) y la Ley (RAG).
        """
        system_prompt = f"""{rol_prompt}

[MEMORIA ESTRUCTURAL DEL CASO]
{contexto_estructural_zep}

[EVIDENCIA DOCUMENTAL ESPECÍFICA (EXPEDIENTE)]
A continuación, extractos literales del expediente recuperados mediante búsqueda semántica:
{evidencia_documental}

[MARCO LEGAL APLICABLE (LEYES Y JURISPRUDENCIA)]
{contexto_leyes}

INSTRUCCIÓN CRÍTICA:
Basado estrictamente en la evidencia documental y el marco legal proporcionado, desarrolla tu argumentación. 
No inventes fechas, nombres ni artículos. Si la evidencia menciona un dato exacto, cítalo.
"""
        try:
            response = openai_client.chat.completions.create(
                model="gpt-4o", 
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"[TU TURNO]\n{input_actual}"}
                ],
                temperature=0.2 # Temperatura baja para mantener el rigor jurídico
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"🚨 Error en el clúster de inferencia: {e}")
            return "Error de comunicación con el agente neuronal."

    @staticmethod
    def _generar_metricas(caso: str, veredicto: str) -> dict:
        """Agente Analista: Extrae métricas probabilísticas estructuradas."""
        system_prompt = """Eres un Analista Jurídico de Datos. Evalúa el veredicto final y el expediente.
        Devuelve ÚNICAMENTE un objeto JSON válido con esta estructura exacta (usa enteros de 0 a 100):
        {
            "probabilidad_exito_demandante": 0,
            "probabilidad_exito_demandado": 0,
            "riesgo_procesal": 0,
            "calidad_argumentativa_fiscal": 0,
            "calidad_argumentativa_defensa": 0,
            "solidez_probatoria": 0,
            "nivel_confianza_resolucion": 0
        }"""
        try:
            response = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"[RESUMEN DEL CASO]\n{caso[:2000]}\n\n[VEREDICTO DEL JUEZ]\n{veredicto}"}
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"🚨 Error generando métricas gráficas: {e}")
            return {}

    @classmethod
    def simulate_case(cls, caso_completo: str) -> Dict[str, str]:
        """Orquesta el flujo completo de la audiencia virtual."""
        
        # Generar IDs únicos
        session_id = f"audiencia_{uuid4().hex[:8]}"
        logger.info(f"\n⚖️ Iniciando Tribunal Híbrido [Sesión: {session_id}]")
        logger.info("="*60)

        # 1. Ingesta: Vectorizar el expediente completo en Supabase
        cls._vectorizar_expediente_vivo(caso_completo, session_id)

        # 2. Crear el Grafo de Zep (Memoria Estructural)
        try:
            logger.info("🌐 Registrando relaciones del expediente en Zep Cloud...")
            zep_client.graph.create(
                graph_id=session_id,
                name=f"Expediente {session_id}",
                description="Simulación de debate legal (Fiscalía vs Defensa)"
            )
            # Extraer entidades iniciales para el contexto estructural
            zep_client.graph.add(graph_id=session_id, type="text", data=caso_completo[:1000])
        except Exception as e:
            logger.warning(f"⚠️ Aviso de Zep: {e}")

        transcript = []

        # 3. Recuperar Marco Legal General (Bypass de seguridad)
        logger.info("📚 Consultando Base Legal del sistema peruano...")
        contexto_legal = "Aplica los principios generales del derecho penal, civil y procesal peruano."

        try:
            # Solo intenta buscar si la función realmente existe en tu retriever
            if hasattr(LegalRetriever, 'search_relevant_laws'):
                leyes = LegalRetriever.search_relevant_laws(query=caso_completo[:1000], match_count=6, threshold=0.3)
                if leyes:
                    contexto_legal = "\n".join([f"[{i+1}] {l['fuente']} - {l['articulo']}:\n{l['texto']}" for i, l in enumerate(leyes)])
        except Exception as e:
            logger.warning(f"⚠️ Se omitió la búsqueda de leyes estáticas: {e}")
            
        # ---------------------------------------------------------
        # TURNO 1: EL FISCAL
        # ---------------------------------------------------------
        logger.info("👨‍⚖️ Fiscal consultando el expediente y elaborando acusación...")
        evidencia_fiscal = cls._consultar_evidencia_documental(
            "Hechos ilícitos, acusación, vulneraciones a la ley, agravios", session_id
        )
        
        argumento_fiscal = cls._generar_respuesta_agente(
            rol_prompt=LegalPersonas.FISCAL_PROMPT,
            contexto_estructural_zep="Inicio del debate. Analiza el caso central.",
            evidencia_documental=evidencia_fiscal,
            contexto_leyes=contexto_legal,
            input_actual="Formula tu acusación formal, tipificación y pena solicitada basándote en el expediente."
        )
        transcript.append(f"FISCAL:\n{argumento_fiscal}")
        
        try:
            zep_client.graph.add(graph_id=session_id, type="text", data=f"FISCAL: {argumento_fiscal}")
        except: pass

        # ---------------------------------------------------------
        # TURNO 2: LA DEFENSA
        # ---------------------------------------------------------
        logger.info("🛡️ Defensa buscando inconsistencias en la evidencia...")
        evidencia_defensa = cls._consultar_evidencia_documental(
            "Atenuantes, contradicciones, defensa propia, falta de pruebas", session_id
        )
        historial_defensa = "\n\n".join(transcript)
        
        argumento_defensa = cls._generar_respuesta_agente(
            rol_prompt=LegalPersonas.DEFENSA_PROMPT,
            contexto_estructural_zep=f"Historial hasta el momento:\n{historial_defensa}",
            evidencia_documental=evidencia_defensa,
            contexto_leyes=contexto_legal,
            input_actual="El Fiscal ha presentado su acusación. Refuta sus argumentos, busca vacíos legales en el expediente y protege a tu cliente."
        )
        transcript.append(f"DEFENSA:\n{argumento_defensa}")
        
        try:
            zep_client.graph.add(graph_id=session_id, type="text", data=f"DEFENSA: {argumento_defensa}")
        except: pass

        # ---------------------------------------------------------
        # TURNO 3: EL JUEZ
        # ---------------------------------------------------------
        logger.info("⚖️ Juez Supremo cruzando el debate con la base documental...")
        evidencia_juez = cls._consultar_evidencia_documental(
            "Pruebas definitivas, sentencias previas, resolución del conflicto", session_id
        )
        historial_juez = "\n\n".join(transcript)

        veredicto_juez = cls._generar_respuesta_agente(
            rol_prompt=LegalPersonas.JUEZ_PROMPT,
            contexto_estructural_zep=f"Historial del debate:\n{historial_juez}",
            evidencia_documental=evidencia_juez,
            contexto_leyes=contexto_legal,
            input_actual="Ambas partes han expuesto. Emite una resolución final, evaluando quién aplicó mejor la ley y justificando con la evidencia documental."
        )

        try:
            zep_client.graph.add(graph_id=session_id, type="text", data=f"JUEZ: {veredicto_juez}")
        except: pass

        # ---------------------------------------------------------
        # MÉTRICAS Y RETORNO
        # ---------------------------------------------------------
        logger.info("📊 Extrayendo analítica avanzada para el Dashboard...")
        metricas_graficas = cls._generar_metricas(caso_completo, veredicto_juez)

        return {
            "session_id": session_id,
            "base_legal": contexto_legal,
            "fiscal": argumento_fiscal,
            "defensa": argumento_defensa,
            "juez": veredicto_juez,
            "metricas": metricas_graficas
        }

# --- ZONA DE PRUEBA (CLI) ---
if __name__ == "__main__":
    caso_real = "El trabajador Juan Pérez solicita la devolución de sus aportes al FOVIPOL tras 20 años de servicio, amparándose en la reciente jurisprudencia sobre fondos de vivienda policial. Adjunta boletas de pago donde se evidencian los descuentos mensuales."
    
    resultados = LegalDebateSimulator.simulate_case(caso_real)
    
    print("\n" + "="*80)
    print(f"🏛️ RESOLUCIÓN DEL TRIBUNAL [SESIÓN: {resultados['session_id']}]")
    print("="*80)
    
    print("\n🔴 1. POSTURA DE LA FISCALÍA / DEMANDANTE:")
    print(resultados["fiscal"])
    
    print("\n" + "-"*80)
    print("🔵 2. CONTRAARGUMENTO DE LA DEFENSA:")
    print(resultados["defensa"])
    
    print("\n" + "-"*80)
    print("⚖️ 3. RESOLUCIÓN FINAL (EL JUEZ):")
    print(resultados["juez"])
    
    print("\n" + "="*80)