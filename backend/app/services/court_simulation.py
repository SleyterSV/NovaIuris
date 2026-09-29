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
from app.services.legal_repository import LegalRepository
from app.utils.cancellation import check_cancelled, OperationCancelled
from app.utils.legal_roles import LegalPersonas

# --- IMPORTACIÓN DEL NUEVO CEREBRO LANGGRAPH ---
from app.services.langgraph_engine import nova_iuris_tribunal
# --------------------------------------------

# Configuración de entorno y logs
load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

# Validación de seguridad de credenciales
def provider_clients():
    return (OpenAI(api_key=os.getenv("OPENAI_API_KEY"), max_retries=0),
            Zep(api_key=os.getenv("ZEP_API_KEY")),
            create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY")))


class LegalDebateSimulator:
    """Orquestador Multi-Agente con Arquitectura Híbrida (LangGraph + Zep + Supabase Vector RAG)."""

    @classmethod
    def simulate_prepared_case(cls, context: str, roles=None, cancellation_token=None) -> Dict[str, str]:
        """Canonical Court path: reuse verified CaseResult context without reingestion."""
        check_cancelled(cancellation_token)
        labels = roles or {"position_a": "Parte promotora", "position_b": "Parte contraria"}
        result = nova_iuris_tribunal.invoke(
            {"caso": "Simulación jurídica argumentativa", "dossier_rag": context, "mensajes": []},
            config={"configurable": {"cancellation_token": cancellation_token,
                                    "court_roles": labels}})
        check_cancelled(cancellation_token)
        return {"fiscal": result.get("argumento_fiscal", ""),
                "defensa": result.get("argumento_defensa", ""),
                "juez": result.get("veredicto_juez", "")}

    @staticmethod
    def _vectorizar_expediente_vivo(texto_completo: str, session_id: str, cancellation_token=None) -> bool:
        """
        Fase de Ingesta: Divide el expediente completo en fragmentos semánticos,
        los convierte en vectores y los guarda en Supabase.
        """
        check_cancelled(cancellation_token)
        openai_client, zep_client, supabase_client = provider_clients()
        try:
            logger.info("🧠 Procesando expediente masivo (Chunking & Embedding)...")
            
            # 1. Chunking: Dividir en fragmentos manejables (~1500 caracteres)
            chunk_size = 1500
            chunks = [texto_completo[i:i+chunk_size] for i in range(0, len(texto_completo), chunk_size)]
            
            # 2. Vectorización y guardado
            for i, chunk in enumerate(chunks):
                check_cancelled(cancellation_token)
                # Omitir fragmentos muy pequeños sin valor semántico
                if len(chunk.strip()) < 50:
                    continue
                    
                response = openai_client.embeddings.create(
                    input=chunk,
                    model="text-embedding-3-small"
                )
                vector = response.data[0].embedding
                
                # Inserción en la tabla de Supabase creada previamente
                check_cancelled(cancellation_token)
                supabase_client.table('expedientes_chunks').insert({
                    "session_id": session_id,
                    "nombre_archivo": "expediente_acumulado.txt",
                    "chunk_texto": chunk,
                    "metadata": {"chunk_index": i},
                    "embedding": vector
                }).execute()
                
            logger.info(f"✅ Expediente vectorizado exitosamente: {len(chunks)} fragmentos en Supabase.")
            return True
        except OperationCancelled:
            raise
        except Exception as e:
            logger.error("Provider operation failed error_type=%s", type(e).__name__)
            return False

    @staticmethod
    def _consultar_evidencia_documental(query: str, session_id: str, limit: int = 4, cancellation_token=None) -> str:
        """
        Fase de Recuperación: Busca en los fragmentos del expediente los párrafos
        que responden a la estrategia del agente en turno.
        """
        check_cancelled(cancellation_token)
        openai_client, zep_client, supabase_client = provider_clients()
        try:
            # 1. Convertir la intención del agente a vector
            query_vector = openai_client.embeddings.create(
                input=query, 
                model="text-embedding-3-small"
            ).data[0].embedding
            
            # 2. Búsqueda de similitud en Supabase mediante RPC
            check_cancelled(cancellation_token)
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
            
        except OperationCancelled:
            raise
        except Exception as e:
            logger.error("Provider operation failed error_type=%s", type(e).__name__)
            raise RuntimeError("Evidence retrieval failed") from None

    @staticmethod
    def _consultar_base_legal(query: str, limit: int = 5, cancellation_token=None) -> str:
        """
        Consulta la tabla legal_knowledge en Supabase por similitud semántica.
        Extrae los artículos exactos (Código Civil, Penal, etc.) para fundamentar el debate.
        """
        check_cancelled(cancellation_token)
        openai_client, zep_client, supabase_client = provider_clients()
        try:
            logger.info("📚 Buscando jurisprudencia y artículos en legal_knowledge...")
            # 1. Convertir la consulta a vector
            query_vector = openai_client.embeddings.create(
                input=query, 
                model="text-embedding-3-small"
            ).data[0].embedding
            
            # 2. Llamar a la función RPC de Supabase para la tabla legal_knowledge
            check_cancelled(cancellation_token)
            rows = LegalRepository().semantic_search(query_vector, limit=limit, threshold=0.4)
            if not rows:
                return "No se encontraron artículos legales específicos en la base de datos."
                
            # 3. Formatear estructuradamente según las columnas
            leyes_encontradas = []
            for item in rows:
                fuente = item.get('fuente', 'Norma Legal')
                articulo = item.get('articulo', 'Artículo')
                texto = item.get('texto', '')
                leyes_encontradas.append(f"[{fuente}] {articulo}: {texto}")
                
            return "\n\n".join(leyes_encontradas)
            
        except OperationCancelled:
            raise
        except Exception as e:
            logger.error("Provider operation failed error_type=%s", type(e).__name__)
            raise RuntimeError("Legal retrieval failed") from None

    @staticmethod
    def _generar_metricas(caso: str, veredicto: str, cancellation_token=None) -> dict:
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
        check_cancelled(cancellation_token)
        openai_client, zep_client, supabase_client = provider_clients()
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
        except OperationCancelled:
            raise
        except Exception as e:
            logger.error("Provider operation failed error_type=%s", type(e).__name__)
            return {}

    @classmethod
    def simulate_case(cls, caso_completo: str, cancellation_token=None) -> Dict[str, str]:
        """Orquesta el flujo delegando el razonamiento a LangGraph (Nova Iuris 2.0)"""
        
        # Generar ID único para esta audiencia
        check_cancelled(cancellation_token)
        openai_client, zep_client, supabase_client = provider_clients()
        session_id = f"audiencia_nova_{uuid4().hex[:8]}"
        logger.info(f"\n⚖️ Iniciando Nova Iuris Tribunal [Sesión: {session_id}]")
        logger.info("="*60)

        # 1. Ingesta: Vectorizar el expediente completo en Supabase 
        if not cls._vectorizar_expediente_vivo(caso_completo, session_id, cancellation_token=cancellation_token):
            raise RuntimeError("Document ingestion failed")

        # 2. Recuperar la Evidencia Central (Hechos)
        logger.info("📄 Consultando hechos en el expediente...")
        evidencia_central = cls._consultar_evidencia_documental(
            "Hechos clave, acusaciones, atenuantes y pruebas", 
            session_id, 
            limit=4, cancellation_token=cancellation_token
        )

        # 3. Recuperar los Artículos de la Ley (legal_knowledge)
        marco_legal = cls._consultar_base_legal(caso_completo[:1000], limit=5, cancellation_token=cancellation_token)

        # 4. Construir el Estado Inicial Combinado para LangGraph
        dossier_combinado = (
            f"--- HECHOS Y EVIDENCIA DEL CASO ---\n{evidencia_central}\n\n"
            f"--- MARCO LEGAL APLICABLE ---\n{marco_legal}"
        )

        # 5. Zep Cloud: Registrar el caso para el grafo visual
        try:
            logger.info("🌐 Registrando relaciones iniciales en Zep Cloud...")
            check_cancelled(cancellation_token)
            zep_client.graph.create(
                graph_id=session_id,
                name=f"Expediente {session_id}",
                description="Simulación de debate legal (Nova Iuris 2.0)"
            )
            check_cancelled(cancellation_token)
            zep_client.graph.add(graph_id=session_id, type="text", data=caso_completo[:1000])
        except OperationCancelled:
            raise
        except Exception as e:
            logger.warning("Provider operation failed error_type=%s", type(e).__name__)

        # 6. Construir el Estado Inicial para la Máquina de Estados (LangGraph)
        estado_inicial = {
            "caso": caso_completo[:1500],  # Limitamos caracteres para optimizar tokens
            "dossier_rag": dossier_combinado,
            "mensajes": []
        }

        # 7. ¡Ejecutar el Grafo Multi-Agente! 
        logger.info("⚙️ Iniciando motor Multi-Agente LangGraph...")
        resultado_final = nova_iuris_tribunal.invoke(estado_inicial, config={"configurable": {"cancellation_token": cancellation_token}})

        # 8. Zep Cloud: Inyectar resultados de LangGraph para el mapa de entidades
        try:
            check_cancelled(cancellation_token)
            zep_client.graph.add(graph_id=session_id, type="text", data=f"FISCAL: {resultado_final.get('argumento_fiscal', '')}")
            check_cancelled(cancellation_token)
            zep_client.graph.add(graph_id=session_id, type="text", data=f"DEFENSA: {resultado_final.get('argumento_defensa', '')}")
            check_cancelled(cancellation_token)
            zep_client.graph.add(graph_id=session_id, type="text", data=f"JUEZ: {resultado_final.get('veredicto_juez', '')}")
        except OperationCancelled:
            raise
        except Exception:
            pass

        # 9. Extrayendo Analítica Avanzada
        logger.info("📊 Extrayendo analítica para el Dashboard...")
        metricas_graficas = cls._generar_metricas(caso_completo, resultado_final.get("veredicto_juez", ""), cancellation_token=cancellation_token)

        # 10. Retornar la estructura exacta que tu Frontend de Vue ya consume
        logger.info("✅ Simulación completada con éxito. Retornando payload al cliente.")
        return {
            "session_id": session_id,
            "base_legal": marco_legal, # Cambiado para devolver el marco normativo al frontend
            "fiscal": resultado_final.get("argumento_fiscal", ""),
            "defensa": resultado_final.get("argumento_defensa", ""),
            "juez": resultado_final.get("veredicto_juez", ""),
            "metricas": metricas_graficas
        }
