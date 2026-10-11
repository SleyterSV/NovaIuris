"""NovaSearch retrieval and answer pipeline with stage-level diagnostics."""
import logging
from time import perf_counter
from typing import Any

from app.utils.cancellation import OperationCancelled, check_cancelled
from app.services.embedding_service import EmbeddingService
from app.services.reranker_service import RerankerService
from app.services.legal_repository import LegalRepository, LegalSearchError
from app.services.legal_repository_v2 import LegalRepositoryV2
from app.services.legal_query_identity import (asks_about_vigencia, asks_for_decision,
                                                explicit_tc_expediente)
from app.services.source_contracts import normalize_public_source, resolve_citations
from app.services.query_analyzer import QueryAnalyzer
from app.services.fusion_service import FusionService
from app.services.citation_service import CitationService
from app.services.context_builder import ContextBuilder
from app.services.answer_service import AnswerService

logger = logging.getLogger("NovaIuris.Search")


def word_safe_excerpt(value: str, limit: int = 250) -> str:
    """Presentation preview only; never changes the canonical unit excerpt."""
    text = str(value or "").strip()
    if len(text) <= limit:
        return text
    sentence = max(text.rfind(mark, 0, limit) for mark in (". ", "! ", "? "))
    if sentence >= limit // 2:
        return text[:sentence + 1].rstrip() + "…"
    boundary = text.rfind(" ", 0, limit + 1)
    if boundary < limit // 2:
        boundary = text.find(" ", limit)
    return text[:boundary if boundary != -1 else len(text)].rstrip(" \t\n([{") + "…"


