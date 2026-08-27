import re
import logging
from typing import List
from typing import Dict


logger = logging.getLogger(
    "NovaIuris.Citation"
)


class CitationService:
    """
    ============================================================

                    NOVA CITATION ENGINE

    Detecta automáticamente referencias jurídicas
    presentes dentro de cualquier documento.

    Utilizado por:

        • NovaSearch

        • NovaCase

        • NovaCourt

    Actualmente detecta:

        ✓ Constitución

        ✓ Leyes

        ✓ Decretos Legislativos

        ✓ Decretos Supremos

        ✓ Códigos

        ✓ Expedientes

        ✓ Casaciones

        ✓ Sentencias del TC

        ✓ Artículos

    En futuras versiones:

        ✓ Plenos Casatorios

        ✓ Opiniones Consultivas

        ✓ CIDH

        ✓ Corte Suprema

        ✓ Corte IDH

    ============================================================
    """

    def __init__(self):

        logger.info(
            "Citation Service iniciado."
        )

    ####################################################################
    ###################### PATRONES JURÍDICOS ###########################
    ####################################################################

    PATTERNS = {

        "constitucion": re.compile(

            r"\bconstituci[oó]n\s+pol[ií]tica\b",

            re.IGNORECASE

        ),

        "codigo": re.compile(

            r"\bc[oó]digo\s+(civil|penal|procesal|tributario|constitucional|procesal\s+civil|procesal\s+penal|niños\s+y\s+adolescentes)\b",

            re.IGNORECASE

        ),

        "ley": re.compile(

            r"\bley\s*n[°ºo]?\s*\d{2,6}\b",

            re.IGNORECASE

        ),

        "decreto_legislativo": re.compile(

            r"\bdecreto\s+legislativo\s*n[°ºo]?\s*\d+\b",

            re.IGNORECASE

        ),

        "decreto_supremo": re.compile(

            r"\bdecreto\s+supremo\s*n[°ºo]?\s*\d+(?:-\d+)?(?:-[A-Z]+)*\b",

            re.IGNORECASE

        ),

        "casacion": re.compile(

            r"\bcasaci[oó]n\s*n[°ºo]?\s*\d+(?:-\d+)?(?:-[A-Z]+)*\b",

            re.IGNORECASE

        ),

        "expediente": re.compile(

            r"\bexp(?:ediente)?\.?\s*n[°ºo]?\s*\d+(?:-\d+)+(?:-[A-Z]+)*\b",

            re.IGNORECASE

        ),

        "sentencia_tc": re.compile(

            r"\bstc\b|\btribunal\s+constitucional\b",

            re.IGNORECASE

        ),

        "articulo": re.compile(

            r"\bart[ií]culo\s+\d+[A-Za-zº°\-]*\b",

            re.IGNORECASE

        )

    }

    ####################################################################
    ###################### EXTRAER CITAS ###############################
    ####################################################################

    def extract_citations(
        self,
        text: str
    ) -> List[Dict]:

        """
        Extrae todas las referencias jurídicas
        encontradas en un texto.
        """

        if not text:

            return []

        citations = []

        for citation_type, pattern in self.PATTERNS.items():

            matches = pattern.finditer(text)

            for match in matches:

                citation = {

                    "type": citation_type,

                    "text": match.group(0).strip(),

                    "start": match.start(),

                    "end": match.end()

                }

                citations.append(citation)

        citations.sort(

            key=lambda x: x["start"]

        )

        logger.info(

            f"{len(citations)} citas jurídicas detectadas."

        )

        return citations
    
    ####################################################################
    ###################### ELIMINAR DUPLICADOS ##########################
    ####################################################################

    @staticmethod
    def unique_citations(
        citations: List[Dict]
    ) -> List[Dict]:

        """
        Elimina citas repetidas conservando
        únicamente una instancia.
        """

        unique = {}

        for citation in citations:

            key = (

                citation["type"],

                citation["text"].lower()

            )

            if key not in unique:

                unique[key] = citation

        return list(unique.values())

    ####################################################################
    ###################### AGRUPAR POR TIPO #############################
    ####################################################################

    @staticmethod
    def group_by_type(
        citations: List[Dict]
    ) -> Dict:

        """
        Agrupa las citas detectadas
        por categoría jurídica.
        """

        grouped = {}

        for citation in citations:

            citation_type = citation["type"]

            grouped.setdefault(

                citation_type,

                []

            ).append(citation)

        return grouped

    ####################################################################
    ######################## ESTADÍSTICAS ###############################
    ####################################################################

    @staticmethod
    def statistics(
        citations: List[Dict]
    ) -> Dict:

        """
        Devuelve estadísticas generales
        del documento analizado.
        """

        grouped = CitationService.group_by_type(
            citations
        )

        return {

            "total": len(citations),

            "tipos_detectados": len(grouped),

            "detalle": {

                key: len(value)

                for key, value in grouped.items()

            }

        }

    ####################################################################
    ######################## DEBUG #####################################
    ####################################################################

    @staticmethod
    def print_debug(
        citations: List[Dict]
    ) -> None:

        """
        Imprime todas las citas encontradas.

        Solo para desarrollo.
        """

        logger.info(
            "========== CITATIONS =========="
        )

        for citation in citations:

            logger.info(

                f"[{citation['type']}] "

                f"{citation['text']}"

            )

        logger.info(
            "================================"
        )