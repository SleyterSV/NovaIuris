"""
Utilidades para la extracción y división de contenido textual.

Este módulo centraliza la lectura de archivos compatibles con Nova Iuris
y proporciona funciones para dividir textos extensos en fragmentos.

Formatos compatibles:
- TXT
- PDF
- DOCX

Responsabilidades principales:
- Detectar el tipo de archivo.
- Extraer contenido textual.
- Procesar múltiples archivos.
- Dividir textos extensos en fragmentos con solapamiento.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable


class FileParser:
    """
    Utilidad centralizada para extraer contenido textual desde archivos.

    Actualmente permite procesar archivos TXT, PDF y DOCX.
    """

    SUPPORTED_EXTENSIONS = {
        ".txt",
        ".pdf",
        ".docx",
    }

    @staticmethod
    def extract(file_path: str | Path) -> str:
        """
        Extrae el contenido textual de un archivo.

        Args:
            file_path: Ruta del archivo que se desea procesar.

        Returns:
            Contenido textual extraído y limpio.

        Raises:
            FileNotFoundError: Si el archivo no existe.
            ValueError: Si el formato no es compatible.
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(
                f"No se encontró el archivo: {path}"
            )

        if not path.is_file():
            raise ValueError(
                f"La ruta proporcionada no corresponde a un archivo: {path}"
            )

        extension = path.suffix.lower()

        if extension not in FileParser.SUPPORTED_EXTENSIONS:
            raise ValueError(
                "Formato de archivo no compatible: "
                f"{extension or 'sin extensión'}"
            )

        if extension == ".txt":
            text = FileParser._extract_from_txt(
                path
            )

        elif extension == ".pdf":
            text = FileParser._extract_from_pdf(
                path
            )

        elif extension == ".docx":
            text = FileParser._extract_from_docx(
                path
            )

        else:
            raise ValueError(
                f"No existe un procesador para el formato: {extension}"
            )

        return FileParser._clean_extracted_text(
            text
        )

    @staticmethod
    def extract_from_multiple(
        file_paths: Iterable[str | Path],
        separator: str = "\n\n",
    ) -> str:
        """
        Extrae y combina contenido textual desde múltiples archivos.

        Los archivos se procesan respetando el orden recibido.

        Args:
            file_paths: Rutas de los archivos que se desean procesar.
            separator: Separador utilizado entre los contenidos.

        Returns:
            Contenido textual combinado de todos los archivos.

        Raises:
            ValueError: Si no se proporciona ninguna ruta válida.
        """
        paths = [
            Path(file_path)
            for file_path in file_paths
            if file_path is not None and str(file_path).strip()
        ]

        if not paths:
            raise ValueError(
                "Debe proporcionar al menos una ruta de archivo válida."
            )

        extracted_texts = []

        for path in paths:

            text = FileParser.extract(
                path
            )

            if text:
                extracted_texts.append(
                    text
                )

        return separator.join(
            extracted_texts
        )

    @staticmethod
    def _extract_from_txt(path: Path) -> str:
        """
        Extrae contenido desde un archivo TXT.

        Intenta utilizar UTF-8 y formatos alternativos comunes
        para evitar errores de codificación.
        """
        encodings = (
            "utf-8",
            "utf-8-sig",
            "latin-1",
            "cp1252",
        )

        last_error = None

        for encoding in encodings:

            try:
                return path.read_text(
                    encoding=encoding
                )

            except UnicodeDecodeError as error:
                last_error = error

        raise ValueError(
            f"No fue posible determinar la codificación del archivo: {path}"
        ) from last_error

    @staticmethod
    def _extract_from_pdf(path: Path) -> str:
        """
        Extrae contenido textual desde un archivo PDF.

        Requiere la librería pypdf.
        """
        try:
            from pypdf import PdfReader

        except ImportError as error:
            raise ImportError(
                "Para procesar archivos PDF debes instalar 'pypdf'."
            ) from error

        reader = PdfReader(
            str(path)
        )

        pages_text = []

        for page in reader.pages:

            page_text = page.extract_text() or ""

            if page_text.strip():
                pages_text.append(
                    page_text
                )

        return "\n\n".join(
            pages_text
        )

    @staticmethod
    def _extract_from_docx(path: Path) -> str:
        """
        Extrae contenido textual desde un archivo DOCX.

        Requiere la librería python-docx.
        """
        try:
            from docx import Document

        except ImportError as error:
            raise ImportError(
                "Para procesar archivos DOCX debes instalar 'python-docx'."
            ) from error

        document = Document(
            str(path)
        )

        paragraphs = [
            paragraph.text.strip()
            for paragraph in document.paragraphs
            if paragraph.text and paragraph.text.strip()
        ]

        return "\n\n".join(
            paragraphs
        )

    @staticmethod
    def _clean_extracted_text(text: str) -> str:
        """
        Realiza una limpieza mínima del texto extraído.

        La normalización más completa corresponde a TextProcessor.
        """
        if not isinstance(text, str):
            return ""

        cleaned_text = text.replace(
            "\x00",
            ""
        )

        cleaned_text = (
            cleaned_text
            .replace("\r\n", "\n")
            .replace("\r", "\n")
        )

        cleaned_text = re.sub(
            r"\n{3,}",
            "\n\n",
            cleaned_text,
        )

        return cleaned_text.strip()


