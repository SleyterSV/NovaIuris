import json
import logging
from typing import Dict
from typing import List

from openai import OpenAI

from app.config import Config


logger = logging.getLogger(
    "NovaIuris.RiskAnalyzer"
)


class RiskAnalyzer:
    """
    ==========================================================

                NOVA RISK ANALYZER

    Evalúa la solidez jurídica del caso.

    Analiza:

        • Probabilidad de éxito

        • Riesgos procesales

        • Debilidades

        • Fortalezas

        • Vacíos probatorios

        • Riesgos de estrategia

        • Riesgos jurídicos

        • Recomendaciones

    NO genera argumentos.

    NO busca documentos.

    NO modifica la estrategia.

    Su función es evaluar objetivamente
    la viabilidad del caso.

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

            "Risk Analyzer iniciado."

        )

    ####################################################################
    ######################## ANALIZAR RIESGOS ###########################
    ####################################################################

    def analyze(
        self,
        analysis: Dict,
        strategy: Dict,
        arguments: Dict,
        documents: List[Dict]
    ) -> Dict:

        """
        Evalúa la viabilidad jurídica del caso.

        Analiza:

            • Riesgos procesales

            • Riesgos jurídicos

            • Probabilidad estimada de éxito

            • Debilidades probatorias

            • Fortalezas

            • Información faltante

        Devuelve una evaluación estructurada.
        """

        logger.info(

            "Analizando riesgos del caso..."

        )

        prompt = self._build_prompt(

            analysis=analysis,

            strategy=strategy,

            arguments=arguments,

            documents=documents

        )

        response = self.client.chat.completions.create(

            model=self.MODEL,

            messages=[

                {
                    "role": "system",
                    "content": (
                        "Eres un abogado litigante peruano "
                        "especialista en evaluación estratégica "
                        "de riesgos procesales. "
                        "Debes devolver únicamente un JSON válido."
                    )
                },

                {
                    "role": "user",
                    "content": prompt
                }

            ]

        )

        content = response.choices[0].message.content

        risk = self._safe_parse_json(

            content

        )

        if not self.validate_risk(

            risk

        ):

            logger.warning(

                "La evaluación de riesgos no pasó la validación."

            )

        logger.info(

            "Evaluación de riesgos completada."

        )

        return risk
    
    ####################################################################
    ######################## PROMPT PRINCIPAL ###########################
    ####################################################################

    @staticmethod
    def _build_prompt(
        analysis: Dict,
        strategy: Dict,
        arguments: Dict,
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

        documents_json = json.dumps(

            documents,

            indent=2,

            ensure_ascii=False

        )

        return f"""
Eres un magistrado peruano con más de 30 años de experiencia.

Especialista en:

• Derecho Constitucional

• Derecho Civil

• Derecho Penal

• Derecho Laboral

• Derecho Administrativo

• Derecho Procesal

• Valoración probatoria

• Litigación Estratégica

========================================================

NO eres abogado del demandante.

NO eres abogado del demandado.

Tu función consiste únicamente en evaluar objetivamente la fortaleza del caso.

No inventes normas.

No inventes jurisprudencia.

No inventes hechos.

No favorezcas a ninguna de las partes.

Debes comportarte como un juez imparcial.

========================================================

Evalúa:

1. Probabilidad estimada de éxito (0-100).

2. Nivel general de riesgo.

3. Riesgos procesales.

4. Riesgos jurídicos.

5. Riesgos probatorios.

6. Fortalezas del caso.

7. Debilidades del caso.

8. Medios probatorios faltantes.

9. Documentos que deberían obtenerse.

10. Aspectos que probablemente observaría un juez.

11. Recomendaciones antes de presentar la demanda.

12. Información crítica que aún falta recopilar.

========================================================

Devuelve EXCLUSIVAMENTE este JSON.

{{
    "overall_probability": 0,

    "risk_level": "",

    "critical_risks": [],

    "procedural_risks": [],

    "legal_risks": [],

    "evidentiary_risks": [],

    "strengths": [],

    "weaknesses": [],

    "missing_evidence": [],

    "missing_documents": [],

    "judge_observations": [],

    "recommendations": [],

    "missing_information": []

}}

========================================================

ANÁLISIS DEL CASO

{analysis_json}

========================================================

ESTRATEGIA

{strategy_json}

========================================================

ARGUMENTOS JURÍDICOS

{arguments_json}

========================================================

DOCUMENTOS RECUPERADOS POR NOVASEARCH

{documents_json}

========================================================

IMPORTANTE

La probabilidad de éxito debe estar fundamentada únicamente en la información disponible.

Si faltan pruebas importantes, disminuye la probabilidad.

Si existen riesgos procesales importantes, disminuye la probabilidad.

Si la jurisprudencia encontrada favorece claramente el caso, aumenta la probabilidad.

