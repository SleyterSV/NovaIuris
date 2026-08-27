import hashlib
import uuid
import re

from app.models.legal_document import LegalDocument

MAX_EMBED_CHARS = 8000

class LegalKnowledgeProcessor:

    def process_article(self, article):
        """
        Convierte un artículo legal en un objeto LegalDocument
        enriquecido con metadatos para indexación semántica.
        """

        texto = article["texto"]

        return LegalDocument(
            id=str(uuid.uuid4()),
            hash_documento=self.generate_hash(texto),
            rama=article["rama"],
            fuente=article["fuente"],
            tipo_documento=self.detect_document_type(
                article["fuente"]
            ),
            jerarquia=self.detect_hierarchy(
                article["fuente"]
            ),
            articulo=article["articulo"],
            texto=texto,
            resumen=self.generate_summary(texto),
            vigencia=article.get(
                "vigencia",
                "Vigente"
            ),
            entidad="",
            numero="",
            fecha_publicacion="",
            keywords=self.extract_keywords(texto),
            metadata={}
        )

    def build_search_text(self, document):
        """
        Construye el texto enriquecido que será utilizado
        para generar embeddings de mayor calidad.
        """

        texto = document.texto

        
        if len(texto) > MAX_EMBED_CHARS:
            texto = texto[:MAX_EMBED_CHARS]

        return f"""
{document.fuente}

{document.articulo}

{document.resumen}

{' '.join(document.keywords)}

{texto}
""".strip()

    @staticmethod
    def generate_hash(text):
        """
        Genera un hash SHA-256 único para detectar documentos duplicados.
        """

        return hashlib.sha256(
            text.encode("utf-8")
        ).hexdigest()

    @staticmethod
    def generate_summary(text):
        """
        Genera un resumen limpio del contenido.
        """

        texto = re.sub(r"\s+", " ", text).strip()

        if len(texto) <= 400:
            return texto

        return texto[:400] + "..."

    @staticmethod
    def detect_document_type(nombre):
        """
        Detecta automáticamente el tipo de documento jurídico.
        """

        nombre = nombre.lower()

        if "constitución" in nombre:
            return "Constitución"

        if "codigo" in nombre or "código" in nombre:
            return "Código"

        if "ley" in nombre:
            return "Ley"

        if "casación" in nombre:
            return "Casación"

        if "acuerdo plenario" in nombre:
            return "Acuerdo Plenario"

        if "decreto" in nombre:
            return "Decreto"

        return "Documento Jurídico"

    @staticmethod
    def detect_hierarchy(nombre):
        """
        Determina la jerarquía normativa del documento.
        """

        nombre = nombre.lower()

        if "constitución" in nombre:
            return "Constitucional"

        if "codigo" in nombre or "código" in nombre:
            return "Legal"

        if "ley" in nombre:
            return "Legal"

        if "decreto" in nombre:
            return "Reglamentaria"

        return "General"

    @staticmethod
    def extract_keywords(text):
        """
        Extrae palabras clave relevantes eliminando duplicados.
        """

        palabras = re.findall(
            r"\b[A-ZÁÉÍÓÚÑ][a-záéíóúñ]{4,}\b",
            text
        )

        palabras = sorted(set(palabras))

        return palabras[:30]