import json
import logging
from typing import Dict, List

from openai import OpenAI

from app.config import Config


logger = logging.getLogger(
    "NovaIuris.CaseReportService"
)


class CaseReportService:
    """
    ==========================================================

                NOVA CASE REPORT SERVICE

    Construye el informe jurídico final.

    Reúne toda la información generada por:

        • CaseAnalyzer

        • StrategyBuilder

        • NovaSearch

        • LegalArgumentService

        • EvidenceAnalyzer

        • RiskAnalyzer

        • CounterArgumentService

    Su única responsabilidad consiste
    en redactar un informe jurídico
    profesional listo para ser utilizado.

    El informe incluye:

        • Resumen Ejecutivo

        • Hechos

        • Problemas Jurídicos

        • Estrategia

        • Normas

        • Jurisprudencia

        • Argumentos

        • Evidencia

        • Riesgos

        • Contraargumentos

        • Recomendaciones

        • Conclusión

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

            "Case Report Service iniciado."

        )

    ####################################################################
    ###################### GENERAR INFORME ##############################
    ####################################################################

    def generate_report(
        self,
        case_text: str,
        analysis: Dict,
        strategy: Dict,
        legal_arguments: Dict,
        evidence_analysis: Dict,
        risk_analysis: Dict,
        counter_arguments: Dict,
        research: Dict
    ) -> str:

        """
        Genera el informe jurídico completo.

        Recibe toda la información producida
        por NovaCase.

        Devuelve un informe profesional
        en formato Markdown.
        """

        logger.info(

            "Generando informe jurídico..."

        )

        prompt = self._build_prompt(

            case_text=case_text,

            analysis=analysis,

            strategy=strategy,

            legal_arguments=legal_arguments,

            evidence_analysis=evidence_analysis,

            risk_analysis=risk_analysis,

            counter_arguments=counter_arguments,

            research=research

        )

        response = self.client.chat.completions.create(

            model=self.MODEL,

            messages=[

                {

                    "role":"system",

                    "content":

                        "Eres un abogado litigante peruano "

                        "especialista en redacción de informes "

                        "jurídicos profesionales."

                },

                {

                    "role":"user",

                    "content":prompt

                }

            ]

        )

        report = (

            response

            .choices[0]

            .message

            .content

        )

        report = self.clean_report(report)

        if not self.validate_report(report):

            logger.warning(

                "El informe generado no contiene todas las secciones esperadas."

            )

        logger.info(

            "Informe jurídico generado."

        )

        return report

    ####################################################################
    ######################## PROMPT PRINCIPAL ###########################
    ####################################################################

    @staticmethod
    def _build_prompt(
        case_text: str,
        analysis: Dict,
        strategy: Dict,
        legal_arguments: Dict,
        evidence_analysis: Dict,
        risk_analysis: Dict,
        counter_arguments: Dict,
        research: Dict
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
            legal_arguments,
            indent=4,
            ensure_ascii=False
        )

        evidence_json = json.dumps(
            evidence_analysis,
            indent=4,
            ensure_ascii=False
        )

        risk_json = json.dumps(
            risk_analysis,
            indent=4,
            ensure_ascii=False
        )

        counter_json = json.dumps(
            counter_arguments,
            indent=4,
            ensure_ascii=False
        )

        research_json = json.dumps(
            research,
            indent=2,
            ensure_ascii=False
        )

        return f"""
Eres un abogado litigante peruano senior con más de 35 años de experiencia.

Has participado en procesos:

• Constitucionales

• Civiles

• Penales

• Laborales

• Administrativos

• Tributarios

• Comerciales

Tu trabajo consiste en redactar un INFORME JURÍDICO PROFESIONAL.

NO inventes normas.

NO inventes jurisprudencia.

NO inventes hechos.

NO inventes pruebas.

Utiliza únicamente la información proporcionada.

