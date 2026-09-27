from app.utils.cancellation import check_cancelled
from typing import Dict, Any

from app.services.embedding_service import EmbeddingService
from app.services.reranker_service import RerankerService
from app.services.legal_repository import LegalRepository

from app.services.query_analyzer import QueryAnalyzer
from app.services.fusion_service import FusionService
from app.services.citation_service import CitationService
from app.services.context_builder import ContextBuilder
from app.services.answer_service import AnswerService


class SearchService:
    """
    Servicio principal de NovaSearch.

    Flujo:

    Usuario
        ↓
    Embedding
        ↓
    Vector Search
        ↓
    Formateo
        ↓
    API
    """

    def __init__(self):

        self.query_analyzer = QueryAnalyzer()


        self.repository = LegalRepository()

        self.fusion_service = FusionService()

        self.reranker = RerankerService()

        self.citation_service = CitationService()

        self.context_builder = ContextBuilder()

        self.answer_service = AnswerService()

    ####################################################################
    ######################## BUSQUEDA PRINCIPAL #########################
    ####################################################################

    def search(
        self,
        query: str,
        filtros: Dict[str, Any] | None = None,
        generate_answer: bool = True,
        build_context: bool = True,
        use_reranker: bool = True,
        cancellation_token=None
    ):

        if filtros is None:

            filtros = {}

        ################################################################
        ################ ANALISIS DE LA CONSULTA ########################
        ################################################################

        analysis = self.query_analyzer.analyze(

            query

        )

        query_mejorada = analysis.get(

            "normalized_query",

            query

        )

        modulo = filtros.get(

            "modulo",

            analysis.get(

                "rama",

                "Todos"

            )

        )

        ################################################################
        ################## GENERACION DEL EMBEDDING #####################
        ################################################################

        check_cancelled(cancellation_token)
        embedding = EmbeddingService().generate_embedding(

            query_mejorada, cancellation_token=cancellation_token

        )

        ################################################################
        ################### BUSQUEDA VECTORIAL ###########################
        ################################################################

        check_cancelled(cancellation_token)
        resultados = self.repository.semantic_search(

            embedding=embedding,

            modulo=modulo,

            limit=20

        )

        if not resultados:

            return {

                "query": query,

                "query_normalizada": query_mejorada,

                "analysis": analysis,

                "answer": "No se encontraron documentos jurídicos relacionados con la consulta.",

                "documents": [],

                "context": ""

            }

        ################################################################
        ###################### FUSION DE RESULTADOS #####################
        ################################################################

        resultados = self.fusion_service.fuse(
            vector_results=resultados
        )

        ################################################################
        ######################## RERANKING ##############################
        ################################################################

        if use_reranker:

            check_cancelled(cancellation_token)
            resultados = self.reranker.rerank(

                query=query_mejorada,

                documents=resultados

            )

        ################################################################
        ###################### TOP DOCUMENTOS ##########################
        ################################################################

        resultados = resultados[:5]


        ################################################################
        ###################### EXTRAER CITAS ############################
        ################################################################

        for documento in resultados:

            documento["citations"] = (

                self.citation_service.extract_citations(

                    documento.get(
                        "texto",
                        ""
                    )

                )

            )


        ################################################################
        ###################### CONSTRUIR CONTEXTO #######################
        ################################################################

        contexto = ""

        if build_context:

            contexto = self.context_builder.build(

                query=query_mejorada,

                documents=resultados

            )


        ################################################################
        ###################### RESPUESTA IA #############################
        ################################################################

        respuesta_texto = ""

        if generate_answer:

            check_cancelled(cancellation_token)
            respuesta = self.answer_service.generate_answer(

                query=query_mejorada,

                context=contexto

            )

            respuesta_texto = self.answer_service.clean_answer(

                respuesta.get(
                    "answer",
                    ""
                )

            )


        ################################################################
        ###################### FORMATEAR RESULTADOS #####################
        ################################################################

        resultados_formateados = self.format_results(

            resultados,

            modulo

        )


        ################################################################
        ###################### RESPUESTA FINAL ##########################
        ################################################################

        return {

            "query": query,

            "query_normalizada": query_mejorada,

            "analysis": analysis,

            "answer": respuesta_texto,

            "documents": resultados_formateados,

            "context": contexto

        }
    ####################################################################
    ###################### FORMATEAR RESULTADOS #########################
    ####################################################################

    @staticmethod
    def format_results(
        resultados,
        modulo: str
    ):

        if not resultados:
            return []

        formatted = []

        for item in resultados:

            texto = item.get(
                "texto",
                ""
            )

            resumen = item.get(
                "resumen"
            )

            if not resumen:

                resumen = (
                    texto[:250] + "..."
                    if len(texto) > 250
                    else texto
                )

            formatted.append({

                "id": item.get("id"),

                "titulo": (
                    item.get("articulo")
                    or item.get("fuente")
                    or "Documento legal"
                ),

                "tipo_documento": item.get(
                    "tipo_documento"
                ),

                "rama": item.get(
                    "rama"
                ),

                "modulo": item.get(
                    "rama",
                    modulo
                ),

                "fuente": item.get(
                    "fuente"
                ),

                "jerarquia": item.get(
                    "jerarquia"
                ),

                "organo_emisor": item.get(
                    "organo_emisor"
                ),

                "expediente": item.get(
                    "expediente"
                ),

                "materia": item.get(
                    "materia"
                ),

                "instancia": item.get(
                    "instancia"
                ),

                "numero": item.get(
                    "numero"
                ),

                "fecha_publicacion": item.get(
                    "fecha_publicacion"
                ),

                "fecha_resolucion": item.get(
                    "fecha_resolucion"
                ),

                "sumilla": item.get(
                    "sumilla"
                ),

                "precedente_vinculante": item.get(
                    "precedente_vinculante",
                    False
                ),

                "keywords": item.get(
                    "keywords",
                    []
                ),

                "resumen_ia": resumen,

                "extracto_exacto": texto,

                "score": round(
                    float(
                        item.get(
                            "similarity",
                            0
                        )
                    ),
                    4
                )

            })

        return formatted