import os
import time
from pathlib import Path
from typing import List

from dotenv import load_dotenv
from openai import OpenAI
from supabase import create_client, Client

from app.utils.pdf_reader import PDFReader
from app.services.jurisprudence_processor import JurisprudenceProcessor

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not all([SUPABASE_URL, SUPABASE_KEY, OPENAI_API_KEY]):
    raise ValueError(
        "Faltan variables de entorno."
    )

supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

client = OpenAI(
    api_key=OPENAI_API_KEY
)


class JurisprudenceIngestor:

    processor = JurisprudenceProcessor()

    CARPETA_JURISPRUDENCIA = (
        Path(__file__)
        .resolve()
        .parents[2]
        / "raw_docs"
        / "jurisprudencia"
    )

    CHUNK_SIZE = 1800

    OVERLAP = 250

    BATCH_SIZE = 25

    ####################################################################
    ######################## EMBEDDINGS ################################
    ####################################################################

    @staticmethod
    def get_embedding(text: str) -> List[float]:

        text = text.replace("\n", " ").strip()

        if not text:
            raise ValueError(
                "Texto vacío."
            )

        response = client.embeddings.create(

            model="text-embedding-3-small",

            input=[text]

        )

        return response.data[0].embedding

    ####################################################################
    ####################### DUPLICADOS #################################
    ####################################################################

    @staticmethod
    def already_exists(hash_documento: str):

        resultado = (

            supabase

            .table("legal_knowledge")

            .select("id")

            .eq("hash_documento", hash_documento)

            .limit(1)

            .execute()

        )

        return len(resultado.data) > 0

    ####################################################################
    ######################## CHUNKING ##################################
    ####################################################################

    @staticmethod
    def build_chunks(text: str):

        return PDFReader.split_into_chunks(

            text,

            chunk_size=JurisprudenceIngestor.CHUNK_SIZE,

            overlap=JurisprudenceIngestor.OVERLAP

        )

    ####################################################################
    ###################### LEER DOCUMENTO ###############################
    ####################################################################

    @staticmethod
    def read_document(filepath: Path):

        texto = PDFReader.read(str(filepath))

        if PDFReader.is_scanned(texto):

            print(
                f"⚠ {filepath.name} parece ser un PDF escaneado."
            )

            return None

        return texto

    ####################################################################
    ######################## INSERT ####################################
    ####################################################################

    @staticmethod
    def insert_batch(data):

        if not data:

            return

        try:

            response = (
                supabase
                .table("legal_knowledge")
                .insert(data)
                .execute()
            )

            print(
                f"✅ Insertados {len(response.data)} registros."
            )

        except Exception as e:

            print(

                f"❌ Error insertando lote:\n{e}"

            )

    ####################################################################
    ################## PROCESAR UN DOCUMENTO ############################
    ####################################################################

    @staticmethod
    def process_document(filepath: Path):

        print(f"\n📄 Procesando: {filepath.name}")

        texto = JurisprudenceIngestor.read_document(filepath)

        if texto is None:
            return []

        document = JurisprudenceIngestor.processor.process(

            fuente=filepath.stem,

            texto=texto

        )

        if JurisprudenceIngestor.already_exists(
            document.hash_documento
        ):

            print("⏭ Documento ya existe.")

            return []

        chunks = JurisprudenceIngestor.build_chunks(
            document.texto
        )

        registros = []

        for indice, chunk in enumerate(chunks):

            try:

                search_text = f"""
{document.tipo_documento}

{document.organo_emisor}

{document.expediente}

{document.materia}

{document.instancia}

{document.resumen}

{document.sumilla}

{' '.join(document.keywords)}

{chunk}
""".strip()

                embedding = JurisprudenceIngestor.get_embedding(
                    search_text
                )

                registros.append({

                    "hash_documento": document.hash_documento,
                    "rama": document.rama,
                    "fuente": document.fuente,
                    "tipo_documento": document.tipo_documento,
                    "jerarquia": document.jerarquia,
                    "articulo": f"Fragmento {indice + 1}",
                    "texto": chunk,
                    "resumen": document.resumen,
                    "vigencia": document.vigencia,
                    "entidad": document.entidad,
                    "numero": document.numero,
                    "fecha_publicacion": document.fecha_publicacion,
                    "keywords": document.keywords,
                    "metadata": document.metadata,
                    "organo_emisor": document.organo_emisor,
                    "expediente": document.expediente,
                    "tipo_resolucion": document.tipo_resolucion,
                    "ponente": document.ponente,
                    "fecha_resolucion": document.fecha_resolucion,
                    "sumilla": document.sumilla,
                    "precedente_vinculante": document.precedente_vinculante,
                    "materia": document.materia,
                    "instancia": document.instancia,
                    "embedding": embedding

                })

            except Exception as e:

                print(
                    f"❌ Error en fragmento {indice + 1}: {e}"
                )

        print(
            f"✅ {len(registros)} fragmentos preparados."
        )

        return registros

    ####################################################################
    ################## RECORRER CARPETA ################################
    ####################################################################

    @staticmethod
    def get_documents():

        carpeta = JurisprudenceIngestor.CARPETA_JURISPRUDENCIA

        if not carpeta.exists():

            raise FileNotFoundError(carpeta)

        archivos = []

        for extension in ("*.pdf", "*.docx", "*.txt"):

            archivos.extend(
                carpeta.glob(extension)
            )

        archivos.sort()

        return archivos

    ####################################################################
    ############################# RUN ##################################
    ####################################################################

    @staticmethod
    def run():

        print("\n===================================================")
        print("⚖️  NOVA IURIS - INGESTA DE JURISPRUDENCIA")
        print("===================================================\n")

        documentos = JurisprudenceIngestor.get_documents()

        if not documentos:

            print("⚠ No se encontraron documentos.")

            return

        print(f"📚 Documentos encontrados: {len(documentos)}\n")

        total_fragmentos = 0

        inicio = time.time()

        for indice, documento in enumerate(documentos, start=1):

            print(f"\n[{indice}/{len(documentos)}] {documento.name}")

            registros = JurisprudenceIngestor.process_document(documento)

            if not registros:

                continue

            for i in range(

                0,

                len(registros),

                JurisprudenceIngestor.BATCH_SIZE

            ):

                lote = registros[

                    i:i + JurisprudenceIngestor.BATCH_SIZE

                ]

                JurisprudenceIngestor.insert_batch(lote)

                total_fragmentos += len(lote)

                time.sleep(0.4)

        fin = time.time()

        print("\n===================================================")
        print("✅ INGESTA FINALIZADA")
        print("===================================================")

        print(f"📄 Documentos procesados : {len(documentos)}")
        print(f"🧩 Fragmentos insertados : {total_fragmentos}")
        print(f"⏱ Tiempo total          : {round(fin - inicio,2)} s")

        print("\n🚀 Legal Intelligence Engine actualizado.\n")


####################################################################
############################ MAIN ##################################
####################################################################

if __name__ == "__main__":

    JurisprudenceIngestor.run()