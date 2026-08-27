import json
import logging
from typing import Dict
from typing import List

from openai import OpenAI

from app.config import Config


logger = logging.getLogger(
    "NovaIuris.CounterArgumentService"
)


class CounterArgumentService:
    """
    ==========================================================

            NOVA COUNTER ARGUMENT SERVICE

    Simula la estrategia jurídica de la contraparte.

    Analiza:

        • Posibles argumentos del demandado

        • Posibles excepciones

        • Posibles defensas

        • Ataques a la prueba

        • Ataques a la estrategia

        • Ataques a la jurisprudencia

        • Riesgos para nuestro caso

        • Refutaciones recomendadas

    NO genera la estrategia principal.

    NO analiza nuevamente el caso.

    NO modifica los argumentos.

    Su única responsabilidad consiste en
    pensar como el abogado de la contraparte.

    Será utilizado por:

        • NovaCase

        • NovaCourt

        • Tribunal Multiagente

    ==========================================================
    """

    MODEL = "gpt-5"

    def __init__(self):

        self.client = OpenAI(

            api_key=Config.OPENAI_API_KEY

        )

        logger.info(

            "Counter Argument Service iniciado."

        )

    ####################################################################
    ################ GENERAR CONTRAARGUMENTOS ###########################
    ####################################################################

    def generate_counterarguments(
        self,
        analysis: Dict,
        strategy: Dict,
        arguments: Dict,
        evidence: Dict,
        risk: Dict,
        documents: List[Dict]
    ) -> Dict:

        """
        Simula el razonamiento del abogado
        de la contraparte.

        Analiza:

            • Argumentos que utilizaría

            • Excepciones procesales

            • Debilidades de nuestra estrategia

            • Ataques a la prueba

            • Ataques a la jurisprudencia

            • Riesgos adicionales

        Devuelve un análisis estructurado.
        """

        logger.info(

            "Generando contraargumentos..."

        )

        prompt = self._build_prompt(

            analysis=analysis,

            strategy=strategy,

            arguments=arguments,

            evidence=evidence,

            risk=risk,

            documents=documents

        )

        response = self.client.chat.completions.create(

            model=self.MODEL,

            messages=[

                {

                    "role": "system",

                    "content":

                        "Eres un abogado litigante peruano "

                        "especialista en defensa judicial. "

                        "Debes pensar como la contraparte "

                        "y devolver únicamente un JSON válido."

                },

                {

                    "role": "user",

                    "content": prompt

                }

            ]

        )

        content = response.choices[0].message.content

        counterarguments = self._safe_parse_json(

            content

        )

        if not self.validate_counterarguments(

            counterarguments

        ):

            logger.warning(

                "Los contraargumentos no pasaron la validación."

            )

        logger.info(

            "Contraargumentos generados correctamente."

        )

        return counterarguments

    ####################################################################
    ######################## PROMPT PRINCIPAL ###########################
    ####################################################################

    @staticmethod
    def _build_prompt(
        analysis: Dict,
        strategy: Dict,
        arguments: Dict,
        evidence: Dict,
        risk: Dict,
        documents: List[Dict]
    ) -> str:

        analysis_json = json.dumps(

            analysis,

            indent=4,

            ensure_ascii=False

        )

        strategy_json = json.dumps(

            strategy,

            indent=4,

            ensure_ascii=False

        )

        arguments_json = json.dumps(

            arguments,

            indent=4,

            ensure_ascii=False

        )

        evidence_json = json.dumps(

            evidence,

            indent=4,

            ensure_ascii=False

        )

        risk_json = json.dumps(

            risk,

            indent=4,

            ensure_ascii=False

        )

        documents_json = json.dumps(

            documents,

            indent=2,

            ensure_ascii=False

        )

        return f"""
Eres un abogado litigante peruano que representa exclusivamente a la contraparte.

Has participado durante más de 30 años en litigios civiles, laborales, penales, constitucionales y administrativos.

========================================================

NO representas al demandante.

Representas únicamente al DEMANDADO.

Tu misión consiste en derrotar la estrategia del demandante.

Debes identificar todas las debilidades posibles.

No inventes hechos.

No inventes jurisprudencia.

No inventes normas.

No inventes pruebas.

Utiliza únicamente la información recibida.

========================================================

Analiza:

1. Argumentos que utilizaría la contraparte.

2. Excepciones procesales.

3. Defensas jurídicas.

4. Ataques contra los argumentos.

5. Ataques contra las pruebas.

6. Ataques contra la jurisprudencia utilizada.

7. Riesgos que aprovecharía la contraparte.

8. Vacíos probatorios.

9. Vacíos jurídicos.

10. Documentos cuya autenticidad podría cuestionarse.

11. Estrategia recomendada para la contraparte.

12. Probabilidad estimada de éxito de la contraparte.

========================================================

Devuelve EXCLUSIVAMENTE este JSON.

{{
    "main_counterarguments": [],

    "procedural_exceptions": [],

    "legal_defenses": [],

    "attacks_on_arguments": [],

    "attacks_on_evidence": [],

    "attacks_on_jurisprudence": [],

    "identified_weaknesses": [],

    "recommended_strategy": [],

    "recommended_evidence": [],

    "opponent_observations": [],

    "opponent_success_probability": 0

}}

========================================================

ANÁLISIS DEL CASO

{analysis_json}

========================================================

ESTRATEGIA DEL DEMANDANTE

{strategy_json}

========================================================

ARGUMENTOS DEL DEMANDANTE

{arguments_json}

========================================================

ANÁLISIS PROBATORIO

{evidence_json}

========================================================

ANÁLISIS DE RIESGO

{risk_json}

========================================================

DOCUMENTOS RECUPERADOS POR NOVASEARCH

{documents_json}

========================================================

IMPORTANTE

No favorezcas al demandante.

Busca todas las debilidades posibles.

Identifica cualquier vacío jurídico.

Identifica cualquier vacío probatorio.

Evalúa cómo respondería un abogado experimentado.

Asigna una probabilidad de éxito de la contraparte entre 0 y 100.

========================================================

Devuelve únicamente el JSON.

No escribas explicaciones.

No utilices Markdown.

No agregues comentarios.

No agregues texto adicional.
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

        Si el modelo devuelve Markdown, texto adicional
        o un JSON parcialmente encapsulado, intenta
        recuperarlo automáticamente.
        """

        if not response:

            return {}

        try:

            return json.loads(

                response

            )

        except Exception:

            pass

        ############################################################
        ################ ELIMINAR MARKDOWN ##########################
        ############################################################

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

        ############################################################
        ################ BUSCAR JSON ###############################
        ############################################################

        try:

            start = cleaned.index("{")

            end = cleaned.rindex("}") + 1

            cleaned = cleaned[start:end]

            return json.loads(

                cleaned

            )

        except Exception as error:

            logger.error(

                f"No fue posible interpretar los contraargumentos: {error}"

            )

            logger.debug(

                f"Respuesta recibida:\n{response}"

            )

            return {

                "main_counterarguments": [],

                "procedural_exceptions": [],

                "legal_defenses": [],

                "attacks_on_arguments": [],

                "attacks_on_evidence": [],

                "attacks_on_jurisprudence": [],

                "identified_weaknesses": [],

                "recommended_strategy": [],

                "recommended_evidence": [],

                "opponent_observations": [],

                "opponent_success_probability": 0

            }

    ####################################################################
    ################ VALIDAR CONTRAARGUMENTOS ###########################
    ####################################################################

    @staticmethod
    def validate_counterarguments(
        counterarguments: Dict
    ) -> bool:

        """
        Verifica que la estructura generada
        tenga todos los campos necesarios.
        """

        required_fields = [

            "main_counterarguments",

            "procedural_exceptions",

            "legal_defenses",

            "attacks_on_arguments",

            "attacks_on_evidence",

            "attacks_on_jurisprudence",

            "identified_weaknesses",

            "recommended_strategy",

            "recommended_evidence",

            "opponent_observations",

            "opponent_success_probability"

        ]

        for field in required_fields:

            if field not in counterarguments:

                logger.warning(

                    f"Campo faltante: {field}"

                )

                return False

        probability = counterarguments.get(

            "opponent_success_probability",

            0

        )

        if not isinstance(

            probability,

            (int, float)

        ):

            logger.warning(

                "opponent_success_probability no es numérico."

            )

            return False

        if probability < 0 or probability > 100:

            logger.warning(

                "opponent_success_probability fuera del rango permitido."

            )

            return False

        return True

    ####################################################################
    ###################### RESUMEN EJECUTIVO ############################
    ####################################################################

    @staticmethod
    def summary(
        counterarguments: Dict
    ) -> Dict:

        """
        Devuelve un resumen ejecutivo de los
        contraargumentos generados.
        """

        return {

            "main_counterarguments":

                len(

                    counterarguments.get(

                        "main_counterarguments",

                        []

                    )

                ),

            "procedural_exceptions":

                len(

                    counterarguments.get(

                        "procedural_exceptions",

                        []

                    )

                ),

            "legal_defenses":

                len(

                    counterarguments.get(

                        "legal_defenses",

                        []

                    )

                ),

            "identified_weaknesses":

                len(

                    counterarguments.get(

                        "identified_weaknesses",

                        []

                    )

                ),

            "opponent_success_probability":

                counterarguments.get(

                    "opponent_success_probability",

                    0

                )

        }

    ####################################################################
    ######################## ESTADÍSTICAS ###############################
    ####################################################################

    @staticmethod
    def statistics(
        counterarguments: Dict
    ) -> Dict:

        """
        Genera estadísticas generales del
        análisis de la contraparte.
        """

        return {

            "counterarguments":

                len(

                    counterarguments.get(

                        "main_counterarguments",

                        []

                    )

                ),

            "procedural_exceptions":

                len(

                    counterarguments.get(

                        "procedural_exceptions",

                        []

                    )

                ),

            "legal_defenses":

                len(

                    counterarguments.get(

                        "legal_defenses",

                        []

                    )

                ),

            "attacks_on_arguments":

                len(

                    counterarguments.get(

                        "attacks_on_arguments",

                        []

                    )

                ),

            "attacks_on_evidence":

                len(

                    counterarguments.get(

                        "attacks_on_evidence",

                        []

                    )

                ),

            "attacks_on_jurisprudence":

                len(

                    counterarguments.get(

                        "attacks_on_jurisprudence",

                        []

                    )

                ),

            "identified_weaknesses":

                len(

                    counterarguments.get(

                        "identified_weaknesses",

                        []

                    )

                )

        }

    ####################################################################
    ###################### SCORE CONTRAPARTE ############################
    ####################################################################

    @staticmethod
    def calculate_opponent_score(
        counterarguments: Dict
    ) -> float:

        """
        Devuelve la probabilidad estimada
        de éxito de la contraparte.
        """

        return round(

            float(

                counterarguments.get(

                    "opponent_success_probability",

                    0

                )

            ),

            2

        )

    ####################################################################
    ###################### COLOR DEL RIESGO #############################
    ####################################################################

    @staticmethod
    def opponent_risk_color(
        probability: float
    ) -> str:

        """
        Devuelve un color para representar
        la fortaleza de la contraparte.
        """

        if probability >= 80:

            return "red"

        if probability >= 60:

            return "orange"

        if probability >= 40:

            return "yellow"

        return "green"

    ####################################################################
    ######################## DEBUG ######################################
    ####################################################################

    @staticmethod
    def print_debug(
        counterarguments: Dict
    ) -> None:

        """
        Imprime el análisis completo
        de la contraparte.

        Solo para desarrollo.
        """

        logger.info(

            "====== COUNTER ARGUMENTS ======"

        )

        logger.info(

            json.dumps(

                counterarguments,

                indent=4,

                ensure_ascii=False

            )

        )

        logger.info(

            "==============================="
        )