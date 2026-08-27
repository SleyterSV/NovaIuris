import re
from typing import Dict, List


class QueryAnalyzer:
    """
    ===========================================================

                    NOVA QUERY ANALYZER

    Analiza la consulta del usuario antes de realizar
    la búsqueda semántica.

    Este servicio identifica automáticamente:

        • Rama del Derecho
        • Materias
        • Órgano Jurisdiccional
        • Tipo documental
        • Palabras clave
        • Intención jurídica

    Será utilizado por:

        • NovaSearch
        • NovaCase
        • NovaCourt

    ===========================================================
    """

    ####################################################################
    ########################### DICCIONARIOS ############################
    ####################################################################

    RAMAS = {

        "constitucional": [
            "constitución",
            "constitucional",
            "amparo",
            "hábeas corpus",
            "habeas corpus",
            "hábeas data",
            "habeas data",
            "cumplimiento",
            "tc",
            "tribunal constitucional"
        ],

        "civil": [
            "civil",
            "contrato",
            "propiedad",
            "obligación",
            "responsabilidad civil",
            "prescripción",
            "nulidad",
            "posesión",
            "usucapión"
        ],

        "penal": [
            "penal",
            "robo",
            "hurto",
            "estafa",
            "homicidio",
            "corrupción",
            "lavado",
            "cohecho",
            "peculado"
        ],

        "laboral": [
            "despido",
            "trabajador",
            "empleador",
            "reposición",
            "cese",
            "remuneración",
            "vacaciones",
            "beneficios sociales",
            "cts"
        ],

        "administrativo": [
            "sunat",
            "osce",
            "indecopi",
            "servir",
            "municipalidad",
            "acto administrativo"
        ],

        "procesal": [
            "apelación",
            "casación",
            "demanda",
            "contestación",
            "medida cautelar",
            "ejecución",
            "proceso"
        ]

    }

    ####################################################################
    ######################## ÓRGANOS EMISORES ###########################
    ####################################################################

    ORGANOS = {

        "Tribunal Constitucional": [
            "tribunal constitucional",
            "tc"
        ],

        "Corte Suprema": [
            "corte suprema",
            "cs"
        ],

        "Corte Superior": [
            "corte superior"
        ],

        "Poder Judicial": [
            "poder judicial",
            "pj"
        ],

        "Corte IDH": [
            "corte interamericana",
            "corte idh"
        ]

    }

    ####################################################################
    ###################### TIPOS DOCUMENTALES ###########################
    ####################################################################

    TIPOS_DOCUMENTO = {

        "Constitución": [
            "constitución"
        ],

        "Código": [
            "código",
            "codigo"
        ],

        "Ley": [
            "ley"
        ],

        "Decreto": [
            "decreto",
            "decreto supremo",
            "decreto legislativo"
        ],

        "Jurisprudencia": [
            "sentencia",
            "casación",
            "casacion",
            "expediente",
            "precedente",
            "jurisprudencia"
        ]

    }

    ####################################################################
    ######################### INTENCIONES ###############################
    ####################################################################

    INTENCIONES = {

        "buscar_norma": [

            "artículo",
            "articulo",
            "ley",
            "código",
            "codigo",
            "constitución"

        ],

        "buscar_jurisprudencia": [

            "sentencia",
            "casación",
            "casacion",
            "precedente",
            "expediente",
            "tribunal constitucional"

        ],

        "buscar_doctrina": [

            "doctrina",
            "autor",
            "interpretación",
            "interpretacion"

        ],

        "consulta_general": []

    }

    ####################################################################
    ###################### LIMPIAR CONSULTA #############################
    ####################################################################

    @staticmethod
    def normalize(
        text: str
    ) -> str:

        text = text.lower()

        text = text.strip()

        text = re.sub(
            r"\s+",
            " ",
            text
        )

        return text

    ####################################################################
    ########################### ANALYZE ################################
    ####################################################################

    def analyze(
        self,
        query: str
    ) -> Dict:

        query = self.normalize(query)

        resultado = {

            "query_original": query,

            "rama": None,

            "organo": None,

            "tipo_documento": None,

            "intencion": "consulta_general",

            "keywords": []

        }

        ###############################################################
        ######################## RAMA #################################
        ###############################################################

        for rama, palabras in self.RAMAS.items():

            if any(
                palabra in query
                for palabra in palabras
            ):

                resultado["rama"] = rama.title()

                resultado["keywords"].extend(
                    palabras
                )

                break

        ###############################################################
        #################### ÓRGANO ###################################
        ###############################################################

        for organo, palabras in self.ORGANOS.items():

            if any(
                palabra in query
                for palabra in palabras
            ):

                resultado["organo"] = organo

                resultado["keywords"].extend(
                    palabras
                )

                break

        ###############################################################
        ################ TIPO DOCUMENTO ###############################
        ###############################################################

        for tipo, palabras in self.TIPOS_DOCUMENTO.items():

            if any(
                palabra in query
                for palabra in palabras
            ):

                resultado["tipo_documento"] = tipo

                resultado["keywords"].extend(
                    palabras
                )

                break

        ###############################################################
        ################### INTENCIÓN #################################
        ###############################################################

        for intencion, palabras in self.INTENCIONES.items():

            if any(
                palabra in query
                for palabra in palabras
            ):

                resultado["intencion"] = intencion

                break

        ###############################################################
        ################ PALABRAS IMPORTANTES ##########################
        ###############################################################

        palabras = re.findall(

            r"[a-zA-ZáéíóúñÁÉÍÓÚÑ]{4,}",

            query

        )

        resultado["keywords"].extend(
            palabras
        )

        ###############################################################
        ################ ELIMINAR DUPLICADOS ###########################
        ###############################################################

        resultado["keywords"] = sorted(

            list(

                set(resultado["keywords"])

            )

        )

        return resultado