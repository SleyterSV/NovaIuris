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
            max_retries=0,

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
        research: Dict,
        sources=None,
        facts=None,
        issues=None,
        timeline=None,
        final_strategy=None,
        case_id=None,
        document_profile="analysis_report",
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

            research=research,
            sources=sources,
            facts=facts,
            issues=issues,
            timeline=timeline,
            final_strategy=final_strategy,
            case_id=case_id,
            document_profile=document_profile,

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
        research: Dict,
        sources=None,
        facts=None,
        issues=None,
        timeline=None,
        final_strategy=None,
        case_id=None,
        document_profile="analysis_report",
    ) -> str:
        """Give the model one compact, traceable case snapshot."""
        if document_profile != "analysis_report":
            raise ValueError("Unsupported document profile")
        analysis_context = {key: value for key, value in analysis.items()
                            if key not in {"hechos", "hechos_estructurados", "fact_records",
                                           "problemas_juridicos", "issue_records", "normas_probables"}}
        source_context = [{key: source.get(key) for key in
                           ("source_id", "source_scope", "source_type", "title", "article",
                            "legal_basis", "court", "case_number", "document_id", "chunk_id",
                            "page_start", "page_end", "section", "excerpt")}
                          for source in (sources or [])]
        context = {
            "case_id": case_id,
            "user_statement": str(case_text or "")[:8000],
            "analysis": analysis_context,
            "facts": facts or [],
            "issues": issues or [],
            "timeline": timeline or [],
            "initial_strategy": {key: value for key, value in strategy.items()
                                 if key != "search_queries"},
            "final_strategy": final_strategy or {},
            "arguments": legal_arguments,
            "evidence": evidence_analysis,
            "risks": risk_analysis,
            "counter_arguments": counter_arguments,
            "research_status": research.get("status"),
            "verified_sources": source_context,
        }
        payload = json.dumps(context, ensure_ascii=False, separators=(",", ":"), default=str)
        return (
            "Redacta un INFORME JURÍDICO DE ANÁLISIS DEL CASO para revisión por un abogado. "
            "Usa tono formal, preciso y sobrio; emplea terminología peruana cuando corresponda. "
            "No escribas como tribunal ni como autoridad pública.\n\n"
            "Estructura adaptable en Markdown: título y secciones de objeto y alcance; "
            "antecedentes y hechos; cuestiones jurídicas; marco normativo y jurisprudencial; "
            "análisis jurídico por cuestión; análisis probatorio; argumentos; contraargumentos; "
            "riesgos; estrategia y actuaciones; conclusiones; fuentes. "
            "Omite secciones sin contenido real. Redacta párrafos desarrollados y conclusiones "
            "que respondan a las cuestiones; usa listas solo cuando aclaren pruebas, acciones o conclusiones.\n\n"
            "El relato del usuario contiene alegaciones. Una fuente documental puede acreditar "
            "que una afirmación consta en un documento sin probar por sí sola su veracidad. "
            "Separa ambos planos. No inventes hechos, pruebas, fechas, normas, jurisprudencia, "
            "tribunales, artículos, fundamentos, URLs ni probabilidades. "
            "Las normas preliminares del análisis no son autoridades verificadas.\n\n"
            "Para toda afirmación jurídica externa o hecho documental relevante respaldado, "
            "cita únicamente los identificadores exactos mostrados en verified_sources, "
            "por ejemplo [SRC-ABC123]. No dupliques el prefijo ni alteres el identificador. "
            "No uses [1] ni otros números de cita: el sistema los asignará tras validar. "
            "No cites una fuente si su fragmento no respalda esa afirmación. "
            "Si la investigación falló o no hay fuentes verificadas, dilo con precisión y "
            "no atribuyas autoridad a información no recuperada. "
            "La sección Fuentes debe mencionar solo las fuentes citadas, sin inventar datos.\n\n"
            f"DATOS DEL CASO:\n{payload}\n\nEntrega únicamente el informe Markdown."
        )

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
    def validate_report(report: str) -> bool:
        """Accept an adaptive report with substantive analysis and conclusions."""
        if not isinstance(report, str) or len(report.strip()) < 120:
            return False
        headings = [line[3:].strip().lower() for line in report.splitlines()
                    if line.startswith("## ")]
        return (len(headings) >= 3
                and any("análisis" in heading or "analisis" in heading for heading in headings)
                and any("conclus" in heading for heading in headings))

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
