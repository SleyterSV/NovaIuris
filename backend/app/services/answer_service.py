import os
import logging
from typing import Dict

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

logger = logging.getLogger(
    "NovaIuris.Answer"
)


class AnswerService:
    """
    ===========================================================

                    NOVA ANSWER ENGINE

    Servicio encargado de generar
    la respuesta jurídica final.

    Este servicio recibe:

        • Consulta del usuario

        • Contexto construido

    Devuelve:

        • Respuesta jurídica fundamentada

    Utilizado por:

        • NovaSearch

        • NovaCase

        • NovaCourt

    ===========================================================
    """

    MODEL = "gpt-4o-mini"

    TEMPERATURE = 0.1

    def __init__(self):

        api_key = os.getenv(
            "OPENAI_API_KEY"
        )

        if not api_key:

            raise ValueError(
                "OPENAI_API_KEY no encontrada."
            )

        self.client = OpenAI(
            max_retries=0,
            api_key=api_key
        )

    ####################################################################
    ######################## PROMPT PRINCIPAL ###########################
    ####################################################################

    @staticmethod
    def build_prompt(
        query: str,
        context: str
    ) -> str:

        """
        Construye el prompt que será enviado
        al modelo de lenguaje.
        """

        return f"""
Eres Nova Iuris, un asistente jurídico peruano de nivel profesional.

Tu función es responder EXCLUSIVAMENTE utilizando la información contenida en el contexto proporcionado.

REGLAS OBLIGATORIAS

REGLA DE TRAZABILIDAD: cada fuente del contexto tiene un marcador [SRC-...]. Usa únicamente esos marcadores al citar; no inventes marcadores ni conviertas menciones legales en citas de respaldo.

1. No inventes normas.

2. No inventes jurisprudencia.

3. No inventes artículos.

4. No inventes expedientes.

5. No inventes precedentes.

6. Si la información no aparece en el contexto, indícalo expresamente.

7. Si existen varias posiciones jurisprudenciales, explícalas.

8. Prioriza siempre:

   • Constitución

   • Tribunal Constitucional

   • Corte Suprema

   • Plenos Casatorios

   • Casaciones

   • Leyes

9. Si existe un precedente vinculante, indícalo.

10. Utiliza lenguaje jurídico profesional.

11. Nunca respondas con opiniones personales.

12. No cites información fuera del contexto.

------------------------------------------------------------

CONSULTA DEL USUARIO

{query}

------------------------------------------------------------

CONTEXTO JURÍDICO

{context}

------------------------------------------------------------

FORMATO DE RESPUESTA

## Respuesta

(Explica claramente la respuesta jurídica.)

## Fundamento jurídico

(Menciona las normas, jurisprudencia o criterios utilizados.)

## Jurisprudencia relevante

(Lista los expedientes, casaciones o sentencias utilizadas.)

## Conclusión

(Conclusión breve y concreta.)

"""

    ####################################################################
    ###################### GENERAR RESPUESTA ############################
    ####################################################################

    @staticmethod
    def build_grounded_v2_prompt(query: str, context: str) -> str:
        """V2 claims must be supported by the exact units supplied in context."""
        return f"""Responde la consulta jurídica usando exclusivamente las unidades V2 siguientes.
Cada afirmación jurídica sustantiva debe ir acompañada del marcador [SRC-...] de
la unidad que la sostiene. No cites fuentes fuera de este contexto. No deduzcas
una causa de la parte resolutiva: improcedencia, inadmisibilidad o rechazo no
demuestran por sí solos el motivo. Explica motivos solo si un fundamento
recuperado los afirma expresamente. Si falta soporte, indícalo sin especular.
Para una pregunta sobre la decisión, usa primero la unidad de decisión.

Consulta: {query}

Unidades verificadas:
{context}
"""

    @staticmethod
    def exact_source_answer(source: dict) -> Dict:
        excerpt = str(source.get("excerpt") or "").strip()
        if not excerpt or not source.get("source_id"):
            return {"success": False, "answer": ""}
        title = source.get("title") or "la fuente recuperada"
        return {"success": True,
                "answer": f"Según {title}: «{excerpt}» [{source['source_id']}]."}

    @staticmethod
    def exact_decision_answer(source: dict) -> Dict:
        excerpt = str(source.get("excerpt") or "").strip()
        if not excerpt or not source.get("source_id") or \
                (source.get("metadata") or {}).get("unit_type") != "decision":
            return {"success": False, "answer": ""}
        title = source.get("title") or "el documento recuperado"
        return {"success": True,
                "answer": f"La parte resolutiva de {title} establece: «{excerpt}» [{source['source_id']}]."}

    def generate_answer(
        self,
        query: str,
        context: str,
        *,
        grounded_v2: bool = False,
    ) -> Dict:

        """
        Genera la respuesta jurídica final
        utilizando el contexto construido.
        """

        if not context.strip():

            return {

                "success": False,

                "answer": (
                    "No se encontró información jurídica "
                    "suficiente para responder la consulta."
                )

            }

        prompt_builder = self.build_grounded_v2_prompt if grounded_v2 else self.build_prompt
        prompt = prompt_builder(

            query=query,

            context=context

        )

        logger.info(

            "Generando respuesta jurídica..."

        )

        try:

            response = self.client.chat.completions.create(

                model=self.MODEL,

                messages=[

                    {

                        "role": "system",

                        "content": (
                            "Eres Nova Iuris, un investigador jurídico "
                            "especializado en Derecho peruano."
                        )

                    },

                    {

                        "role": "user",

                        "content": prompt

                    }

                ]

            )

            answer = (

                response

                .choices[0]

                .message

                .content

                .strip()

            )

            logger.info(

                "Respuesta generada correctamente."

            )

            return {

                "success": True,

                "answer": answer

            }

        except Exception as e:

            logger.exception(

                f"Error generando respuesta: {e}"

            )

            return {

                "success": False,

                "answer": (
                    "Ocurrió un error al generar "
                    "la respuesta jurídica."
                )

            }

    ####################################################################
    ###################### LIMPIEZA RESPUESTA ###########################
    ####################################################################

    @staticmethod
    def clean_answer(
        answer: str
    ) -> str:

        """
        Limpia espacios innecesarios
        de la respuesta generada.
        """

        if not answer:
            return ""

        answer = answer.replace("\r", "")

        while "\n\n\n" in answer:

            answer = answer.replace(
                "\n\n\n",
                "\n\n"
            )

        return answer.strip()

    ####################################################################
    ######################## VALIDACIÓN ################################
    ####################################################################

    @staticmethod
    def is_valid_answer(
        answer: str
    ) -> bool:

        """
        Verifica que la respuesta
        tenga contenido suficiente.
        """

        if answer is None:
            return False

        if len(answer.strip()) < 50:
            return False

        return True

    ####################################################################
    ######################## ESTADÍSTICAS ###############################
    ####################################################################

    @staticmethod
    def statistics(
        answer: str
    ) -> Dict:

        """
        Devuelve estadísticas de la
        respuesta generada.
        """

        return {

            "characters": len(answer),

            "words": len(answer.split()),

            "lines": len(answer.splitlines())

        }

    ####################################################################
    ######################## DEBUG #####################################
    ####################################################################

    @staticmethod
    def print_debug(
        answer: str
    ) -> None:

        """
        Imprime la respuesta generada.

        Solo para desarrollo.
        """

        logger.info(
            "========== ANSWER =========="
        )

        logger.info(answer)

        logger.info(
            "============================"
        )
