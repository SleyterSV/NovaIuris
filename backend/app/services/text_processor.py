"""
Servicio centralizado de procesamiento y normalización de texto.

Este módulo proporciona las operaciones necesarias para preparar contenido
textual dentro de Nova Iuris antes de procesos posteriores como análisis,
indexación, recuperación de información o construcción de grafos.

Responsabilidades principales:
- Extraer texto desde múltiples archivos.
- Normalizar y limpiar contenido textual.
- Dividir textos extensos en fragmentos con solapamiento.
- Obtener estadísticas básicas del contenido.
"""

from __future__ import annotations

import re
from typing import Any

from ..utils.file_parser import FileParser, split_text_into_chunks


class TextProcessor:
    """
    Procesador centralizado de contenido textual para Nova Iuris.

    Proporciona métodos estáticos para extraer, normalizar, dividir
    y analizar texto de forma consistente dentro de la aplicación.
    """

    @staticmethod
    def extract_from_files(file_paths: list[str]) -> str:
        """
        Extrae y combina el contenido textual de múltiples archivos.

        El contenido extraído se normaliza antes de ser devuelto para
        garantizar una estructura textual consistente.

        Args:
            file_paths: Lista de rutas de los archivos que se procesarán.

        Returns:
            Contenido textual combinado y normalizado.

        Raises:
            ValueError: Si no se proporciona ninguna ruta válida.
        """
        if not file_paths:
            raise ValueError(
                "Debe proporcionar al menos una ruta de archivo."
            )

        valid_paths = [
            str(file_path).strip()
            for file_path in file_paths
            if file_path is not None and str(file_path).strip()
        ]

        if not valid_paths:
            raise ValueError(
                "No se proporcionaron rutas de archivo válidas."
            )

        extracted_text = FileParser.extract_from_multiple(
            valid_paths
        )

        if not extracted_text:
            return ""

        return TextProcessor.preprocess_text(
            extracted_text
        )

    @staticmethod
    def split_text(
        text: str,
        chunk_size: int = 500,
        overlap: int = 50,
    ) -> list[str]:
        """
        Divide un texto en fragmentos con un solapamiento configurable.

        El texto se normaliza antes de dividirse para evitar fragmentos
        innecesarios causados por espacios, saltos de línea o contenido
        vacío.

        Args:
            text: Texto original que se desea dividir.
            chunk_size: Tamaño máximo aproximado de cada fragmento.
            overlap: Cantidad de contenido compartido entre fragmentos.

        Returns:
            Lista de fragmentos de texto no vacíos.

        Raises:
            TypeError: Si el texto no es una cadena.
            ValueError: Si los parámetros de división son inválidos.
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
                "El solapamiento debe ser menor que el tamaño "
                "del fragmento."
            )

        normalized_text = TextProcessor.preprocess_text(
            text
        )

        if not normalized_text:
            return []

        chunks = split_text_into_chunks(
            normalized_text,
            chunk_size,
            overlap,
        )

        return [
            chunk.strip()
            for chunk in chunks
            if isinstance(chunk, str) and chunk.strip()
        ]

    @staticmethod
    def preprocess_text(text: str) -> str:
        """
        Normaliza y limpia un texto antes de su procesamiento.

        Operaciones realizadas:
        - Elimina caracteres nulos.
        - Normaliza los saltos de línea.
        - Convierte tabulaciones en espacios.
        - Elimina espacios innecesarios al inicio y final de cada línea.
        - Reduce espacios consecutivos dentro de una línea.
        - Reduce bloques excesivos de líneas vacías.
        - Conserva la estructura general de los párrafos.

        Args:
            text: Texto original.

        Returns:
            Texto normalizado y limpio.

        Raises:
            TypeError: Si el valor proporcionado no es una cadena.
        """
        if not isinstance(text, str):
            raise TypeError(
                "El contenido a procesar debe ser una cadena de texto."
            )

        if not text.strip():
            return ""

        processed_text = text.replace(
            "\x00",
            ""
        )

        processed_text = (
            processed_text
            .replace("\r\n", "\n")
            .replace("\r", "\n")
            .replace("\t", " ")
        )

        lines = [
            re.sub(
                r"[ \f\v]+",
                " ",
                line,
            ).strip()
            for line in processed_text.split("\n")
        ]

        processed_text = "\n".join(lines)

        processed_text = re.sub(
            r"\n{3,}",
            "\n\n",
            processed_text,
        )

        return processed_text.strip()

    @staticmethod
    def get_text_stats(text: str) -> dict[str, Any]:
        """
        Obtiene estadísticas básicas de un contenido textual.

        Args:
            text: Texto que se desea analizar.

        Returns:
            Diccionario con estadísticas del texto procesado.

        Raises:
            TypeError: Si el texto no es una cadena.
        """
        if not isinstance(text, str):
            raise TypeError(
                "El texto debe ser una cadena de caracteres."
            )

        normalized_text = TextProcessor.preprocess_text(
            text
        )

        if not normalized_text:
            return {
                "total_caracteres": 0,
                "total_lineas": 0,
                "total_palabras": 0,
                "total_parrafos": 0,
                "esta_vacio": True,
            }

        paragraphs = [
            paragraph.strip()
            for paragraph in normalized_text.split("\n\n")
            if paragraph.strip()
        ]

        words = re.findall(
            r"\b[\wÁÉÍÓÚÜÑáéíóúüñ'-]+\b",
            normalized_text,
            flags=re.UNICODE,
        )

        return {
            "total_caracteres": len(normalized_text),
            "total_lineas": len(normalized_text.splitlines()),
            "total_palabras": len(words),
            "total_parrafos": len(paragraphs),
            "esta_vacio": False,
        }