def split_text_into_chunks(
    text: str,
    chunk_size: int = 500,
    overlap: int = 50,
) -> list[str]:
    """
    Divide un texto en fragmentos con solapamiento.

    Intenta respetar los límites naturales del contenido, priorizando
    separaciones por párrafos y oraciones antes de realizar un corte.

    Args:
        text: Texto que será dividido.
        chunk_size: Tamaño máximo aproximado de cada fragmento.
        overlap: Número de caracteres de contexto compartido entre
            fragmentos consecutivos.

    Returns:
        Lista de fragmentos no vacíos.

    Raises:
        TypeError: Si el texto no es una cadena.
        ValueError: Si los parámetros son inválidos.
    """
    if not isinstance(text, str):
        raise TypeError(
            "El texto debe ser una cadena de caracteres."
        )

    if chunk_size <= 0:
        raise ValueError(
            "El tamaño del fragmento debe ser mayor que cero."
        )

    if overlap < 0:
        raise ValueError(
            "El solapamiento no puede ser negativo."
        )

    if overlap >= chunk_size:
        raise ValueError(
            "El solapamiento debe ser menor que el tamaño del fragmento."
        )

    normalized_text = text.strip()

    if not normalized_text:
        return []

    if len(normalized_text) <= chunk_size:
        return [
            normalized_text
        ]

    chunks = []
    start = 0
    text_length = len(normalized_text)

    while start < text_length:

        end = min(
            start + chunk_size,
            text_length,
        )

        if end < text_length:

            paragraph_break = normalized_text.rfind(
                "\n\n",
                start,
                end,
            )

            sentence_break = max(
                normalized_text.rfind(
                    ". ",
                    start,
                    end,
                ),
                normalized_text.rfind(
                    "? ",
                    start,
                    end,
                ),
                normalized_text.rfind(
                    "! ",
                    start,
                    end,
                ),
            )

            word_break = normalized_text.rfind(
                " ",
                start,
                end,
            )

            break_position = max(
                paragraph_break,
                sentence_break,
                word_break,
            )

            minimum_break_position = (
                start + int(chunk_size * 0.5)
            )

            if break_position >= minimum_break_position:
                end = break_position + 1

        chunk = normalized_text[
            start:end
        ].strip()

        if chunk:
            chunks.append(
                chunk
            )

        if end >= text_length:
            break

        next_start = end - overlap

        if next_start <= start:
            next_start = end

        start = next_start

    return chunks