import os
import json
import time
import logging

from typing import List

from dotenv import load_dotenv
from openai import OpenAI
from app.utils.cancellation import OperationCancelled, check_cancelled


load_dotenv()


logger = logging.getLogger(
    "NovaIuris.Reranker"
)


class RerankerService:
    """
    Servicio de reranking jurídico.

    Reordena documentos recuperados por búsqueda vectorial
    según su relevancia respecto de una consulta.

    Utilizado por:

        - NovaSearch
        - NovaCase
        - NovaCourt

    IMPORTANTE:

    NovaCase puede desactivar este servicio para evitar
    llamadas LLM innecesarias durante investigaciones
    compuestas por múltiples consultas.
    """

    DEFAULT_MODEL = "gpt-4o-mini"

    DEFAULT_TIMEOUT = 45.0

    DEFAULT_RETRIES = 2

    MAX_DOCUMENTS = 10


    def __init__(
        self,
        enabled: bool = True
    ):

        self.enabled = enabled


        self.MODEL = os.getenv(

            "OPENAI_RERANKER_MODEL",

            self.DEFAULT_MODEL

        )


        self.TIMEOUT = float(

            os.getenv(

                "OPENAI_RERANKER_TIMEOUT",

                self.DEFAULT_TIMEOUT

            )

        )


        api_key = os.getenv(
            "OPENAI_API_KEY"
        )


        if not api_key:

            raise ValueError(
                "OPENAI_API_KEY no encontrada."
            )


        self.client = OpenAI(
            max_retries=0,

            api_key=api_key,

            timeout=self.TIMEOUT

        )


        logger.info(

            "RerankerService iniciado. "
            "Modelo: %s | Activo: %s",

            self.MODEL,

            self.enabled

        )


    # ============================================================
    # PROMPT
    # ============================================================

    @staticmethod
    def build_prompt(
        query: str,
        documents: List[dict]
    ) -> str:

        documentos = []


        for i, doc in enumerate(

            documents,

            start=1

        ):

            documentos.append(

                f"""
DOCUMENTO {i}

ID:
{doc.get("id")}

Tipo:
{doc.get("tipo_documento")}

Rama:
{doc.get("rama")}

Materia:
{doc.get("materia")}

Órgano:
{doc.get("organo_emisor")}

Expediente:
{doc.get("expediente")}

Título:
{doc.get("articulo") or doc.get("fuente")}

Resumen:
{doc.get("resumen")}

Texto:
{(doc.get("texto") or "")[:1600]}
"""

            )


        documentos_texto = "\n\n".join(
            documentos
        )


        return f"""
Eres un especialista en recuperación de información jurídica.

Tu única función es REORDENAR los documentos
según su relevancia jurídica respecto de la consulta.

NO debes:

- responder la consulta;
- inventar documentos;
- agregar documentos;
- eliminar documentos;
- modificar los IDs.

Únicamente debes devolver el orden de relevancia.

Consulta:

{query}

Documentos:

{documentos_texto}

Devuelve únicamente JSON válido:

{{
    "ranking": [
        {{
            "id": "ID_DOCUMENTO",
            "score": 98,
            "motivo": "Razón breve de relevancia."
        }}
    ]
}}

El score debe ser un número entre 0 y 100.

No escribas markdown.

No escribas explicaciones fuera del JSON.
"""


    # ============================================================
    # RERANK
    # ============================================================

    def rerank(
        self,
        query: str,
        documents: List[dict],
        retries: int = DEFAULT_RETRIES,
        cancellation_token=None
    ) -> List[dict]:

        self.last_failed = False
        check_cancelled(cancellation_token)

        if not documents:

            return []


        # --------------------------------------------------------
        # RERANKING DESACTIVADO
        # --------------------------------------------------------

        if not self.enabled:

            logger.info(
                "Reranking desactivado. "
                "Se conserva el ranking original."
            )

            return documents


        # --------------------------------------------------------
        # LIMITAR DOCUMENTOS
        # --------------------------------------------------------

        documents_to_rank = documents[
            :self.MAX_DOCUMENTS
        ]


        logger.info(

            "Rerankeando %s documentos.",

            len(documents_to_rank)

        )


        prompt = self.build_prompt(

            query=query,

            documents=documents_to_rank

        )


        last_error = None


        # --------------------------------------------------------
        # LLAMADA AL MODELO
        # --------------------------------------------------------

        for attempt in range(

            1,

            retries + 1

        ):

            check_cancelled(cancellation_token)

            try:

                response = (

                    self.client.chat.completions.create(

                        model=self.MODEL,

                        response_format={

                            "type":
                                "json_object"

                        },

                        messages=[

                            {
                                "role": "system",

                                "content":
                                    (
                                        "Eres un sistema "
                                        "de recuperación "
                                        "jurídica. "
                                        "Devuelve "
                                        "únicamente JSON válido."
                                    )
                            },

                            {
                                "role": "user",

                                "content":
                                    prompt
                            }

                        ]

                    )

                )


                content = (

                    response
                    .choices[0]
                    .message
                    .content

                )


                if not content:

                    raise ValueError(
                        "El reranker devolvió una respuesta vacía."
                    )


                data = json.loads(
                    content
                )


                ranking = data.get(
                    "ranking",
                    []
                )


                if not isinstance(
                    ranking,
                    list
                ):

                    raise ValueError(
                        "El ranking no es una lista válida."
                    )


                # ------------------------------------------------
                # DOCUMENTOS POR ID
                # ------------------------------------------------

                documentos_por_id = {

                    str(
                        doc.get("id")
                    ): doc

                    for doc in documents_to_rank

                }


                documentos_ordenados = []

                ids_agregados = set()


                # ------------------------------------------------
                # PROCESAR RANKING
                # ------------------------------------------------

                for item in ranking:

                    if not isinstance(
                        item,
                        dict
                    ):

                        continue


                    document_id = str(

                        item.get(
                            "id",
                            ""
                        )

                    )


                    if document_id not in documentos_por_id:

                        continue


                    if document_id in ids_agregados:

                        continue


                    try:

                        score = float(

                            item.get(
                                "score",
                                0
                            )

                        )

                    except (
                        TypeError,
                        ValueError
                    ):

                        score = 0.0


                    score = max(

                        0.0,

                        min(
                            100.0,
                            score
                        )

                    )


                    documento = (

                        documentos_por_id[
                            document_id
                        ].copy()

                    )


                    documento[
                        "rerank_score"
                    ] = score


                    documento[
                        "rerank_reason"
                    ] = str(

                        item.get(
                            "motivo",
                            ""
                        )

                    )


                    documentos_ordenados.append(
                        documento
                    )


                    ids_agregados.add(
                        document_id
                    )


                # ------------------------------------------------
                # CONSERVAR LOS NO MENCIONADOS
                # ------------------------------------------------

                for documento in documents_to_rank:

                    document_id = str(

                        documento.get(
                            "id"
                        )

                    )


                    if document_id not in ids_agregados:

                        documentos_ordenados.append(
                            documento
                        )


                # ------------------------------------------------
                # AGREGAR DOCUMENTOS FUERA DEL TOP RERANKEADO
                # ------------------------------------------------

                documentos_ordenados.extend(

                    documents[
                        self.MAX_DOCUMENTS:
                    ]

                )


                logger.info(
                    "Reranking completado correctamente."
                )


                return documentos_ordenados


            except OperationCancelled:
                raise
            except Exception as error:

                last_error = error


                logger.warning("Reranking attempt failed attempt=%s/%s error_type=%s",
                               attempt, retries, type(error).__name__)


                if attempt < retries:

                    time.sleep(
                        2 ** (
                            attempt - 1
                        )
                    )


        # --------------------------------------------------------
        # FALLBACK
        # --------------------------------------------------------

        self.last_failed = True
        logger.error("Reranking exhausted retries error_type=%s", type(last_error).__name__)


        logger.warning(

            "Se conservará el ranking vectorial original."
        )


        return documents


    # ============================================================
    # CAMBIAR ESTADO
    # ============================================================

    def set_enabled(
        self,
        enabled: bool
    ):

        self.enabled = bool(
            enabled
        )


        logger.info(

            "Reranking %s.",

            "activado"
            if self.enabled
            else "desactivado"

        )
