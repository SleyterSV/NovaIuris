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

    def generate_answer(
        self,
        query: str,
        context: str
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

        prompt = self.build_prompt(

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