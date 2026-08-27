import logging
from typing import List
from typing import Dict


logger = logging.getLogger(
    "NovaIuris.ContextBuilder"
)


class ContextBuilder:
    """
    ==========================================================

                NOVA CONTEXT BUILDER

    Construye el contexto que será enviado
    al modelo de lenguaje.

    Su objetivo NO es responder.

    Su trabajo consiste en seleccionar,
    organizar y sintetizar los documentos
    encontrados.

    Utilizado por:

        • NovaSearch

        • NovaCase

        • NovaCourt

    ==========================================================
    """

    MAX_DOCUMENTS = 5

    MAX_CHARS_PER_DOCUMENT = 1800

    def __init__(self):

        logger.info(

            "Context Builder iniciado."

        )

    ####################################################################
    ###################### CONSTRUIR CONTEXTO ###########################
    ####################################################################

    def build(
        self,
        query: str,
        documents: List[Dict]
    ) -> str:

        """
        Construye el contexto jurídico que
        será enviado al modelo de lenguaje.
        """

        if not documents:

            return ""

        documents = documents[:self.MAX_DOCUMENTS]

        context = [

            "CONSULTA DEL USUARIO",

            query,

            "",

            "DOCUMENTOS RELEVANTES",

            ""
        ]

        for index, document in enumerate(documents, start=1):

            context.append(

                self._build_document_context(

                    index,

                    document

                )

            )

        final_context = "\n\n".join(context)

        logger.info(

            f"Contexto generado ({len(final_context)} caracteres)."

        )

        return final_context

    ####################################################################
    ################### CONTEXTO DE UN DOCUMENTO ########################
    ####################################################################

    def _build_document_context(
        self,
        index: int,
        document: Dict
    ) -> str:

        """
        Construye el contexto individual
        de un documento jurídico.
        """

        texto = (
            document.get("texto")
            or ""
        )[:self.MAX_CHARS_PER_DOCUMENT]

        resumen = (
            document.get("resumen")
            or "No disponible."
        )

        contexto = f"""
================ DOCUMENTO {index} ================

Título:
{document.get("articulo") or document.get("fuente")}

Tipo de documento:
{document.get("tipo_documento")}

Jerarquía:
{document.get("jerarquia")}

Rama:
{document.get("rama")}

Órgano emisor:
{document.get("organo_emisor")}

Expediente:
{document.get("expediente")}

Materia:
{document.get("materia")}

Instancia:
{document.get("instancia")}

Número:
{document.get("numero")}

Fecha de resolución:
{document.get("fecha_resolucion")}

Fecha de publicación:
{document.get("fecha_publicacion")}

Precedente vinculante:
{document.get("precedente_vinculante")}

Sumilla:
{document.get("sumilla")}

Resumen:
{resumen}

Texto relevante:
{texto}

==================================================
"""

        return contexto.strip()

    ####################################################################
    ######################## VALIDACIÓN ################################
    ####################################################################

    @staticmethod
    def is_valid_context(
        context: str
    ) -> bool:

        """
        Verifica que el contexto no esté vacío
        y tenga suficiente contenido.
        """

        if context is None:
            return False

        if len(context.strip()) < 50:
            return False

        return True

    ####################################################################
    ######################## ESTADÍSTICAS ###############################
    ####################################################################

    @staticmethod
    def statistics(
        context: str
    ) -> Dict:

        """
        Devuelve información útil del contexto
        construido.
        """

        lines = context.splitlines()

        words = context.split()

        return {

            "characters": len(context),

            "words": len(words),

            "lines": len(lines)

        }

    ####################################################################
    ######################## DEBUG #####################################
    ####################################################################

    @staticmethod
    def print_debug(
        context: str
    ) -> None:

        """
        Imprime el contexto generado.

        Solo para desarrollo.
        """

        logger.info(
            "========== CONTEXT =========="
        )

        logger.info(context)

        logger.info(
            "============================="
        )