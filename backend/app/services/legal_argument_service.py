import json
import logging
from typing import Dict
from typing import List

from openai import OpenAI

from app.config import Config


logger = logging.getLogger(
    "NovaIuris.LegalArgumentService"
)


class LegalArgumentService:
    """
    ==========================================================

            NOVA LEGAL ARGUMENT SERVICE

    Construye los argumentos jurídicos que serán
    utilizados durante la defensa del caso.

    NO analiza el caso.

    NO busca documentos.

    NO genera estrategias.

    Su única función consiste en transformar
    el análisis, la estrategia y la investigación
    jurídica en argumentos jurídicos sólidos.

    Genera:

        • Argumentos principales

        • Argumentos secundarios

        • Argumentos constitucionales

        • Argumentos procesales

        • Argumentos normativos

        • Posibles contraargumentos

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

            "Legal Argument Service iniciado."

        )

    ####################################################################
    ###################### GENERAR ARGUMENTOS ###########################
    ####################################################################

    def generate_arguments(
        self,
        analysis: Dict,
        strategy: Dict,
        documents: List[Dict]
    ) -> Dict:

        """
        Construye los argumentos jurídicos del caso.

        Utiliza:

            • Análisis del caso

            • Estrategia jurídica

            • Documentos recuperados por NovaSearch

        Devuelve una estructura organizada que será
        utilizada posteriormente por NovaCase y NovaCourt.
        """

        logger.info(

            "Generando argumentos jurídicos..."

        )

        prompt = self._build_prompt(

            analysis=analysis,

            strategy=strategy,

            documents=documents

        )

        response = self.client.chat.completions.create(

            model=self.MODEL,

            messages=[

                {
                    "role": "system",
                    "content": (
                        "Eres un abogado litigante peruano experto en "
                        "argumentación jurídica. "
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

        arguments = self._safe_parse_json(

            content

        )

        if not self.validate_arguments(

            arguments

        ):

            logger.warning(

                "Los argumentos generados no pasaron la validación."

            )

        logger.info(

            "Argumentos jurídicos generados correctamente."

        )

        return arguments

    ####################################################################
    ######################## PROMPT PRINCIPAL ###########################
    ####################################################################

    @staticmethod
    def _build_prompt(
        analysis: Dict,
        strategy: Dict,
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

        documents_json = json.dumps(

            documents,

            indent=2,

            ensure_ascii=False

        )

        return f"""
Eres un abogado litigante peruano con más de 30 años de experiencia.

Especialista en:

• Derecho Constitucional

• Derecho Civil

• Derecho Penal

• Derecho Laboral

• Derecho Administrativo

• Derecho Procesal

• Litigación Estratégica

========================================================

Tu única función consiste en construir los mejores argumentos jurídicos posibles.

NO inventes hechos.

NO inventes jurisprudencia.

NO inventes normas.

NO inventes artículos.

NO inventes precedentes.

Utiliza EXCLUSIVAMENTE la información recibida.

Los argumentos deben ser:

• Técnicamente correctos.

• Coherentes.

• Ordenados.

• Persuasivos.

• Propios de un escrito judicial.

========================================================

Construye:

1. Argumentos principales.

2. Argumentos secundarios.

3. Argumentos constitucionales.

4. Argumentos procesales.

5. Argumentos normativos.

6. Jurisprudencia relevante utilizada.

7. Posibles contraargumentos.

8. Respuesta frente a esos contraargumentos.

9. Riesgos de cada argumento.

10. Valoración cualitativa de cada argumento, solo si los datos la sustentan.
    Si no puede fundamentarse, indícala como "No determinada".

========================================================

Devuelve EXCLUSIVAMENTE este JSON.

{{
    "main_arguments":[
        {{
            "title":"",
            "argument":"",
            "issue_id":null,
            "supporting_fact_ids":[],
            "source_ids":[],
            "legal_basis":[],
            "jurisprudence":[],
            "strength":"No determinada",
            "risk":"Bajo"
        }}
    ],

    "secondary_arguments":[],

    "constitutional_arguments":[],

    "procedural_arguments":[],

    "normative_arguments":[],

    "jurisprudence_used":[],

    "possible_counterarguments":[],

    "counterargument_responses":[],

    "general_observations":[]

}}

========================================================

ANÁLISIS DEL CASO

{analysis_json}

