import os
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from supabase import create_client, Client
from openai import OpenAI

# Cargar variables de entorno
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not all([SUPABASE_URL, SUPABASE_KEY, OPENAI_API_KEY]):
    raise ValueError("Faltan variables de entorno para inicializar el Retriever.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
client = OpenAI(api_key=OPENAI_API_KEY)

class LegalRetriever:
    """
    Motor de recuperación (RAG) híbrido. 
    Busca tanto en la biblioteca legal (leyes) como en los expedientes vivos del usuario.
    """

    @staticmethod
    def _generate_query_embedding(query: str) -> List[float]:
        """Convierte la pregunta o argumento en un vector matemático."""
        query = query.replace("\n", " ")
        response = client.embeddings.create(
            input=[query],
            model="text-embedding-3-small"
        )
        return response.data[0].embedding

    # =====================================================================
    # 1. BÚSQUEDA EN EL EXPEDIENTE DEL USUARIO (CEREBRO VIVO)
    # =====================================================================
    
    @staticmethod
    def search_expediente_context(query: str, session_id: str, match_count: int = 5, threshold: float = 0.4) -> List[Dict[str, Any]]:
        """
        Busca fragmentos relevantes dentro del documento PDF que el usuario subió en la sesión actual.
        """
        print(f"🔍 [Expediente] Buscando contexto para: '{query[:50]}...'")
        
        query_vector = LegalRetriever._generate_query_embedding(query)

        try:
            response = supabase.rpc(
                "match_expediente_chunks",
                {
                    "query_embedding": query_vector,
                    "match_threshold": threshold,
                    "match_count": match_count,
                    "p_session_id": session_id
                }
            ).execute()
            
            resultados = response.data
            if not resultados:
                print("⚠️ [Expediente] No se encontró contexto relevante en el documento subido.")
                return []
                
            print(f"✅ [Expediente] {len(resultados)} fragmentos encontrados.")
            return resultados

        except Exception as e:
            print(f"❌ Error al consultar el expediente en Supabase: {e}")
            return []

    # =====================================================================
    # 2. BÚSQUEDA EN LA BIBLIOTECA LEGAL (LEYES Y JURISPRUDENCIA)
    # =====================================================================

    @staticmethod
    def search_base_legal(query: str, match_count: int = 5, threshold: float = 0.5) -> List[Dict[str, Any]]:
        """
        Busca artículos, leyes o jurisprudencia en la base de datos estática.
        """
        print(f"🔍 [Base Legal] Buscando normativa para: '{query[:50]}...'")
        
        query_vector = LegalRetriever._generate_query_embedding(query)

        try:
            response = supabase.rpc(
                "match_base_legal",
                {
                    "query_embedding": query_vector,
                    "match_threshold": threshold,
                    "match_count": match_count
                }
            ).execute()
            
            resultados = response.data
            if not resultados:
                print("⚠️ [Base Legal] No se encontraron artículos suficientemente relevantes.")
                return []
                
            print(f"✅ [Base Legal] Se encontraron {len(resultados)} artículos relevantes.")
            return resultados

        except Exception as e:
            print(f"❌ Error al consultar la base legal en Supabase: {e}")
            return []


# --- ZONA DE PRUEBAS ---
if __name__ == "__main__":
    # Prueba 1: Buscar normativa en la Base Legal
    caso_prueba = "Devolución de aportes obligatorios vulnera libertad de asociación"
    
    print("\n--- TEST: BÚSQUEDA EN BASE LEGAL ---")
    leyes_recuperadas = LegalRetriever.search_base_legal(query=caso_prueba, match_count=3, threshold=0.3)
    
    for i, ley in enumerate(leyes_recuperadas, 1):
        print(f"\n[{i}] {ley.get('fuente', 'Desconocido')} - {ley.get('articulo', '')}")
        print(f"Similitud: {ley.get('similitud', 0):.2f}")
        print(f"Texto: {ley.get('texto_contenido', '')[:150]}...")