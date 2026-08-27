import hashlib
import re
import uuid
from datetime import datetime
from typing import List

from app.models.jurisprudence_document import JurisprudenceDocument
from app.utils.pdf_reader import PDFReader


class JurisprudenceProcessor:
    """
    Procesa un documento jurisprudencial y extrae automáticamente
    los metadatos más importantes antes de generar embeddings.
    """

    def process(self, fuente: str, texto: str):

        texto = PDFReader.clean_text(texto)

        primera_pagina = PDFReader.first_page(texto)

        documento = JurisprudenceDocument(

            id=str(uuid.uuid4()),

            hash_documento=self.generate_hash(texto),

            rama="Jurisprudencia",

            fuente=fuente,

            tipo_documento=self.detect_document_type(
                primera_pagina,
                fuente
            ),

            jerarquia=self.detect_hierarchy(
                primera_pagina
            ),

            articulo=self.detect_title(
                primera_pagina,
                fuente
            ),

            texto=texto,

            resumen=PDFReader.build_summary(texto),

            vigencia="Vigente",

            entidad=self.detect_entity(
                primera_pagina
            ),

            numero=self.detect_document_number(
                primera_pagina
            ),

            fecha_publicacion=self.detect_date(
                primera_pagina
            ),

            organo_emisor=self.detect_entity(
                primera_pagina
            ),

            expediente=self.detect_expediente(
                primera_pagina
            ),

            tipo_resolucion=self.detect_resolution_type(
                primera_pagina
            ),

            ponente=self.detect_ponente(
                primera_pagina
            ),

            fecha_resolucion=self.detect_date(
                primera_pagina
            ),

            sumilla=self.detect_sumilla(
                texto
            ),

            precedente_vinculante=self.detect_precedente(
                primera_pagina
            ),

            materia=self.detect_materia(
                primera_pagina
            ),

            instancia=self.detect_instancia(
                primera_pagina
            ),

            keywords=self.extract_keywords(texto),

            metadata={}
        )

        documento.search_text = documento.build_search_text()

        return documento

    ###############################################################
    ######################## HASH #################################
    ###############################################################

    @staticmethod
    def generate_hash(text):

        return hashlib.sha256(
            text.encode("utf-8")
        ).hexdigest()

    ###############################################################
    ################### TIPO DOCUMENTO ############################
    ###############################################################

    @staticmethod
    def detect_document_type(text, fuente):

        texto = (text + fuente).lower()

        if "casación" in texto:
            return "Casación"

        if "sentencia" in texto:
            return "Sentencia"

        if "tribunal constitucional" in texto:
            return "Sentencia TC"

        if "acuerdo plenario" in texto:
            return "Acuerdo Plenario"

        if "pleno casatorio" in texto:
            return "Pleno Casatorio"

        if "resolución" in texto:
            return "Resolución"

        if "auto" in texto:
            return "Auto"

        return "Jurisprudencia"

    ###############################################################
    ###################### JERARQUÍA ###############################
    ###############################################################

    @staticmethod
    def detect_hierarchy(text):

        texto = text.lower()

        if "tribunal constitucional" in texto:
            return "Constitucional"

        if "corte suprema" in texto:
            return "Suprema"

        if "corte superior" in texto:
            return "Superior"

        return "Jurisprudencial"

    ###############################################################
    ###################### TÍTULO #################################
    ###############################################################

    @staticmethod
    def detect_title(text, fuente):

        lineas = text.splitlines()

        for linea in lineas:

            linea = linea.strip()

            if len(linea) > 10:

                return linea

        return fuente

    ###############################################################
    ###################### EXPEDIENTE ##############################
    ###############################################################

    @staticmethod
    def detect_expediente(text):

        patrones = [

            r'EXP\.\s*N[°º.]?\s*([\w\-\/]+)',

            r'EXPEDIENTE\s*N[°º.]?\s*([\w\-\/]+)',

            r'CASACIÓN\s*N[°º.]?\s*([\w\-\/]+)',

        ]

        for patron in patrones:

            resultado = re.search(
                patron,
                text,
                re.IGNORECASE
            )

            if resultado:

                return resultado.group(1)

        return ""

    ###############################################################
    ###################### FECHA ##################################
    ###############################################################

    @staticmethod
    def detect_date(text):

        patron = r'(\d{1,2})\s+de\s+([A-Za-zÁÉÍÓÚáéíóú]+)\s+de\s+(\d{4})'

        resultado = re.search(
            patron,
            text,
            re.IGNORECASE
        )

        if not resultado:
            return None

        meses = {
            "enero":1,
            "febrero":2,
            "marzo":3,
            "abril":4,
            "mayo":5,
            "junio":6,
            "julio":7,
            "agosto":8,
            "septiembre":9,
            "setiembre":9,
            "octubre":10,
            "noviembre":11,
            "diciembre":12
        }

        dia = int(resultado.group(1))
        mes = meses.get(resultado.group(2).lower())
        anio = int(resultado.group(3))

        if mes is None:
            return None

        return datetime(anio, mes, dia).date().isoformat()

    ###############################################################
    ###################### ENTIDAD ################################
    ###############################################################

    @staticmethod
    def detect_entity(text):

        texto = text.lower()

        if "tribunal constitucional" in texto:
            return "Tribunal Constitucional"

        if "corte suprema" in texto:
            return "Corte Suprema de Justicia"

        if "corte superior" in texto:
            return "Corte Superior de Justicia"

        if "poder judicial" in texto:
            return "Poder Judicial"

        if "jurado nacional de elecciones" in texto:
            return "Jurado Nacional de Elecciones"

        return ""

    ###############################################################
    ################ TIPO DE RESOLUCIÓN ############################
    ###############################################################

    @staticmethod
    def detect_resolution_type(text):

        texto = text.lower()

        if "casación" in texto:
            return "Casación"

        if "sentencia" in texto:
            return "Sentencia"

        if "auto" in texto:
            return "Auto"

        if "acuerdo plenario" in texto:
            return "Acuerdo Plenario"

        if "pleno casatorio" in texto:
            return "Pleno Casatorio"

        if "resolución" in texto:
            return "Resolución"

        return ""

    ###############################################################
    ###################### PONENTE ################################
    ###############################################################

    @staticmethod
    def detect_ponente(text):

        patrones = [

            r'Ponente[:\s]+([A-ZÁÉÍÓÚÑa-záéíóúñ\s]+)',

            r'Magistrado Ponente[:\s]+([A-ZÁÉÍÓÚÑa-záéíóúñ\s]+)',

        ]

        for patron in patrones:

            resultado = re.search(
                patron,
                text,
                re.IGNORECASE
            )

            if resultado:

                return resultado.group(1).strip()

        return ""

    ###############################################################
    ###################### SUMILLA ################################
    ###############################################################

    @staticmethod
    def detect_sumilla(text):

        lineas = text.splitlines()

        resumen = []

        for linea in lineas:

            linea = linea.strip()

            if len(linea) > 30:

                resumen.append(linea)

            if len(" ".join(resumen)) > 500:
                break

        return " ".join(resumen)

    ###############################################################
    ################ PRECEDENTE VINCULANTE #########################
    ###############################################################

    @staticmethod
    def detect_precedente(text):

        texto = text.lower()

        palabras = [

            "precedente vinculante",

            "observancia obligatoria",

            "doctrina jurisprudencial",

            "precedente"

        ]

        return any(p in texto for p in palabras)

    ###############################################################
    ###################### MATERIA ################################
    ###############################################################

    @staticmethod
    def detect_materia(text):

        texto = text.lower()

        materias = {

            "penal": "Penal",

            "civil": "Civil",

            "constitucional": "Constitucional",

            "laboral": "Laboral",

            "tributario": "Tributario",

            "administrativo": "Administrativo",

            "familia": "Familia",

            "comercial": "Comercial",

            "procesal": "Procesal"

        }

        for palabra, materia in materias.items():

            if palabra in texto:

                return materia

        return ""

    ###############################################################
    ###################### INSTANCIA ###############################
    ###############################################################

    @staticmethod
    def detect_instancia(text):

        texto = text.lower()

        if "tribunal constitucional" in texto:
            return "Tribunal Constitucional"

        if "corte suprema" in texto:
            return "Corte Suprema"

        if "corte superior" in texto:
            return "Corte Superior"

        if "juzgado" in texto:
            return "Juzgado"

        return ""

    ###############################################################
    ###################### NÚMERO #################################
    ###############################################################

    @staticmethod
    def detect_document_number(text):

        patrones = [

            r'N[°º.]?\s*([\w\-\/]+)',

            r'NÚMERO\s*([\w\-\/]+)',

        ]

        for patron in patrones:

            resultado = re.search(
                patron,
                text,
                re.IGNORECASE
            )

            if resultado:

                return resultado.group(1)

        return ""

    ###############################################################
    ###################### KEYWORDS ###############################
    ###############################################################

    @staticmethod
    def extract_keywords(text) -> List[str]:

        palabras = re.findall(

            r"\b[A-ZÁÉÍÓÚÑ][a-záéíóúñ]{4,}\b",

            text

        )

        palabras = sorted(set(palabras))

        return palabras[:40]