========================================================

ESTRATEGIA

{strategy_json}

========================================================

DOCUMENTOS RECUPERADOS Y FRAGMENTOS DEL EXPEDIENTE

{documents_json}

Usa issue_id de los problemas jurídicos recibidos, supporting_fact_ids de los
hechos estructurados recibidos y source_ids solo de las
fuentes verificadas incluidas en los documentos. Las normas_probables del
análisis inicial son hipótesis, no autoridad recuperada. Si una fuente no
existe, no la cites ni atribuyas una regla jurídica a ella.

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

                f"No fue posible interpretar los argumentos: {error}"

            )

            logger.debug("Model response omitted from logs")

            return {

                "main_arguments": [],

                "secondary_arguments": [],

                "constitutional_arguments": [],

                "procedural_arguments": [],

                "normative_arguments": [],

                "jurisprudence_used": [],

                "possible_counterarguments": [],

                "counterargument_responses": [],

                "general_observations": []

            }

    ####################################################################
    ###################### VALIDAR ARGUMENTOS ###########################
    ####################################################################

    @staticmethod
    def validate_arguments(
        arguments: Dict
    ) -> bool:

        """
        Verifica que la estructura generada
        tenga todos los campos necesarios.
        """

        required_fields = [

            "main_arguments",

            "secondary_arguments",

            "constitutional_arguments",

            "procedural_arguments",

            "normative_arguments",

            "jurisprudence_used",

            "possible_counterarguments",

            "counterargument_responses",

            "general_observations"

        ]

        for field in required_fields:

            if field not in arguments:

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
        arguments: Dict
    ) -> Dict:

        """
        Devuelve un resumen ejecutivo de los
        argumentos jurídicos generados.
        """

        return {

            "main_arguments":

                len(

                    arguments.get(

                        "main_arguments",

                        []

                    )

                ),

            "secondary_arguments":

                len(

                    arguments.get(

                        "secondary_arguments",

                        []

                    )

                ),

            "constitutional_arguments":

                len(

                    arguments.get(

                        "constitutional_arguments",

                        []

                    )

                ),

            "procedural_arguments":

                len(

                    arguments.get(

                        "procedural_arguments",

                        []

                    )

                ),

            "normative_arguments":

                len(

                    arguments.get(

                        "normative_arguments",

                        []

                    )

                ),

            "counterarguments":

                len(

                    arguments.get(

                        "possible_counterarguments",

                        []

                    )

                )

        }

    ####################################################################
    ###################### ESTADISTICAS ################################
    ####################################################################

    @staticmethod
    def statistics(
        arguments: Dict
    ) -> Dict:

        """
        Genera estadísticas generales de la
        argumentación jurídica.
        """

        total = (

            len(arguments.get("main_arguments", []))

            +

            len(arguments.get("secondary_arguments", []))

            +

            len(arguments.get("constitutional_arguments", []))

            +

            len(arguments.get("procedural_arguments", []))

            +

            len(arguments.get("normative_arguments", []))

        )

        return {

            "total_arguments": total,

            "jurisprudence_used":

                len(

                    arguments.get(

                        "jurisprudence_used",

                        []

                    )

                ),

            "counterarguments":

                len(

                    arguments.get(

                        "possible_counterarguments",

                        []

                    )

                ),

            "responses":

                len(

                    arguments.get(

                        "counterargument_responses",

                        []

                    )

                ),

            "observations":

                len(

                    arguments.get(

                        "general_observations",

                        []

                    )

                )

        }

    ####################################################################
    ################ EXTRAER ARGUMENTOS PRINCIPALES #####################
    ####################################################################

    @staticmethod
    def extract_main_arguments(
        arguments: Dict
    ) -> List[Dict]:

        """
        Devuelve únicamente los argumentos
        principales del caso.
        """

        return arguments.get(

            "main_arguments",

            []

        )

    ####################################################################
    ###################### DEBUG #######################################
    ####################################################################

    @staticmethod
    def print_debug(
        arguments: Dict
    ) -> None:

        """
        Imprime los argumentos generados.

        Solo para desarrollo.
        """

        logger.info(

            "======= LEGAL ARGUMENTS ======="

        )

        logger.info(

            json.dumps(

                arguments,

                indent=4,

                ensure_ascii=False

            )

        )

        logger.info(

            "==============================="
        )
