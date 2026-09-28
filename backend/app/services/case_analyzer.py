import json
import logging
from typing import Dict
from typing import List

from openai import OpenAI

from app.config import Config


logger = logging.getLogger(
    "NovaIuris.CaseAnalyzer"
)


class CaseAnalyzer:
    """
    ==========================================================

                    NOVA CASE ANALYZER

    Analiza un caso jurídico y extrae automáticamente:

        • Rama del Derecho
        • Tipo de proceso
        • Pretensión
        • Partes
        • Hechos relevantes
        • Problemas jurídicos
        • Palabras clave
        • Normas aplicables
        • Documentos mencionados

    Este servicio NO genera respuestas.

    Solo estructura el caso para que los demás
    servicios trabajen sobre información organizada.

    Será utilizado por:

        • NovaCase

        • NovaCourt

        • Tribunal Multiagente

    ==========================================================
    """

    def __init__(self):

        self.client = OpenAI(
            max_retries=0,
            api_key=Config.OPENAI_API_KEY
        )

        logger.info(
            "Case Analyzer iniciado."
        )

    ####################################################################
    ######################## ANALISIS PRINCIPAL #########################
    ####################################################################

    def analyze_case(
        self,
        case_text: str
    ) -> Dict:

        """
        Analiza un caso jurídico y devuelve una estructura
        organizada que será utilizada por NovaCase.
        """

        logger.info(
            "Analizando caso jurídico..."
        )

        prompt = self._build_prompt(case_text)

        response = self.client.chat.completions.create(

            model="gpt-5",

            messages=[

                {
                    "role": "system",
                    "content": (
                        "Eres un abogado peruano experto en análisis jurídico. "
                        "Tu única función es analizar un caso y devolver "
                        "EXCLUSIVAMENTE un objeto JSON válido."
                    )
                },

                {
                    "role": "user",
                    "content": prompt
                }

            ]

        )

        content = response.choices[0].message.content

        analysis = self._safe_parse_json(
            content
        )

        logger.info(
            "Caso analizado correctamente."
        )

        return analysis

    ####################################################################
    ######################## PROMPT PRINCIPAL ###########################
    ####################################################################

    @staticmethod
    def _build_prompt(
        case_text: str
    ) -> str:

        return f"""
Eres un abogado litigante peruano con amplia experiencia en Derecho.

Debes analizar el caso recibido y devolver EXCLUSIVAMENTE un JSON válido.

NO expliques.

NO redactes estrategias.

NO emitas conclusiones.

NO cites jurisprudencia.

NO respondas preguntas.

Solo analiza el caso.

========================================================

Extrae la siguiente información:

1. Rama principal del Derecho.

2. Tipo de proceso.

3. Pretensión principal.

4. Pretensiones secundarias.

5. Partes involucradas.

6. Hechos relevantes ordenados cronológicamente.

7. Problemas jurídicos.

8. Palabras clave.

9. Normas que probablemente serán aplicables.

10. Posibles documentos mencionados.

11. Posibles pruebas.

12. Riesgos procesales detectados.

13. Vacíos de información del caso.

========================================================

Los hechos del relato son alegaciones; no los presentes como probados.
En hechos_estructurados usa objetos con text, status, date y source_ids.
status puede ser alleged, supported, disputed o unclear. Usa supported solo
si un fragmento documental concreto lo respalda; distingue un documento que
menciona una alegación de uno que acredita un hecho.
source_ids solo puede contener marcadores SRC proporcionados en el caso.
No inventes fechas ni referencias. Formula problemas jurídicos concretos
relacionados con las circunstancias del caso. normas_probables son hipótesis
para investigar, no autoridades verificadas.

Devuelve únicamente este formato JSON.

{{
    "rama": "",

    "tipo_proceso": "",

    "pretension_principal": "",

    "pretensiones_secundarias": [],

    "partes": {{

        "demandante": "",

        "demandado": ""

    }},

    "hechos": [],

    "hechos_estructurados": [],

    "problemas_juridicos": [],

    "palabras_clave": [],

    "normas_probables": [],

    "documentos_detectados": [],

    "pruebas_detectadas": [],

    "riesgos": [],

    "informacion_faltante": []

}}

========================================================

CASO

{case_text}

========================================================

Responde únicamente con JSON.
"""
    ####################################################################
    ######################## PARSER SEGURO ##############################
    ####################################################################

    @staticmethod
    def _safe_parse_json(
        response: str
    ) -> Dict:

        """
        Convierte la respuesta del LLM en un diccionario.

        Si el modelo devuelve texto adicional o bloques
        Markdown, intenta recuperar el JSON automáticamente.
        """

        if not response:

            return {}

        try:

            return json.loads(
                response
            )

        except Exception:

            pass

        # ------------------------------------------------------------
        # Eliminar bloques ```json ... ```
        # ------------------------------------------------------------

        cleaned = (

            response

            .replace("```json", "")

            .replace("```JSON", "")

            .replace("```", "")

            .strip()

        )

        try:

            return json.loads(
                cleaned
            )

        except Exception:

            pass

        # ------------------------------------------------------------
        # Buscar el primer '{' y el último '}'
        # ------------------------------------------------------------

        try:

            start = cleaned.index("{")

            end = cleaned.rindex("}") + 1

            cleaned = cleaned[start:end]

            return json.loads(
                cleaned
            )

        except Exception as error:

            logger.error(

                f"No fue posible interpretar el JSON: {error}"

            )

            logger.debug("Model response omitted from logs")

            return {

                "rama": "",

                "tipo_proceso": "",

                "pretension_principal": "",

                "pretensiones_secundarias": [],

                "partes": {

                    "demandante": "",

                    "demandado": ""

                },

                "hechos": [],

                "problemas_juridicos": [],

                "palabras_clave": [],

                "normas_probables": [],

                "documentos_detectados": [],

                "pruebas_detectadas": [],

                "riesgos": [],

                "informacion_faltante": []

            }

    ####################################################################
    ###################### VALIDAR ANALISIS #############################
    ####################################################################

    @staticmethod
    def validate_analysis(
        analysis: Dict
    ) -> bool:

        """
        Verifica que el análisis tenga la estructura mínima
        esperada por NovaCase.
        """

        required_fields = [

            "rama",

            "tipo_proceso",

            "pretension_principal",

            "hechos",

            "problemas_juridicos",

            "palabras_clave",

            "normas_probables"

        ]

        for field in required_fields:

            if field not in analysis:

                logger.warning(

                    f"Campo faltante: {field}"

                )

                return False

        return True

    ####################################################################
    ###################### RESUMEN RAPIDO ###############################
    ####################################################################

    @staticmethod
    def summary(
        analysis: Dict
    ) -> Dict:

        """
        Devuelve un resumen ejecutivo del análisis.

        Será utilizado por la interfaz de NovaCase.
        """

        return {

            "rama":

                analysis.get("rama"),

            "tipo_proceso":

                analysis.get("tipo_proceso"),

            "pretension":

                analysis.get(

                    "pretension_principal"

                ),

            "problemas":

                len(

                    analysis.get(

                        "problemas_juridicos",

                        []

                    )

                ),

            "hechos":

                len(

                    analysis.get(

                        "hechos",

                        []

                    )

                ),

            "normas":

                len(

                    analysis.get(

                        "normas_probables",

                        []

                    )

                )

        }

    ####################################################################
    ###################### ESTADISTICAS ################################
    ####################################################################

    @staticmethod
    def statistics(
        analysis: Dict
    ) -> Dict:

        """
        Genera estadísticas generales del caso.

        Estas métricas servirán para mostrar
        información en el Dashboard.
        """

        return {

            "keywords":

                len(

                    analysis.get(

                        "palabras_clave",

                        []

                    )

                ),

            "documents":

                len(

                    analysis.get(

                        "documentos_detectados",

                        []

                    )

                ),

            "evidence":

                len(

                    analysis.get(

                        "pruebas_detectadas",

                        []

                    )

                ),

            "risks":

                len(

                    analysis.get(

                        "riesgos",

                        []

                    )

                ),

            "missing_information":

                len(

                    analysis.get(

                        "informacion_faltante",

                        []

                    )

                )

        }

    ####################################################################
    ###################### DEBUG #######################################
    ####################################################################

    @staticmethod
    def print_debug(
        analysis: Dict
    ) -> None:

        """
        Imprime el análisis generado.

        Solo para desarrollo.
        """

        logger.info(

            "========== CASE ANALYSIS =========="

        )

        logger.info(

            json.dumps(

                analysis,

                indent=4,

                ensure_ascii=False

            )

        )

        logger.info(

            "==================================="

        )
