import re
import os
import time
import json
from typing import List
from dotenv import load_dotenv
from supabase import create_client, Client
from openai import OpenAI
from pathlib import Path
import sys
from app.services.legal_processor import LegalKnowledgeProcessor

# Truco para importar módulos hermanos
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from app.utils.file_parser import LegalParser

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not all([SUPABASE_URL, SUPABASE_KEY, OPENAI_API_KEY]):
    raise ValueError("Faltan variables de entorno. Asegúrate de tener tu archivo .env configurado.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
client = OpenAI(api_key=OPENAI_API_KEY)

class VectorStoreManager:

    processor = LegalKnowledgeProcessor()
    
    @staticmethod
    def get_embedding(text: str) -> List[float]:

        text = re.sub(r"\s+", " ", text).strip()

        if not text:
            raise ValueError("El texto para embedding está vacío.")

        response = client.embeddings.create(
            input=[text],
            model="text-embedding-3-small"
        )

        return response.data[0].embedding

    # =====================================================================
    # MÓDULO 1: MEMORIA DEL CASO ACTUAL (EXPEDIENTES Y SESSION_ID)
    # =====================================================================
    
    @staticmethod
    def procesar_y_vectorizar_expediente(texto_completo: str, session_id: str, filename: str, chunk_size: int = 1000):
        """
        Pica el texto del expediente en fragmentos y los guarda en Supabase como vectores.
        Tabla objetivo: expedientes_chunks
        """
        print(f"[*] Procesando expediente '{filename}' para la sesión '{session_id}'...")
        
        # 1. Chunking: Dividir en fragmentos
        chunks = [texto_completo[i:i+chunk_size] for i in range(0, len(texto_completo), chunk_size)]
        print(f"[*] Texto dividido en {len(chunks)} fragmentos. Vectorizando...")
        
        data_to_insert = []
        batch_size = 50 # Lotes para no saturar Supabase
        
        for i, chunk in enumerate(chunks):
            try:
                # 2. Generar Embedding
                vector = VectorStoreManager.get_embedding(chunk)
                
                # 3. Preparar data coincidiendo con el esquema SQL
                data_to_insert.append({
                    "session_id": session_id,
                    "nombre_archivo": filename,
                    "chunk_texto": chunk,
                    "metadata": {"chunk_index": i},
                    "embedding": vector
                })
            except Exception as e:
                print(f"[!] Error generando embedding para el fragmento {i}: {e}")

            # 4. Insertar en lotes
            if len(data_to_insert) >= batch_size or i == len(chunks) - 1:
                if data_to_insert:
                    try:
                        supabase.table('expedientes_chunks').insert(data_to_insert).execute()
                        data_to_insert = [] # Limpiar el lote
                        time.sleep(0.5) # Pausa por rate limits de OpenAI/Supabase
                    except Exception as e:
                        print(f"❌ Error al insertar fragmentos del expediente en Supabase: {e}")
                        
        print(f"✅ {len(chunks)} fragmentos del expediente vectorizados y guardados correctamente.")
        return True

    # =====================================================================
    # MÓDULO 2: BASE DE CONOCIMIENTO LEGAL (LEYES, CÓDIGOS, JURISPRUDENCIA)
    # =====================================================================

    @staticmethod
    def upload_legal_document(document_path: str, rama: str, fuente: str):
        print(f"[*] Iniciando procesamiento de: {fuente}...")
        parser = LegalParser(document_path=document_path, rama=rama, fuente=fuente)
        articles = parser.parse_articles()
        if not articles:
            print("❌ No se encontraron artículos. Revisa el documento fuente.")
            return
        VectorStoreManager._process_and_upload_batches(articles, fuente)

    @staticmethod
    def upload_from_json(json_path: str):
        path = Path(json_path)
        if not path.exists():
            print(f"❌ No se encontró el archivo JSON en: {json_path}")
            return
        print(f"[*] Cargando datos estructurados desde el caché: {path.name}...")
        with open(path, 'r', encoding='utf-8') as f:
            articles = json.load(f)
        if not articles:
            print(f"❌ El archivo {path.name} está vacío o es inválido.")
            return
        fuente = articles[0].get('fuente', path.stem)
        VectorStoreManager._process_and_upload_batches(articles, fuente)

    @staticmethod
    def _process_and_upload_batches(articles: List[dict], fuente: str):
        # 1. Limpieza Quirúrgica: Borramos registros previos de esta fuente en base_legal
        print(f"[*] Iniciando subida de {len(articles)} artículos...")

        # 2. Generación de embeddings con Chunking Dinámico
        print(f"[*] Iniciando subida de {len(articles)} artículos vectorizados a 'legal_knowledge'...")
                
        batch_size = 50
        
        for i in range(0, len(articles), batch_size):
            batch = articles[i:i + batch_size]
            data_to_insert = []
            
            for article in batch:

                try:
                    document = VectorStoreManager.processor.process_article(article)

                    existing = (
                        supabase
                        .table("legal_knowledge")
                        .select("id", count="exact")
                        .eq("hash_documento", document.hash_documento)
                        .limit(1)
                        .execute()
                    )

                    if existing.data:
                        print(f"⏭ Saltando duplicado: {document.articulo}")
                        continue

                    texto_embedding = VectorStoreManager.processor.build_search_text(document)

                    vector = VectorStoreManager.get_embedding(texto_embedding)

                    data_to_insert.append({

                    "hash_documento": document.hash_documento,

                    "rama": document.rama,

                    "fuente": document.fuente,

                    "tipo_documento": document.tipo_documento,

                    "jerarquia": document.jerarquia,

                    "articulo": document.articulo,

                    "texto": document.texto,

                    "resumen": document.resumen,

                    "vigencia": document.vigencia,

                    "entidad": document.entidad,

                    "numero": document.numero,

                    "fecha_publicacion": document.fecha_publicacion or None,

                    "keywords": document.keywords,

                    "metadata": document.metadata,

                    "embedding": vector

                    })

                except Exception as e:
                    print(f"[!] Error procesando {article.get('articulo', 'Sin nombre')}: {e}")               
                         
            # 3. Insertar lote
            if data_to_insert:
                try:
                    response = (
                        supabase
                        .table("legal_knowledge")
                        .insert(data_to_insert)
                        .execute()
                    )

                    print(f"✅ Insertados {len(response.data)} registros.")
                    print(f"✅ Lote insertado: {min(i + batch_size, len(articles))} / {len(articles)}")
                    time.sleep(0.5)
                except Exception as e:
                    print(f"❌ Error al insertar en Supabase: {e}")

if __name__ == "__main__":
    BASE_DIR = Path(__file__).resolve().parents[2]
    PROCESSED_DIR = BASE_DIR.parent / "processed_docs"
    
    print("=================== INICIANDO SUBIDA VECTORIAL A SUPABASE ===================")
    
    archivos_json = list(PROCESSED_DIR.glob("*.json"))
    
    if not archivos_json:
        print("⚠️ No se encontraron archivos JSON en la carpeta processed_docs.")
    else:
        print(f"[*] Se detectaron {len(archivos_json)} archivos estructurados para subir.\n")
        
        for ruta_json in archivos_json:
            VectorStoreManager.upload_from_json(str(ruta_json))
            print("-" * 60)
            
    print("=================== PROCESO VECTORIAL FINALIZADO ===================")