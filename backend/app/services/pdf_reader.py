import fitz
import docx
import re
from pathlib import Path


class PDFReader:
    """
    Lector universal de documentos jurídicos.

    Soporta:
        - PDF
        - DOCX
        - TXT
    """

    SUPPORTED_EXTENSIONS = {
        ".pdf",
        ".docx",
        ".txt"
    }

    @classmethod
    def read(cls, filepath: str) -> str:

        path = Path(filepath)

        if not path.exists():
            raise FileNotFoundError(path)

        extension = path.suffix.lower()

        if extension not in cls.SUPPORTED_EXTENSIONS:
            raise ValueError(
                f"Formato no soportado: {extension}"
            )

        if extension == ".pdf":
            texto = cls._read_pdf(path)

        elif extension == ".docx":
            texto = cls._read_docx(path)

        else:
            texto = cls._read_txt(path)

        return cls.clean_text(texto)

    @staticmethod
    def _read_pdf(path: Path) -> str:

        texto = []

        documento = fitz.open(path)

        try:

            for pagina in documento:

                contenido = pagina.get_text("text")

                if contenido:

                    texto.append(contenido)

        finally:

            documento.close()

        return "\n".join(texto)

    @staticmethod
    def _read_docx(path: Path) -> str:

        documento = docx.Document(path)

        texto = []

        for p in documento.paragraphs:

            if p.text.strip():

                texto.append(p.text)

        return "\n".join(texto)

    @staticmethod
    def _read_txt(path: Path) -> str:

        with open(
            path,
            "r",
            encoding="utf-8",
            errors="ignore"
        ) as f:

            return f.read()

    @staticmethod
    def clean_text(text: str) -> str:
        """
        Limpia el texto antes de enviarlo al modelo.
        """

        if not text:
            return ""

        text = text.replace("\x00", " ")

        text = text.replace("\t", " ")

        text = text.replace("\r", "\n")

        text = re.sub(
            r"[ ]{2,}",
            " ",
            text
        )

        text = re.sub(
            r"\n{3,}",
            "\n\n",
            text
        )

        return text.strip()

    @staticmethod
    def is_scanned(text: str) -> bool:
        """
        Detecta PDFs escaneados.
        """

        if not text:
            return True

        texto = text.strip()

        if len(texto) < 200:
            return True

        palabras = texto.split()

        return len(palabras) < 50

    @staticmethod
    def split_into_chunks(
        text: str,
        chunk_size: int = 1800,
        overlap: int = 250
    ):
        """
        Chunking inteligente.

        Intenta cortar cerca de un salto de línea
        para no romper párrafos.
        """

        chunks = []

        inicio = 0

        while inicio < len(text):

            fin = min(
                inicio + chunk_size,
                len(text)
            )

            if fin < len(text):

                corte = text.rfind(
                    "\n",
                    inicio,
                    fin
                )

                if corte != -1 and corte > inicio:

                    fin = corte

            chunk = text[inicio:fin].strip()

            if len(chunk) > 80:

                chunks.append(chunk)

            inicio = max(
                fin - overlap,
                fin
            )

        return chunks

    @staticmethod
    def first_page(text: str) -> str:
        """
        Devuelve aproximadamente
        la primera página del documento.
        """

        return text[:5000]

    @staticmethod
    def build_summary(text: str) -> str:
        """
        Resumen simple utilizado
        cuando aún no se llama a GPT.
        """

        texto = PDFReader.clean_text(text)

        if len(texto) <= 700:

            return texto

        return texto[:700] + "..."