class SearchService:
    """Pipeline: analysis, retrieval, ranking, context and verified citations."""

    def __init__(self, knowledge_version="v1"):
        self.knowledge_version = knowledge_version
        if self.knowledge_version not in {"v1", "v2"}:
            raise SearchPipelineError("INVALID_KNOWLEDGE_VERSION")
        self.query_analyzer = QueryAnalyzer()
        self.repository = LegalRepositoryV2() if self.knowledge_version == "v2" else LegalRepository()
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
        version = getattr(self, "knowledge_version", "v1")
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
        try:
            exact_expediente = explicit_tc_expediente(normalized_query) if version == "v2" else None
        except ValueError as error:
            raise SearchPipelineError("MULTIPLE_EXACT_CASES") from error
        decision_intent = version == "v2" and asks_for_decision(normalized_query)
        if version == "v2":
            analysis["exact_expediente"] = exact_expediente
            analysis["decision_intent"] = decision_intent
        modulo = filtros.get("modulo", "Todos") or "Todos"
        solo_vigentes = filtros.get("solo_vigentes", True)
        vigencia_explicit = filtros.get("vigencia_explicit", False)
        if (not isinstance(modulo, str) or not isinstance(solo_vigentes, bool)
                or not isinstance(vigencia_explicit, bool)):
            raise SearchPipelineError("INVALID_FILTERS")
        analysis["filters"] = {"modulo": modulo, "solo_vigentes": solo_vigentes}
        if version == "v2":
            analysis["filters"]["vigencia_explicit"] = vigencia_explicit

        check_cancelled(cancellation_token)
        try:
            def embed_query():
                provider = EmbeddingService()
                if version == "v2" and provider.MODEL != "text-embedding-3-small":
                    raise ValueError("EMBEDDING_MODEL_MISMATCH")
                return provider.generate_embedding(normalized_query, cancellation_token=cancellation_token)
            embedding = timed("embedding", "embedding", embed_query)
        except OperationCancelled:
            raise
        except Exception as error:
            logger.warning("NovaSearch embedding failed (%s)", type(error).__name__)
            raise SearchPipelineError("EMBEDDING_FAILED") from error

        check_cancelled(cancellation_token)
        try:
            if version == "v2":
                results = timed("retrieval", "retrieval", lambda: self.repository.search(
                    embedding=embedding, query_text=normalized_query, match_count=20,
                    filter_rama=LegalRepository.normalize_rama(modulo),
                    filter_expediente=exact_expediente))
            else:
                results = timed("retrieval", "retrieval", lambda: self.repository.semantic_search(
                    embedding=embedding, modulo=modulo, solo_vigentes=solo_vigentes, limit=20))
        except OperationCancelled:
            raise
        except Exception as error:
            if isinstance(error, LegalSearchError):
                raise
            logger.warning("NovaSearch retrieval failed (%s)", type(error).__name__)
            raise LegalSearchError("Legal source search failed") from error
        if exact_expediente:
            results = [row for row in results if row.get("expediente") == exact_expediente]
        retrieved_count = len(results)
        self._stage(progress_callback, "retrieval", "completed", retrieved_count=retrieved_count)

        if not results:
            for stage in ("fusion", "reranking", "context", "answer", "citations"):
                self._stage(progress_callback, stage, "skipped")
            timings["total"] = round((perf_counter() - total_started) * 1000, 2)
            empty_status = "no_exact_case_found" if exact_expediente else "no_results"
            logger.info("NovaSearch completed knowledge_version=%s status=%s result_count=0 empty_result=true timings_ms=%s", version, empty_status, timings)
            empty_warnings = ([{"code": "NO_EXACT_CASE_FOUND", "message": "No se encontró el expediente exacto en el corpus publicado."}]
                              if exact_expediente else [{"code": "NO_RESULTS", "message": "No se encontraron fuentes verificables para respaldar esta respuesta."}])
            if version == "v2" and (asks_about_vigencia(normalized_query) or
                                    (solo_vigentes and vigencia_explicit)):
                empty_warnings.append({"code": "VIGENCIA_FILTER_UNAVAILABLE", "message": "El corpus V2 no clasifica vigencia normativa; este filtro no se aplicó."})
            empty = self._result(query, normalized_query, analysis, empty_status,
                                "No se encontró el expediente exacto en el corpus publicado." if exact_expediente else
                                "No se encontraron fuentes que coincidan con los criterios de búsqueda.",
                                [], "", [], [], empty_warnings,
                                timings, retrieved_count, 0)
            empty["metadata"]["knowledge_version"] = version
            return empty

        check_cancelled(cancellation_token)
        if version == "v2":
            # The V2 RPC already combines lexical and vector signals and defines its rank.
            fused = results
            self._stage(progress_callback, "fusion", "skipped")
            use_reranker = False
        else:
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
        if exact_expediente and decision_intent:
            decision = next((row for row in fused if row.get("unit_type") == "decision"), None)
            if decision is not None:
                fused = [decision] + [row for row in fused if row is not decision]
        results = fused[:5]
        reranked_count = len(results)
        self._stage(progress_callback, "reranking", "completed" if use_reranker else "skipped",
                    reranked_count=reranked_count)

        for document in results:
            document["detected_legal_mentions"] = self.citation_service.extract_citations(document.get("texto", ""))

        answer_documents = results
        if exact_expediente and decision_intent:
            decision = next((row for row in results if row.get("unit_type") == "decision"), None)
            if decision is not None:
                answer_documents = [decision]
            else:
                # A foundation cannot establish the disposition by inference.
                for stage in ("context", "answer", "citations"):
                    self._stage(progress_callback, stage, "skipped")
                timings["total"] = round((perf_counter() - total_started) * 1000, 2)
                response = self._result(query, normalized_query, analysis, "no_exact_decision_found",
                    "Se encontraron unidades del expediente, pero no una unidad de decisión verificable.",
                    [], "", [], [],
                    [{"code": "NO_EXACT_DECISION_FOUND", "message":
                      "No se encontró una unidad de decisión verificable para este expediente."}],
                    timings, retrieved_count, reranked_count)
                response["metadata"]["knowledge_version"] = version
                return response
        context = {"text": "", "sources": []}
        if build_context:
            context = timed("context", "context", lambda: self.context_builder.build(
                query=normalized_query, documents=answer_documents))
        else:
            self._stage(progress_callback, "context", "skipped")

        answer = ""
        resolved = {"citations": [], "sources_used": [], "warnings": []}
        if generate_answer:
            check_cancelled(cancellation_token)
            if version == "v2" and exact_expediente and decision_intent and \
                    answer_documents[0].get("unit_type") == "decision" and context["sources"]:
                generated = timed("answer", "answer", lambda: AnswerService.exact_decision_answer(context["sources"][0]))
            else:
                generated = timed("answer", "answer", lambda: self.answer_service.generate_answer(
                    query=normalized_query, context=context["text"], grounded_v2=(version == "v2"))
                    if version == "v2" else self.answer_service.generate_answer(
                    query=normalized_query, context=context["text"]))
            if generated.get("success") is False:
                raise SearchPipelineError("ANSWER_FAILED")
            answer = self.answer_service.clean_answer(generated.get("answer", ""))
            resolved = timed("citation_validation", "citations", lambda: resolve_citations(answer, context["sources"]))
            if version == "v2" and not resolved["sources_used"] and context["sources"]:
                grounded = AnswerService.exact_source_answer(context["sources"][0])
                answer = grounded["answer"]
                resolved = resolve_citations(answer, context["sources"])
            answer = resolved["answer"]
            self._stage(progress_callback, "citations", "completed",
                        used_source_count=len(resolved["sources_used"]))
        else:
            self._stage(progress_callback, "answer", "skipped")
            self._stage(progress_callback, "citations", "skipped")

        warnings = list(resolved.get("warnings", []))
        if version == "v2" and (asks_about_vigencia(normalized_query) or
                                (solo_vigentes and vigencia_explicit)):
            warnings.append({"code": "VIGENCIA_FILTER_UNAVAILABLE", "message": "El corpus V2 no clasifica vigencia normativa; este filtro no se aplicó."})
        if rerank_warning:
            warnings.append(rerank_warning)
        formatted = self.format_results(results, modulo, context["sources"])
        timings["total"] = round((perf_counter() - total_started) * 1000, 2)
        logger.info("NovaSearch completed knowledge_version=%s status=completed result_count=%s document_types=%s empty_result=false used_sources=%s timings_ms=%s",
                    version, retrieved_count, sorted({row.get("tipo_documento") for row in results if row.get("tipo_documento")}),
                    len(resolved["sources_used"]), timings)
        self._stage(progress_callback, "completed", "completed", retrieved_count=retrieved_count,
                    reranked_count=reranked_count, used_source_count=len(resolved["sources_used"]))
        response = self._result(query, normalized_query, analysis, "completed", answer,
                            formatted, context["text"], resolved["sources_used"],
                            resolved["citations"], warnings, timings, retrieved_count, reranked_count,
                            [mention for item in results for mention in item.get("detected_legal_mentions", [])])
        response["metadata"]["knowledge_version"] = version
        return response

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
        sources_by_record = {str(source.get("chunk_id") or source.get("document_id")): source
                             for source in (context_sources or [])}
        for index, item in enumerate(resultados):
            texto = item.get("texto", "")
            resumen = (word_safe_excerpt(texto, limit=220) if item.get("unit_id") else
                       item.get("resumen") or (texto[:250] + "..." if len(texto) > 250 else texto))
            source = sources_by_record.get(str(item.get("id"))) or (
                context_sources[index] if not item.get("unit_id") and context_sources and index < len(context_sources) else None
            ) or normalize_public_source(item, excerpt=str(texto or "")[:ContextBuilder.MAX_CHARS_PER_DOCUMENT])
            formatted.append({"id": item.get("id"), "source_id": source["source_id"], "source": source,
                "detected_legal_mentions": item.get("detected_legal_mentions", []),
                "article": source.get("article"), "official_url": source.get("official_url"),
                "unit_id": item.get("unit_id"), "document_id": item.get("document_id"),
                "unit_type": item.get("unit_type"), "unit_number": item.get("unit_number"),
                "heading": item.get("heading"), "page_start": source.get("page_start"),
                "page_end": source.get("page_end"), "lexical_score": item.get("lexical_score"),
                "metadata": source.get("metadata", {}),
                "titulo": (item.get("titulo") if item.get("unit_id") else item.get("articulo"))
                          or item.get("fuente") or "Documento legal",
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