Si existen vacíos relevantes de información, indícalos.

========================================================

Devuelve únicamente el JSON.

No utilices Markdown.

No escribas explicaciones.

No agregues comentarios.

No escribas texto adicional.
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

                f"No fue posible interpretar la evaluación de riesgos: {error}"

            )

            logger.debug(

                f"Respuesta recibida:\n{response}"

            )

            return {

                "overall_probability": 0,

                "risk_level": "DESCONOCIDO",

                "critical_risks": [],

                "procedural_risks": [],

                "legal_risks": [],

                "evidentiary_risks": [],

                "strengths": [],

                "weaknesses": [],

                "missing_evidence": [],

                "missing_documents": [],

                "judge_observations": [],

                "recommendations": [],

                "missing_information": []

            }

    ####################################################################
    ###################### VALIDAR RESULTADO ############################
    ####################################################################

    @staticmethod
    def validate_risk(
        risk: Dict
    ) -> bool:

        """
        Verifica que el análisis de riesgos tenga
        la estructura mínima esperada.
        """

        required_fields = [

            "overall_probability",

            "risk_level",

            "critical_risks",

            "procedural_risks",

            "legal_risks",

            "evidentiary_risks",

            "strengths",

            "weaknesses",

            "missing_evidence",

            "missing_documents",

            "judge_observations",

            "recommendations",

            "missing_information"

        ]

        for field in required_fields:

            if field not in risk:

                logger.warning(

                    f"Campo faltante: {field}"

                )

                return False

        probability = risk.get(

            "overall_probability",

            0

        )

        if not isinstance(

            probability,

            (int, float)

        ):

            logger.warning(

                "overall_probability no es numérico."

            )

            return False

        if probability < 0 or probability > 100:

            logger.warning(

                "overall_probability fuera del rango permitido."

            )

            return False

        return True

    ####################################################################
    ###################### RESUMEN EJECUTIVO ###########################
    ####################################################################

    @staticmethod
    def summary(
        risk: Dict
    ) -> Dict:

        """
        Devuelve un resumen ejecutivo del análisis
        de riesgos.
        """

        return {

            "overall_probability":

                risk.get(

                    "overall_probability",

                    0

                ),

            "risk_level":

                risk.get(

                    "risk_level",

                    "DESCONOCIDO"

                ),

            "critical_risks":

                len(

                    risk.get(

                        "critical_risks",

                        []

                    )

                ),

            "recommendations":

                len(

                    risk.get(

                        "recommendations",

                        []

                    )

                )

        }

    ####################################################################
    ###################### ESTADISTICAS ################################
    ####################################################################

    @staticmethod
    def statistics(
        risk: Dict
    ) -> Dict:

        """
        Genera estadísticas del análisis
        de riesgos.
        """

        return {

            "critical_risks":

                len(

                    risk.get(

                        "critical_risks",

                        []

                    )

                ),

            "procedural_risks":

                len(

                    risk.get(

                        "procedural_risks",

                        []

                    )

                ),

            "legal_risks":

                len(

                    risk.get(

                        "legal_risks",

                        []

                    )

                ),

            "evidentiary_risks":

                len(

                    risk.get(

                        "evidentiary_risks",

                        []

                    )

                ),

            "strengths":

                len(

                    risk.get(

                        "strengths",

                        []

                    )

                ),

            "weaknesses":

                len(

                    risk.get(

                        "weaknesses",

                        []

                    )

                )

        }

    ####################################################################
    ###################### SCORE DEL CASO ###############################
    ####################################################################

    @staticmethod
    def calculate_case_score(
        risk: Dict
    ) -> float:

        """
        Devuelve el score estimado del caso.

        Se utiliza para el Dashboard.
        """

        return round(

            float(

                risk.get(

                    "overall_probability",

                    0

                )

            ),

            2

        )

    ####################################################################
    ###################### COLOR DEL RIESGO #############################
    ####################################################################

    @staticmethod
    def risk_color(
        probability: float
    ) -> str:

        """
        Devuelve un color para representar
        visualmente el riesgo.

        Verde: Muy favorable

        Amarillo: Riesgo medio

        Rojo: Riesgo alto
        """

        if probability >= 80:

            return "green"

        if probability >= 60:

            return "yellow"

        if probability >= 40:

            return "orange"

        return "red"

    ####################################################################
    ###################### DEBUG #######################################
    ####################################################################

    @staticmethod
    def print_debug(
        risk: Dict
    ) -> None:

        """
        Imprime el análisis de riesgos.

        Solo para desarrollo.
        """

        logger.info(

            "========== RISK ANALYSIS =========="

        )

        logger.info(

            json.dumps(

                risk,

                indent=4,

                ensure_ascii=False

            )

        )

        logger.info(

            "==================================="
        )
