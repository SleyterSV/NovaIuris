import json
import logging
from typing import Dict
from typing import List

from openai import OpenAI

from app.config import Config


logger = logging.getLogger(
    "NovaIuris.StrategyBuilder"
)


class StrategyBuilder:
    """
    ==========================================================

                NOVA STRATEGY BUILDER

    Construye la estrategia jurídica del caso.

    Este servicio NO responde preguntas.

    Su función es transformar el análisis
    realizado por CaseAnalyzer en una
    estrategia jurídica estructurada.

    Genera:

        • Estrategia del demandante

        • Estrategia del demandado

        • Fortalezas

        • Debilidades

        • Riesgos

        • Medios probatorios

        • Consultas sugeridas para NovaSearch

        • Acciones recomendadas

    Será utilizado por:

        • NovaCase

        • NovaCourt

    ==========================================================
    """

    MODEL = "gpt-5"

    def __init__(self):

        self.client = OpenAI(
            max_retries=0,

            api_key=Config.OPENAI_API_KEY

        )

        logger.info(

            "Strategy Builder iniciado."

        )

    ####################################################################
    ###################### CONSTRUIR ESTRATEGIA #########################
    ####################################################################

    def build_strategy(
        self,
        analysis: Dict
    ) -> Dict:

        """
        Construye la estrategia jurídica a partir
        del análisis realizado por CaseAnalyzer.
        """

        logger.info(
            "Construyendo estrategia jurídica..."
        )

        prompt = self._build_prompt(
            analysis
        )

        response = self.client.chat.completions.create(

            model=self.MODEL,

            messages=[

                {
                    "role": "system",
                    "content": (
                        "Eres un abogado litigante peruano con amplia "
                        "experiencia en litigación estratégica. "
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

        strategy = self._safe_parse_json(
            content
        )

        if not self.validate_strategy(
            strategy
        ):

            logger.warning(
                "La estrategia generada no pasó la validación."
            )

        logger.info(
            "Estrategia jurídica construida correctamente."
        )

        return strategy

    ####################################################################
    ######################## PROMPT PRINCIPAL ###########################
    ####################################################################

    @staticmethod
    def _build_prompt(
        analysis: Dict
    ) -> str:

        analysis_json = json.dumps(

            analysis,

            indent=4,

            ensure_ascii=False

        )

        return f"""
Eres un abogado litigante peruano con más de 25 años de experiencia.

Especialista en:

• Derecho Constitucional

• Derecho Civil

• Derecho Penal

• Derecho Laboral

• Derecho Administrativo

• Litigación Estratégica

Tu función NO es responder preguntas.

Tu trabajo consiste en construir la MEJOR estrategia jurídica posible utilizando únicamente el análisis del caso recibido.

NO inventes hechos.

NO agregues información inexistente.

NO cites normas inexistentes.

NO cites jurisprudencia inexistente.

Analiza objetivamente el caso.

========================================================

Debes construir:

1. Estrategia del demandante.

2. Posible estrategia del demandado.

3. Fortalezas del caso.

4. Debilidades del caso.

5. Riesgos procesales.

6. Medios probatorios recomendados.

7. Documentos que deberían obtenerse.

8. Consultas recomendadas para NovaSearch.

9. Acciones jurídicas recomendadas.

10. Información que aún falta recopilar.

========================================================

Devuelve EXCLUSIVAMENTE este JSON.

{{
    "claim_strategy": "",

    "defense_strategy": "",

    "strengths": [],

    "weaknesses": [],

    "procedural_risks": [],

    "recommended_evidence": [],

    "recommended_documents": [],

    "search_queries": [],

    "recommended_actions": [],

    "missing_information": []

}}

========================================================

ANÁLISIS DEL CASO

{analysis_json}

========================================================

Las consultas para NovaSearch deben ser extremadamente específicas.

Ejemplos:

- "Despido nulo libertad de expresión Tribunal Constitucional"

- "Artículo 29 LPCL"

- "Casación despido por pérdida de confianza"

- "Reposición trabajador precedente vinculante"

- "Convenio 158 OIT despido"

========================================================

Devuelve únicamente el objeto JSON.

No utilices Markdown.

No agregues explicaciones.

No agregues comentarios.

Solo devuelve el JSON.
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

        Si el modelo devuelve texto adicional,
        Markdown o un JSON mal encapsulado,
        intenta recuperarlo automáticamente.
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
        # Eliminar bloques Markdown
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
        # Buscar primer { y último }
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

                f"No fue posible interpretar la estrategia: {error}"

            )

            logger.debug("Model response omitted from logs")

            return {

                "claim_strategy": "",

                "defense_strategy": "",

                "strengths": [],

                "weaknesses": [],

                "procedural_risks": [],

                "recommended_evidence": [],

                "recommended_documents": [],

                "search_queries": [],

                "recommended_actions": [],

                "missing_information": []

            }

    ####################################################################
    ###################### VALIDAR ESTRATEGIA ###########################
    ####################################################################

    @staticmethod
    def validate_strategy(
        strategy: Dict
    ) -> bool:

        """
        Verifica que la estrategia tenga
        la estructura mínima esperada.
        """

        required_fields = [

            "claim_strategy",

            "defense_strategy",

            "strengths",

            "weaknesses",

            "procedural_risks",

            "recommended_evidence",

            "recommended_documents",

            "search_queries",

            "recommended_actions",

            "missing_information"

        ]

        for field in required_fields:

            if field not in strategy:

                logger.warning(

                    f"Campo faltante: {field}"

                )

                return False

        return True

    ####################################################################
    ###################### RESUMEN EJECUTIVO ############################
    ####################################################################

    @staticmethod
    def summary(
        strategy: Dict
    ) -> Dict:

        """
        Devuelve un resumen ejecutivo de la estrategia.

        Será utilizado por NovaCase Dashboard.
        """

        return {

            "strengths":

                len(

                    strategy.get(

                        "strengths",

                        []

                    )

                ),

            "weaknesses":

                len(

                    strategy.get(

                        "weaknesses",

                        []

                    )

                ),

            "procedural_risks":

                len(

                    strategy.get(

                        "procedural_risks",

                        []

                    )

                ),

            "recommended_evidence":

                len(

                    strategy.get(

                        "recommended_evidence",

                        []

                    )

                ),

            "recommended_documents":

                len(

                    strategy.get(

                        "recommended_documents",

                        []

                    )

                ),

            "search_queries":

                len(

                    strategy.get(

                        "search_queries",

                        []

                    )

                ),

            "recommended_actions":

                len(

                    strategy.get(

                        "recommended_actions",

                        []

                    )

                )

        }

    ####################################################################
    ###################### ESTADISTICAS ################################
    ####################################################################

    @staticmethod
    def statistics(
        strategy: Dict
    ) -> Dict:

        """
        Genera estadísticas del plan estratégico.

        Estas métricas servirán para el Dashboard
        y para futuras métricas del caso.
        """

        score = 100

        score -= len(

            strategy.get(

                "weaknesses",

                []

            )

        ) * 5

        score -= len(

            strategy.get(

                "procedural_risks",

                []

            )

        ) * 8

        score += len(

            strategy.get(

                "strengths",

                []

            )

        ) * 3

        score = max(
            0,
            min(
                score,
                100
            )
        )

        return {

            "estimated_case_score": score,

            "strengths":

                len(

                    strategy.get(

                        "strengths",

                        []

                    )

                ),

            "weaknesses":

                len(

                    strategy.get(

                        "weaknesses",

                        []

                    )

                ),

            "procedural_risks":

                len(

                    strategy.get(

                        "procedural_risks",

                        []

                    )

                ),

            "recommended_actions":

                len(

                    strategy.get(

                        "recommended_actions",

                        []

                    )

                )

        }

    ####################################################################
    ###################### DEBUG #######################################
    ####################################################################

    @staticmethod
    def print_debug(
        strategy: Dict
    ) -> None:

        """
        Imprime la estrategia generada.

        Solo para desarrollo.
        """

        logger.info(

            "========== CASE STRATEGY =========="

        )

        logger.info(

            json.dumps(

                strategy,

                indent=4,

                ensure_ascii=False

            )

        )

        logger.info(

            "==================================="

        )