El informe debe ser claro, técnico, objetivo y apto para ser revisado por otro abogado.

==============================================================

El informe debe contener exactamente las siguientes secciones:

# INFORME JURÍDICO

## I. Resumen Ejecutivo

Realiza un resumen profesional del caso.

--------------------------------------------------------------

## II. Hechos Relevantes

Resume cronológicamente los hechos relevantes.

--------------------------------------------------------------

## III. Problemas Jurídicos

Identifica los principales problemas jurídicos del caso.

--------------------------------------------------------------

## IV. Normativa Aplicable

Explica las normas aplicables encontradas por NovaSearch.

--------------------------------------------------------------

## V. Jurisprudencia Relevante

Resume la jurisprudencia más importante encontrada.

--------------------------------------------------------------

## VI. Estrategia Jurídica Recomendada

Explica por qué la estrategia propuesta es adecuada.

--------------------------------------------------------------

## VII. Argumentos Jurídicos Principales

Desarrolla los argumentos más sólidos.

--------------------------------------------------------------

## VIII. Evaluación Probatoria

Describe las pruebas disponibles.

Explica las pruebas faltantes.

Explica qué pruebas deberían conseguirse.

--------------------------------------------------------------

## IX. Evaluación de Riesgos

Describe:

• Riesgos procesales

• Riesgos jurídicos

• Riesgos probatorios

Incluye una valoración de la probabilidad estimada de éxito.

--------------------------------------------------------------

## X. Posibles Argumentos de la Contraparte

Resume los argumentos que probablemente utilizará la contraparte.

Explica cómo responder a ellos.

--------------------------------------------------------------

## XI. Recomendaciones

Indica acciones concretas antes de iniciar el proceso.

--------------------------------------------------------------

## XII. Conclusión

Concluye indicando:

• Fortalezas.

• Debilidades.

• Viabilidad del caso.

• Recomendación final.

==============================================================

CASO ORIGINAL

{case_text}

==============================================================

ANÁLISIS DEL CASO

{analysis_json}

==============================================================

ESTRATEGIA

{strategy_json}

==============================================================

ARGUMENTOS JURÍDICOS

{arguments_json}

==============================================================

ANÁLISIS PROBATORIO

{evidence_json}

==============================================================

ANÁLISIS DE RIESGOS

{risk_json}

==============================================================

CONTRAARGUMENTOS

{counter_json}

==============================================================

INVESTIGACIÓN JURÍDICA (NOVASEARCH)

{research_json}

==============================================================

IMPORTANTE

El informe debe parecer elaborado por un abogado experto.

Debe ser técnico.

Debe ser ordenado.

Debe ser objetivo.

Debe ser claro.

No utilices tablas.

No utilices Markdown adicional distinto a los encabezados.

No inventes información.

No omitas ninguna sección.

