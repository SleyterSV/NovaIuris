from app.utils.cancellation import check_cancelled
from typing import Dict, Any

from app.services.embedding_service import EmbeddingService
from app.services.reranker_service import RerankerService
from app.services.legal_repository import LegalRepository
from app.services.source_contracts import normalize_public_source, resolve_citations

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
                "result_status": "no_results",

                "answer": "No se encontraron documentos jurídicos relacionados con la consulta.",

                "documents": [],

                "context": "",
                "sources": [], "citations": [], "sources_used": [],
                "detected_legal_mentions": [],
                "warnings": [{"code": "NO_RESULTS", "message": "No se encontraron fuentes verificables para respaldar esta respuesta."}]

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

            documento["detected_legal_mentions"] = (

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

        contexto = {"text": "", "sources": []}

        if build_context:

            contexto = self.context_builder.build(

                query=query_mejorada,

                documents=resultados

            )


        ################################################################
        ###################### RESPUESTA IA #############################
        ################################################################

        respuesta_texto = ""
        resolved = {"citations": [], "sources_used": [], "warnings": []}

        if generate_answer:

            check_cancelled(cancellation_token)
            respuesta = self.answer_service.generate_answer(

                query=query_mejorada,

                context=contexto["text"]

            )

            respuesta_texto = self.answer_service.clean_answer(

                respuesta.get(
                    "answer",
                    ""
                )

            )
            resolved = resolve_citations(respuesta_texto, contexto["sources"])
            respuesta_texto = resolved["answer"]


        ################################################################
        ###################### FORMATEAR RESULTADOS #####################
        ################################################################

        resultados_formateados = self.format_results(

            resultados,

            modulo,
            contexto["sources"]

        )


        ################################################################
        ###################### RESPUESTA FINAL ##########################
        ################################################################

        return {

            "query": query,

            "query_normalizada": query_mejorada,

            "analysis": analysis,

            "result_status": "completed",

            "answer": respuesta_texto,

            "documents": resultados_formateados,

            "context": contexto["text"],
            "sources": resolved["sources_used"],
            "citations": resolved["citations"],
            "warnings": resolved["warnings"],
            "detected_legal_mentions": [mention for item in resultados
                                         for mention in item.get("detected_legal_mentions", [])]

        }
    ####################################################################
    ###################### FORMATEAR RESULTADOS #########################
    ####################################################################

    @staticmethod
    def format_results(
        resultados,
        modulo: str,
        context_sources: list[dict] | None = None
    ):

        if not resultados:
            return []

        formatted = []
        sources_by_record = {str(source.get("document_id")): source for source in (context_sources or [])}

        for index, item in enumerate(resultados):

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

            source = sources_by_record.get(str(item.get("id"))) or (
                context_sources[index] if context_sources and index < len(context_sources) else None
            ) or normalize_public_source(
                item, excerpt=str(texto or "")[:ContextBuilder.MAX_CHARS_PER_DOCUMENT])
            formatted.append({

                "id": item.get("id"),

                "source_id": source["source_id"],
                "source": source,
                "detected_legal_mentions": item.get("detected_legal_mentions", []),
                "article": source.get("article"),
                "official_url": source.get("official_url"),
                "metadata": source.get("metadata", {}),

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
