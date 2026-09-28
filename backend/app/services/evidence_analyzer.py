import json
import logging
from typing import Dict
from typing import List

from openai import OpenAI

from app.config import Config


logger = logging.getLogger(
    "NovaIuris.EvidenceAnalyzer"
)


class EvidenceAnalyzer:
    """
    ==========================================================

                NOVA EVIDENCE ANALYZER

    Evalúa toda la evidencia disponible del caso.

    Analiza:

        • Pruebas existentes

        • Pruebas faltantes

        • Valor probatorio

        • Riesgos probatorios

        • Medios de prueba recomendados

        • Documentos por obtener

        • Pruebas impugnables

        • Suficiencia probatoria

    NO analiza el caso.

    NO genera argumentos.

    NO busca jurisprudencia.

    Su única responsabilidad es evaluar
    la fortaleza de la evidencia disponible.

    Será utilizado por:

        • NovaCase

        • NovaCourt

        • Tribunal Multiagente

    ==========================================================
    """

    MODEL = "gpt-5"

    def __init__(self):

        self.client = OpenAI(
            max_retries=0,

            api_key=Config.OPENAI_API_KEY

        )

        logger.info(

            "Evidence Analyzer iniciado."

        )

    ####################################################################
    ###################### ANALIZAR EVIDENCIA ###########################
    ####################################################################

    def analyze(
        self,
        analysis: Dict,
        strategy: Dict,
        arguments: Dict,
        documents: List[Dict]
    ) -> Dict:

        """
        Evalúa la evidencia disponible del caso.

        Analiza:

            • Pruebas existentes

            • Pruebas faltantes

            • Valor probatorio

            • Riesgos probatorios

            • Documentos recomendados

            • Medios de prueba sugeridos

        Devuelve un análisis estructurado.
        """

        logger.info(

            "Analizando evidencia del caso..."

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

                    "content":

                        "Eres un abogado litigante peruano "

                        "especialista en valoración probatoria. "

                        "Debes devolver únicamente un JSON válido."

                },

                {

                    "role": "user",

                    "content": prompt

                }

            ]

        )

        content = response.choices[0].message.content

        evidence = self._safe_parse_json(

            content

        )

        if not self.validate_evidence(

            evidence

        ):

            logger.warning(

                "La evaluación de evidencia no pasó la validación."

            )

        logger.info(

            "Evaluación probatoria completada."

        )

        return evidence

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
Eres un abogado litigante peruano especializado en Derecho Probatorio y valoración de la prueba.

Has trabajado durante más de 30 años en procesos judiciales civiles, laborales, penales, constitucionales y administrativos.

========================================================

Tu única función consiste en evaluar la evidencia del caso.

NO analices nuevamente el caso.

NO modifiques la estrategia.

NO inventes documentos.

NO inventes pruebas.

NO inventes hechos.

NO inventes jurisprudencia.

Debes evaluar únicamente la información proporcionada.

========================================================

Analiza:

1. Evidencia actualmente disponible.

2. Evidencia documental.

3. Evidencia testimonial.

4. Evidencia pericial.

5. Evidencia digital.

6. Evidencia material.

7. Evidencia faltante.

8. Documentos que deberían conseguirse.

9. Medios probatorios recomendados.

10. Riesgos probatorios.

11. Fortalezas probatorias.

12. Debilidades probatorias.

13. Qué acredita y qué no acredita cada fragmento identificado.

14. Recomendaciones antes del proceso.

========================================================

Devuelve EXCLUSIVAMENTE este JSON.