Entrega únicamente el informe.
"""

    ####################################################################
    ###################### LIMPIAR INFORME ##############################
    ####################################################################

    @staticmethod
    def clean_report(
        report: str
    ) -> str:

        """
        Limpia el informe generado por el LLM.

        Elimina:

            • Markdown innecesario

            • Bloques ```markdown

            • Espacios duplicados

            • Saltos excesivos

        Devuelve un informe listo
        para mostrarse en NovaCase.
        """

        if not report:

            return ""

        report = (

            report

            .replace(

                "```markdown",

                ""

            )

            .replace(

                "```md",

                ""

            )

            .replace(

                "```",

                ""

            )

            .strip()

        )

        while "\n\n\n" in report:

            report = report.replace(

                "\n\n\n",

                "\n\n"

            )

        return report

    ####################################################################
    ###################### VALIDAR INFORME ##############################
    ####################################################################

    @staticmethod
    def validate_report(
        report: str
    ) -> bool:

        """
        Verifica que el informe tenga
        las secciones mínimas esperadas.
        """

        if not report:

            return False

        required_sections = [

            "Resumen Ejecutivo",

            "Hechos",

            "Problemas Jurídicos",

            "Normativa",

            "Jurisprudencia",

            "Estrategia",

            "Argumentos",

            "Evaluación Probatoria",

            "Evaluación de Riesgos",

            "Contraparte",

            "Recomendaciones",

            "Conclusión"

        ]

        report_lower = report.lower()

        encontrados = 0

        for section in required_sections:

            if section.lower() in report_lower:

                encontrados += 1

        logger.info(

            f"Secciones detectadas: {encontrados}/{len(required_sections)}"

        )

        return encontrados >= 10

    ####################################################################
    ###################### RESUMEN DEL INFORME ##########################
    ####################################################################

    @staticmethod
    def summary(
        report: str
    ) -> Dict:

        """
        Genera un resumen estadístico
        del informe jurídico.
        """

        if not report:

            return {

                "characters": 0,

                "words": 0,

                "sections": 0

            }

        words = report.split()

        sections = report.count("##")

        return {

            "characters": len(report),

            "words": len(words),

            "sections": sections

        }

    ####################################################################
    ###################### EXTRAER SECCIONES ############################
    ####################################################################

    @staticmethod
    def extract_sections(
        report: str
    ) -> Dict:

        """
        Extrae las principales secciones
        del informe para mostrarlas
        individualmente en el frontend.
        """

        section_titles = [

            "Resumen Ejecutivo",

            "Hechos Relevantes",

            "Problemas Jurídicos",

            "Normativa Aplicable",

            "Jurisprudencia Relevante",

            "Estrategia Jurídica Recomendada",

            "Argumentos Jurídicos Principales",

            "Evaluación Probatoria",

            "Evaluación de Riesgos",

            "Posibles Argumentos de la Contraparte",

            "Recomendaciones",

            "Conclusión"

        ]

        sections = {}

        current_section = "Introducción"

        buffer = []

        for line in report.splitlines():

            line_strip = line.strip()

            found = False

            for title in section_titles:

                if title.lower() in line_strip.lower():

                    sections[current_section] = "\n".join(buffer).strip()

                    current_section = title

                    buffer = []

                    found = True

                    break

            if not found:

                buffer.append(line)

        sections[current_section] = "\n".join(buffer).strip()

        return sections

    ####################################################################
    ###################### ÍNDICE DEL INFORME ###########################
    ####################################################################

    @staticmethod
    def generate_table_of_contents() -> List[str]:

        """
        Devuelve el índice estándar del
        informe jurídico.
        """

        return [

            "I. Resumen Ejecutivo",

            "II. Hechos Relevantes",

            "III. Problemas Jurídicos",

            "IV. Normativa Aplicable",

            "V. Jurisprudencia Relevante",

            "VI. Estrategia Jurídica Recomendada",

            "VII. Argumentos Jurídicos Principales",

            "VIII. Evaluación Probatoria",

            "IX. Evaluación de Riesgos",

            "X. Posibles Argumentos de la Contraparte",

            "XI. Recomendaciones",

            "XII. Conclusión"

        ]

    ####################################################################
    ###################### ESTADÍSTICAS ################################
    ####################################################################

    @staticmethod
    def statistics(
        report: str
    ) -> Dict:

        """
        Devuelve estadísticas generales
        del informe.
        """

        return {

            "characters": len(report),

            "words": len(report.split()),

            "paragraphs": len(

                [

                    p for p in report.split("\n\n")

                    if p.strip()

                ]

            ),

            "sections": report.count("##")

        }

    ####################################################################
    ######################## DEBUG #####################################
    ####################################################################

    @staticmethod
    def print_debug(
        report: str
    ) -> None:

        """
        Imprime el informe completo.

        Solo para desarrollo.
        """

        logger.info(

            "========== CASE REPORT =========="

        )

        logger.info(

            report

        )

        logger.info(

            "================================="
        )