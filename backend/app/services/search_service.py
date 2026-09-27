"""NovaSearch retrieval and answer pipeline with stage-level diagnostics."""
import logging
from time import perf_counter
from typing import Any

from app.utils.cancellation import OperationCancelled, check_cancelled
from app.services.embedding_service import EmbeddingService
from app.services.reranker_service import RerankerService
from app.services.legal_repository import LegalRepository, LegalSearchError
from app.services.source_contracts import normalize_public_source, resolve_citations
from app.services.query_analyzer import QueryAnalyzer
from app.services.fusion_service import FusionService
from app.services.citation_service import CitationService
from app.services.context_builder import ContextBuilder
from app.services.answer_service import AnswerService

logger = logging.getLogger("NovaIuris.Search")


class SearchService:
    """Pipeline: analysis, retrieval, ranking, context and verified citations."""

    def __init__(self):
        self.query_analyzer = QueryAnalyzer()
        self.repository = LegalRepository()
        self.fusion_service = FusionService()
        self.reranker = RerankerService()
        self.citation_service = CitationService()
        self.context_builder = ContextBuilder()
        self.answer_service = AnswerService()

    @staticmethod
    def _stage(callback, name, status="running", **details):
        if callback:
            callback(name, status, details)

    def search(self, query: str, filtros: dict[str, Any] | None = None,
               generate_answer: bool = True, build_context: bool = True,
               use_reranker: bool = True, cancellation_token=None,
               progress_callback=None):
        filtros = filtros or {}
        timings = {}
        total_started = perf_counter()

        def timed(name, stage, fn):
            self._stage(progress_callback, stage, "running")
            started = perf_counter()
            try:
                result = fn()
            except Exception:
                timings[name] = round((perf_counter() - started) * 1000, 2)
                self._stage(progress_callback, stage, "failed", duration_ms=timings[name])
                raise
            timings[name] = round((perf_counter() - started) * 1000, 2)
            self._stage(progress_callback, stage, "completed", duration_ms=timings[name])
            return result

        check_cancelled(cancellation_token)
        analysis = timed("query_analysis", "query_analysis", lambda: self.query_analyzer.analyze(query))
        normalized_query = analysis.get("normalized_query") or query
        modulo = filtros.get("modulo", "Todos") or "Todos"
        solo_vigentes = filtros.get("solo_vigentes", True)
        if not isinstance(modulo, str) or not isinstance(solo_vigentes, bool):
            raise SearchPipelineError("INVALID_FILTERS")
        analysis["filters"] = {"modulo": modulo, "solo_vigentes": solo_vigentes}

        check_cancelled(cancellation_token)
        try:
            embedding = timed("embedding", "embedding", lambda: EmbeddingService().generate_embedding(
                normalized_query, cancellation_token=cancellation_token))
        except OperationCancelled:
            raise
        except Exception as error:
            logger.warning("NovaSearch embedding failed (%s)", type(error).__name__)
            raise SearchPipelineError("EMBEDDING_FAILED") from error

        check_cancelled(cancellation_token)
        try:
            results = timed("retrieval", "retrieval", lambda: self.repository.semantic_search(
                embedding=embedding, modulo=modulo, solo_vigentes=solo_vigentes, limit=20))
        except OperationCancelled:
            raise
        except Exception as error:
            if isinstance(error, LegalSearchError):
                raise
            logger.warning("NovaSearch retrieval failed (%s)", type(error).__name__)
            raise LegalSearchError("Legal source search failed") from error
        retrieved_count = len(results)
        self._stage(progress_callback, "retrieval", "completed", retrieved_count=retrieved_count)

        if not results:
            for stage in ("fusion", "reranking", "context", "answer", "citations"):
                self._stage(progress_callback, stage, "skipped")
            timings["total"] = round((perf_counter() - total_started) * 1000, 2)
            logger.info("NovaSearch completed status=no_results retrieved=0 timings_ms=%s", timings)
            return self._result(query, normalized_query, analysis, "no_results",
                                "No se encontraron fuentes que coincidan con los criterios de búsqueda.",
                                [], "", [], [], [{"code": "NO_RESULTS", "message": "No se encontraron fuentes verificables para respaldar esta respuesta."}],
                                timings, retrieved_count, 0)

        check_cancelled(cancellation_token)
        fused = timed("fusion", "fusion", lambda: self.fusion_service.fuse(vector_results=results))
        rerank_warning = None
        if use_reranker:
            check_cancelled(cancellation_token)
            try:
                before_failed = getattr(self.reranker, "last_failed", False)
                ranked = timed("reranking", "reranking", lambda: self.reranker.rerank(
                    query=normalized_query, documents=fused, cancellation_token=cancellation_token))
                if getattr(self.reranker, "last_failed", False) and not before_failed:
                    rerank_warning = {"code": "RERANKING_DEGRADED", "message": "Los resultados se muestran con el orden de recuperación original."}
                fused = ranked
            except OperationCancelled:
                raise
            except Exception as error:
                logger.warning("NovaSearch reranking degraded (%s)", type(error).__name__)
                timings["reranking"] = timings.get("reranking", 0)
                rerank_warning = {"code": "RERANKING_DEGRADED", "message": "Los resultados se muestran con el orden de recuperación original."}
        else:
            self._stage(progress_callback, "reranking", "skipped")
        results = fused[:5]
        reranked_count = len(results)
        self._stage(progress_callback, "reranking", "completed" if use_reranker else "skipped",
                    reranked_count=reranked_count)

        for document in results:
            document["detected_legal_mentions"] = self.citation_service.extract_citations(document.get("texto", ""))

        context = {"text": "", "sources": []}
        if build_context:
            context = timed("context", "context", lambda: self.context_builder.build(
                query=normalized_query, documents=results))
        else:
            self._stage(progress_callback, "context", "skipped")

        answer = ""
        resolved = {"citations": [], "sources_used": [], "warnings": []}
        if generate_answer:
            check_cancelled(cancellation_token)
            generated = timed("answer", "answer", lambda: self.answer_service.generate_answer(
                query=normalized_query, context=context["text"]))
            if generated.get("success") is False:
                raise SearchPipelineError("ANSWER_FAILED")
            answer = self.answer_service.clean_answer(generated.get("answer", ""))
            resolved = timed("citation_validation", "citations", lambda: resolve_citations(answer, context["sources"]))
            answer = resolved["answer"]
            self._stage(progress_callback, "citations", "completed",
                        used_source_count=len(resolved["sources_used"]))
        else:
            self._stage(progress_callback, "answer", "skipped")
            self._stage(progress_callback, "citations", "skipped")

        warnings = list(resolved.get("warnings", []))
        if rerank_warning:
            warnings.append(rerank_warning)
        formatted = self.format_results(results, modulo, context["sources"])
        timings["total"] = round((perf_counter() - total_started) * 1000, 2)
        logger.info("NovaSearch completed status=%s retrieved=%s prioritized=%s used_sources=%s timings_ms=%s",
                    "completed", retrieved_count, reranked_count, len(resolved["sources_used"]), timings)
        self._stage(progress_callback, "completed", "completed", retrieved_count=retrieved_count,
                    reranked_count=reranked_count, used_source_count=len(resolved["sources_used"]))
        return self._result(query, normalized_query, analysis, "completed", answer,
                            formatted, context["text"], resolved["sources_used"],
                            resolved["citations"], warnings, timings, retrieved_count, reranked_count,
                            [mention for item in results for mention in item.get("detected_legal_mentions", [])])

    @staticmethod
    def _result(query, normalized_query, analysis, status, answer, documents, context,
                sources, citations, warnings, timings, retrieved_count, reranked_count,
                mentions=None):
        return {"query": query, "query_normalizada": normalized_query,
                "analysis": analysis, "result_status": status, "answer": answer,
                "documents": documents, "context": context, "sources": sources,
                "citations": citations, "warnings": warnings,
                "detected_legal_mentions": mentions or [],
                "metadata": {"counts": {"retrieved_count": retrieved_count,
                                           "reranked_count": reranked_count,
                                           "used_source_count": len(sources)},
                             "timings_ms": timings}}

    @staticmethod
    def format_results(resultados, modulo: str, context_sources: list[dict] | None = None):
        if not resultados:
            return []
        formatted = []
        sources_by_record = {str(source.get("document_id")): source for source in (context_sources or [])}
        for index, item in enumerate(resultados):
            texto = item.get("texto", "")
            resumen = item.get("resumen") or (texto[:250] + "..." if len(texto) > 250 else texto)
            source = sources_by_record.get(str(item.get("id"))) or (
                context_sources[index] if context_sources and index < len(context_sources) else None
            ) or normalize_public_source(item, excerpt=str(texto or "")[:ContextBuilder.MAX_CHARS_PER_DOCUMENT])
            formatted.append({"id": item.get("id"), "source_id": source["source_id"], "source": source,
                "detected_legal_mentions": item.get("detected_legal_mentions", []),
                "article": source.get("article"), "official_url": source.get("official_url"),
                "metadata": source.get("metadata", {}),
                "titulo": item.get("articulo") or item.get("fuente") or "Documento legal",
                "tipo_documento": item.get("tipo_documento"), "rama": item.get("rama"),
                "modulo": item.get("rama", modulo), "fuente": item.get("fuente"),
                "jerarquia": item.get("jerarquia"), "organo_emisor": item.get("organo_emisor"),
                "expediente": item.get("expediente"), "materia": item.get("materia"),
                "instancia": item.get("instancia"), "numero": item.get("numero"),
                "fecha_publicacion": item.get("fecha_publicacion"),
                "fecha_resolucion": item.get("fecha_resolucion"), "sumilla": item.get("sumilla"),
                "precedente_vinculante": item.get("precedente_vinculante", False),
                "keywords": item.get("keywords", []), "resumen_ia": resumen,
                "extracto_exacto": texto,
                "vector_similarity": item.get("similarity"),
                "reranker_score": item.get("rerank_score")})
        return formatted


class SearchPipelineError(RuntimeError):
    def __init__(self, code):
        self.code = code
        super().__init__(code)