{{
    "available_evidence": [],

    "documentary_evidence": [],

    "testimonial_evidence": [],

    "expert_evidence": [],

    "digital_evidence": [],

    "physical_evidence": [],

    "missing_evidence": [],

    "recommended_documents": [],

    "recommended_evidence": [],

    "evidentiary_risks": [],

    "strengths": [],

    "weaknesses": [],

    "evidence_strength": "",

    "evidence_links": [
        {{"fact_ids":[], "issue_id":null, "source_ids":[],
          "what_it_supports":"", "limitations":""}}
    ],

    "recommendations": []

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

DOCUMENTOS RECUPERADOS Y FRAGMENTOS DEL EXPEDIENTE

{documents_json}

En evidence_links relaciona únicamente evidencia existente con fact_id,
issue_id y source_ids recibidos. Para cada relación indica what_it_supports
y limitations. Si no hay fuente documental verificable, deja el vínculo vacío.
No conviertas medios probatorios recomendados en prueba disponible.

========================================================

IMPORTANTE

Evalúa objetivamente si las pruebas son suficientes para sostener la estrategia jurídica.

Si detectas ausencia de pruebas esenciales, indícalo expresamente.

Si existen medios probatorios más adecuados, recomiéndalos.

Clasifica la fortaleza probatoria como:

• MUY ALTA

• ALTA

• MEDIA

• BAJA

• MUY BAJA

La clasificación es cualitativa y debe derivarse de la procedencia,
integridad, corroboración y relación de la evidencia disponible con los
hechos relevantes. Si esos criterios no pueden evaluarse, usa DESCONOCIDA.
No la presentes como probabilidad de acreditar hechos.

========================================================

Devuelve únicamente el objeto JSON.

No escribas explicaciones.

No utilices Markdown.

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
        o un JSON mal encapsulado, intenta recuperarlo.
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

                f"No fue posible interpretar el análisis probatorio: {error}"

            )

            logger.debug("Model response omitted from logs")

            return {

                "available_evidence": [],

                "documentary_evidence": [],

                "testimonial_evidence": [],

                "expert_evidence": [],

                "digital_evidence": [],

                "physical_evidence": [],

                "missing_evidence": [],

                "recommended_documents": [],

                "recommended_evidence": [],

                "evidentiary_risks": [],

                "strengths": [],

                "weaknesses": [],

                "evidence_strength": "DESCONOCIDA",

                "evidence_links": [],

                "recommendations": []

            }

    ####################################################################
    ###################### VALIDAR EVIDENCIA ############################
    ####################################################################

    @staticmethod
    def validate_evidence(evidence: Dict) -> bool:
        if not isinstance(evidence, dict):
            return False
        required = ("available_evidence", "documentary_evidence",
                    "missing_evidence", "evidence_strength")
        return all(key in evidence for key in required) and isinstance(
            evidence.get("evidence_links", []), list)

    @staticmethod
    def summary(
        evidence: Dict
    ) -> Dict:

        """
        Devuelve un resumen ejecutivo del
        análisis probatorio.
        """

        return {

            "available_evidence":

                len(

                    evidence.get(

                        "available_evidence",

                        []

                    )

                ),

            "missing_evidence":

                len(

                    evidence.get(

                        "missing_evidence",

                        []

                    )

                ),

            "recommended_documents":

                len(

                    evidence.get(

                        "recommended_documents",

                        []

                    )

                ),

            "evidence_strength":

                evidence.get(

                    "evidence_strength",

                    "DESCONOCIDA"

                ),

        }

    ####################################################################
    ######################## ESTADISTICAS ###############################
    ####################################################################

    @staticmethod
    def statistics(
        evidence: Dict
    ) -> Dict:

        """
        Devuelve estadísticas generales
        del análisis probatorio.
        """

        return {

            "documentary_evidence":

                len(

                    evidence.get(

                        "documentary_evidence",

                        []

                    )

                ),

            "testimonial_evidence":

                len(

                    evidence.get(

                        "testimonial_evidence",

                        []

                    )

                ),

            "expert_evidence":

                len(

                    evidence.get(

                        "expert_evidence",

                        []

                    )

                ),

            "digital_evidence":

                len(

                    evidence.get(

                        "digital_evidence",

                        []

                    )

                ),

            "physical_evidence":

                len(

                    evidence.get(

                        "physical_evidence",

                        []

                    )

                ),

            "evidentiary_risks":

                len(

                    evidence.get(

                        "evidentiary_risks",

                        []

                    )

                ),

            "recommendations":

                len(

                    evidence.get(

                        "recommendations",

                        []

                    )

                )

        }


    ####################################################################
    ######################## DEBUG ######################################
    ####################################################################

    @staticmethod
    def print_debug(
        evidence: Dict
    ) -> None:

        """
        Imprime el análisis probatorio.

        Solo para desarrollo.
        """

        logger.info(

            "======= EVIDENCE ANALYSIS ======="

        )

        logger.info(

            json.dumps(

                evidence,

                indent=4,

                ensure_ascii=False

            )

        )

        logger.info(

            "================================="
        )
