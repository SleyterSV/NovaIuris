from app.utils.cancellation import check_cancelled, OperationCancelled
from app.utils.case_contract import normalize_case_result
from uuid import uuid4
import logging

from typing import Dict
from typing import Any

from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed

from app.services.case_analyzer import CaseAnalyzer
from app.services.strategy_builder import StrategyBuilder
from app.services.search_service import SearchService
from app.services.legal_repository import LegalSearchError
from app.services.legal_argument_service import LegalArgumentService
from app.services.evidence_analyzer import EvidenceAnalyzer
from app.services.risk_analyzer import RiskAnalyzer
from app.services.counter_argument_service import CounterArgumentService
from app.services.case_report_service import CaseReportService
from app.services.case_professional import (
    build_report_document, case_facts, case_issues,
    case_timeline, final_strategy, ground_links, select_report_sources,
)
from app.services.case_execution import CaseExecutionContext, CaseExecutionMetrics, prompt_documents, research_queries
from app.services.source_contracts import normalize_case_source, normalize_public_source, resolve_citations
from app.config import Config
from flask import current_app, has_app_context

logger = logging.getLogger(
    "NovaIuris.Service.Case"
)

class CaseService:
    """
    ==========================================================

                    NOVA CASE SERVICE

    Orquestador principal de NovaCase.

    Coordina todos los módulos del sistema.

    Flujo:

        Caso

            ↓

        CaseAnalyzer

            ↓

        StrategyBuilder

            ↓

        NovaSearch

            ↓

        RiskAnalyzer

            ↓

        LegalArgumentService

            ↓

        EvidenceAnalyzer

            ↓

        CounterArgumentService

            ↓

        TimelineService

            ↓

        CaseReportService

    ==========================================================
    """

    def __init__(self):

        ########################################################
        ################ ANALISIS ##############################
        ########################################################

        self.case_analyzer = CaseAnalyzer()

        ########################################################
        ################ ESTRATEGIA ############################
        ########################################################

        self.strategy_builder = StrategyBuilder()

        ########################################################
        ################ NOVASEARCH ############################
        ########################################################

        self.search_service = SearchService()

        ########################################################
        ################ ARGUMENTOS JURÍDICOS ##################
        ########################################################

        self.argument_service = LegalArgumentService()

        ########################################################
        ################ EVIDENCIA #############################
        ########################################################

        self.evidence_analyzer = EvidenceAnalyzer()

        ########################################################
        ################ RIESGOS ###############################
        ########################################################

        self.risk_analyzer = RiskAnalyzer()

        ########################################################
        ################ CONTRAPARTE ###########################
        ########################################################

        self.counter_argument_service = CounterArgumentService()

        ########################################################
        ################ INFORME FINAL #########################
        ########################################################

        self.report_service = CaseReportService()
        self.case_corpus_repository = (
            current_app.extensions.get("case_corpus_repository") if has_app_context() else None
        )

    ####################################################################
    ######################## ANALISIS DEL CASO ##########################
    ####################################################################

    def analyze_case(
        self,
        case_text: str,
        filtros: Dict[str, Any] | None = None,
        progress_callback=None, cancellation_token=None, case_id=None, document_ids=None
    ) -> Dict:

        """
        Orquesta el flujo integral de NovaCase.

        Pipeline:

            1. Análisis jurídico
            2. Construcción de estrategia
            3. Investigación jurídica
            4. Generación de argumentos
            5. Evaluación probatoria
            6. Evaluación de riesgos
            7. Generación de contraargumentos
            8. Generación del informe final

        Las operaciones independientes se ejecutan
        en paralelo cuando sus dependencias lo permiten.
        """

        case_id = case_id or str(uuid4())
        metrics = CaseExecutionMetrics()
        execution = CaseExecutionContext(case_id)
        def stage(name, status):
            check_cancelled(cancellation_token)
            metrics.stage(name, status)
            if progress_callback:
                progress_callback(name, status)
        metrics.stage('intake', 'running')
        stage('intake', 'completed')
        if filtros is None:

            filtros = {}

        case_sources = []
        case_source_contracts = []
        analysis_case_text = case_text
        if document_ids:
            stage("documents", "running")
            if self.case_corpus_repository is None:
                raise ValueError("El corpus documental del caso no está disponible.")
            from app.services.case_corpus import CaseContextService
            from app.services.embedding_service import EmbeddingService
            documents_in_case = self.case_corpus_repository.list_documents(case_id)
            selected_ids = set(document_ids)
            manifests = {doc["document_id"]: doc for doc in documents_in_case
                         if doc.get("document_id") in selected_ids}
            execution = CaseExecutionContext(case_id, (
                (str(document_id), str(manifests.get(document_id, {}).get("document_version") or ""),
                 str(manifests.get(document_id, {}).get("sha256") or ""))
                for document_id in selected_ids))
            context_service = CaseContextService(self.case_corpus_repository, EmbeddingService())
            context_query = (case_text or "").strip() or "hechos, pretensiones, pruebas y cuestiones jurídicas"
            def load_context():
                metrics.increment("case_context_lookup_count")
                return context_service.relevant_context(
                    case_id, context_query, document_ids=document_ids,
                    top_k=Config.CASE_DOCUMENT_CONTEXT_TOP_K,
                    cancellation_token=cancellation_token,
                    operation_callback=lambda name: metrics.increment(f"{name}_call_count"))
            case_sources = execution.case_context(context_query, load_context)
            if case_sources:
                document_names = {doc["document_id"]: doc.get("filename")
                                  for doc in documents_in_case}
                case_source_contracts = [normalize_case_source({
                    **item, "case_id": case_id,
                    "filename": document_names.get(item.get("document_id")),
                }) for item in case_sources]
                excerpts = "\n\n".join(
                    f"[{source['source_id']}] {source['title']} "
                    f"página={source.get('page_start')} sección={source.get('section')}\n{source['excerpt']}"
                    for source in case_source_contracts)
                analysis_case_text = f"{case_text}\n\nDOCUMENTOS DEL MISMO CASO (fragmentos recuperados):\n{excerpts}"
            stage("documents", "completed")
        else:
            stage("documents", "skipped")

        ############################################################
        ###################### ANALIZAR CASO ########################
        ############################################################

        stage('facts', 'running')
        metrics.increment("llm_service_call_count")
        analysis = self.case_analyzer.analyze_case(

            analysis_case_text

        )

        ############################################################
        ################ VALIDAR ANALISIS ###########################
        ############################################################

        if not self.case_analyzer.validate_analysis(

            analysis

        ):

            return {

                "success": False,

                "error": "No fue posible analizar correctamente el caso."

            }

        fact_records = case_facts(analysis, case_source_contracts, case_id)
        issue_records = case_issues(analysis, case_id)
        analysis["fact_records"] = fact_records
        analysis["issue_records"] = issue_records

        ############################################################
        ################ CONSTRUIR ESTRATEGIA #######################
        ############################################################

        stage('facts', 'completed')
        stage('strategy', 'running')
        metrics.increment("llm_service_call_count")
        strategy = self.strategy_builder.build_strategy(

            analysis

        )

        ############################################################
        ################ VALIDAR ESTRATEGIA #########################
        ############################################################

        if not self.strategy_builder.validate_strategy(

            strategy

        ):

            return {

                "success": False,

                "error": "No fue posible construir la estrategia jurídica."

            }

        ############################################################
        ################### NOVASEARCH ############################
        ############################################################

        stage('strategy', 'completed')
        stage('research', 'running')
        search_queries = research_queries(strategy.get("search_queries", []), Config.CASE_RESEARCH_MAX_QUERIES)

        search_results = []


        def execute_search(query):
            check_cancelled(cancellation_token)

            try:

                logger.info(
                    "NovaSearch ejecutando consulta: %s",
                    "[redacted]"
                )

                def search_progress(name, status, details=None):
                    if status == "running" and name in {"embedding", "retrieval"}:
                        metrics.increment(f"{name}_call_count")

                def retrieve():
                    metrics.increment("research_service_call_count")
                    return self.search_service.search(
                        query=query, filtros=filtros, generate_answer=False,
                        build_context=False, use_reranker=False,
                        cancellation_token=cancellation_token,
                        progress_callback=search_progress,
                    )
                result = execution.research(query, filtros, retrieve)

                if not result:
                    return None

                return {
                    "query": query,
                    "result_status": result.get("result_status", "completed"),
                    "answer": result.get(
                        "answer",
                        ""
                    ),
                    "documents": result.get(
                        "documents",
                        []
                    ),
                    "analysis": result.get(
                        "analysis",
                        {}
                    ),
                    "sources": result.get("sources", []),
                    "warnings": result.get("warnings", []),
                }

            except OperationCancelled:
                raise
            except LegalSearchError:
                return {"query": query, "result_status": "search_failed", "documents": [],
                        "answer": "", "analysis": {}}
            except Exception as error:

                logger.error("Search stage failed error_type=%s", type(error).__name__)

                return {"query": query, "result_status": "search_failed", "documents": [],
                        "answer": "", "analysis": {}, "sources": [], "warnings": []}


        ############################################################
        ################ BÚSQUEDAS EN PARALELO #####################
        ############################################################

        if search_queries:

            max_workers = min(
                4,
                len(search_queries)
            )

            with ThreadPoolExecutor(
                max_workers=max_workers
            ) as executor:

                futures = [

                    executor.submit(
                        execute_search,
                        query
                    )

                    for query in search_queries

                ]

                for future in as_completed(
                    futures
                ):

                    result = future.result()

                    if result:

                        search_results.append(
                            result
                        )


        ############################################################
        ################ ORDENAR RESULTADOS ########################
        ############################################################

        query_order = {query: index for index, query in enumerate(search_queries)}
        search_results.sort(key=lambda item: query_order.get(item["query"], len(query_order)))

        ############################################################
        ################ ELIMINAR DUPLICADOS ########################
        ############################################################

        documentos = []

        ids = set()

        for resultado in search_results:

            for documento in resultado.get(
                "documents",
                []
            ):

                document_id = documento.get(
                    "id"
                )

                # Si no tiene ID, no descartamos el documento.
                # Esto evita perder resultados válidos.

                if document_id is not None:

                    if document_id in ids:

                        continue

                    ids.add(
                        document_id
                    )

                documentos.append(
                    documento
                )


        ############################################################
        ################ DOCUMENTOS ORDENADOS #######################
        ############################################################

        documentos.sort(

            key=lambda x:
            x.get(
                "score",
                x.get(
                    "similarity",
                    0
                )
            ),

            reverse=True

        )
        public_sources = []
        seen_public = set()
        for document in documentos:
            if not isinstance(document, dict):
                continue
            source = document.get("source")
            if not isinstance(source, dict) or source.get("source_scope") != "public":
                source = normalize_public_source(
                    document, excerpt=document.get("extracto_exacto") or document.get("texto") or "")
                document["source"] = source
            if source["source_id"] not in seen_public:
                public_sources.append(source)
                seen_public.add(source["source_id"])
        for source in case_source_contracts:
            documentos.append({"id": source["chunk_id"], "source_id": source["source_id"],
                               "tipo_documento": "case_document", "title": source["title"],
                               "texto": source["excerpt"], "source": source})
        verified_sources = public_sources + case_source_contracts
        downstream_documents = prompt_documents(documentos)
        
        ############################################################
        ################ LEGAL ARGUMENT SERVICE ####################
        ############################################################

        stage('research', 'completed')
        stage('arguments', 'running')
        metrics.increment("llm_service_call_count")
        legal_arguments = (

            self.argument_service.generate_arguments(

                analysis=analysis,

                strategy=strategy,

                documents=downstream_documents

            )

        )

        if not self.argument_service.validate_arguments(

            legal_arguments

        ):

            return {

                "success": False,

                "error": "No fue posible generar los argumentos jurídicos."

            }
        if isinstance(legal_arguments.get("main_arguments"), list):
            legal_arguments["main_arguments"] = ground_links(
                legal_arguments["main_arguments"], issue_records, fact_records,
                verified_sources, case_id)

        ############################################################
        ################ EVIDENCE + RISK ##########################
        ############################################################

        stage('arguments', 'completed')
        def analyze_evidence():
            stage("evidence", "running")
            metrics.increment("llm_service_call_count")
            try:
                result = self.evidence_analyzer.analyze(
                    analysis=analysis, strategy=strategy, arguments=legal_arguments,
                    documents=downstream_documents)
            except Exception:
                stage("evidence", "failed")
                raise
            stage("evidence", "completed")
            return result


        def analyze_risk():
            stage("risks", "running")
            metrics.increment("llm_service_call_count")
            try:
                result = self.risk_analyzer.analyze(
                    analysis=analysis, strategy=strategy, arguments=legal_arguments,
                    documents=downstream_documents)
            except Exception:
                stage("risks", "failed")
                raise
            stage("risks", "completed")
            return result


        ############################################################
        ################ EJECUCIÓN PARALELA ########################
        ############################################################

        with ThreadPoolExecutor(
            max_workers=2
        ) as executor:

            evidence_future = executor.submit(
                analyze_evidence
            )

            risk_future = executor.submit(
                analyze_risk
            )

            evidence_analysis = (
                evidence_future.result()
            )

            risk_analysis = (
                risk_future.result()
            )


        ############################################################
        ################ VALIDAR EVIDENCIA #########################
        ############################################################

        if not self.evidence_analyzer.validate_evidence(
            evidence_analysis
        ):

            return {

                "success": False,

                "error":
                    "No fue posible evaluar la evidencia del caso."

            }
        evidence_analysis.pop("evidence_score", None)
        evidence_analysis["evidence_links"] = ground_links(
            evidence_analysis.get("evidence_links", []), issue_records, fact_records,
            case_source_contracts, case_id)


        ############################################################
        ################ VALIDAR RIESGOS ###########################
        ############################################################

        if not self.risk_analyzer.validate_risk(
            risk_analysis
        ):

            return {

                "success": False,

                "error":
                    "No fue posible evaluar los riesgos del caso."

            }
        risk_analysis.pop("overall_probability", None)
        
        ############################################################
        ################ COUNTER ARGUMENTS #########################
        ############################################################

        stage('counter_arguments', 'running')
        metrics.increment("llm_service_call_count")
        counter_arguments = (

            self.counter_argument_service.generate_counterarguments(

                analysis=analysis,

                strategy=strategy,

                arguments=legal_arguments,

                evidence=evidence_analysis,

                risk=risk_analysis,

                documents=downstream_documents

            )

        )

        if not self.counter_argument_service.validate_counterarguments(

            counter_arguments

        ):

            return {

                "success": False,

                "error": "No fue posible generar los contraargumentos."

            }
        counter_arguments.pop("opponent_success_probability", None)

        ############################################################
        ################ TIMELINE #################################
        ############################################################

        stage('counter_arguments', 'completed')
        timeline = case_timeline(fact_records)
        stage('final_strategy', 'running')
        final_plan = final_strategy(
            analysis, strategy, legal_arguments, evidence_analysis,
            risk_analysis, counter_arguments)
        stage('final_strategy', 'completed')

        research_failed = any(item.get("result_status") == "search_failed"
                              for item in search_results)
        research_status = (
            "partial" if research_failed and public_sources else
            "search_failed" if research_failed else
            "not_requested" if not search_queries else
            "completed"
        )
        report_sources = select_report_sources(
            public_sources, case_source_contracts, case_id,
            limit=Config.CASE_REPORT_MAX_SOURCES)
        report, citations, cited_sources, report_warnings = "", [], [], []
        report_status, report_error = "ready", None
        report_document = None

        stage('report', 'running')
        try:
            metrics.increment("llm_service_call_count")
            candidate = self.report_service.generate_report(
                case_text=case_text,
                analysis=analysis,
                strategy=strategy,
                legal_arguments=legal_arguments,
                evidence_analysis=evidence_analysis,
                risk_analysis=risk_analysis,
                counter_arguments=counter_arguments,
                research={"status": research_status},
                sources=report_sources,
                facts=fact_records,
                issues=issue_records,
                timeline=timeline,
                final_strategy=final_plan,
                case_id=case_id,
                document_profile="analysis_report",
            )
            if not isinstance(candidate, str) or not candidate.strip():
                raise ValueError("Report content missing")
            if not self.report_service.validate_report(candidate):
                report_warnings.append({"code": "REPORT_OPTIONAL_SECTIONS_MISSING",
                                        "message": "El informe contiene secciones de presentaciÃ³n incompletas."})
        except OperationCancelled:
            raise
        except Exception as error:
            logger.error("Report generation failed error_type=%s", type(error).__name__)
            report_status = "failed"
            report_error = {"code": "REPORT_FAILED",
                            "message": "No se pudo preparar el informe jurídico. El análisis estructurado permanece disponible."}
            stage('report', 'failed')
            stage('citations', 'skipped')
        else:
            stage('report', 'completed')
            stage('citations', 'running')
            try:
                # Only validated SRC markers become interactive citations. Keep
                # ordinary numeric references intact; they may be legal numbering.
                resolved = resolve_citations(candidate, report_sources, case_id)
                report = resolved["answer"]
                citations = resolved["citations"]
                cited_sources = resolved["sources_used"]
                report_warnings.extend(resolved["warnings"])
                report_document = build_report_document(report, case_id, citations, cited_sources)
                stage('citations', 'completed')
            except OperationCancelled:
                raise
            except Exception as error:
                logger.error("Report citation validation failed error_type=%s", type(error).__name__)
                report_status = "failed"
                report_error = {"code": "REPORT_FAILED",
                                "message": "No se pudo verificar el informe. El análisis estructurado permanece disponible."}
                report, citations, cited_sources, report_document = "", [], [], None
                stage('citations', 'failed')
        if report_document is None:
            report_document = build_report_document("", case_id, [], [])

        result = {

            ########################################################
            ################ ESTADO ################################
            ########################################################

            "success": True,

            ########################################################
            ################ CASO ORIGINAL ##########################
            ########################################################

            "case": case_text,

            ########################################################
            ################ ANALISIS ###############################
            ########################################################

            "analysis": analysis,

            "analysis_summary":

                self.case_analyzer.summary(

                    analysis

                ),

            "analysis_statistics":

                self.case_analyzer.statistics(

                    analysis

                ),

            ########################################################
            ################ ESTRATEGIA #############################
            ########################################################

            "strategy": strategy,

            "strategy_summary":

                self.strategy_builder.summary(

                    strategy

                ),

            "strategy_statistics":

                self.strategy_builder.statistics(

                    strategy

                ),

            ########################################################
            ################ NOVASEARCH #############################
            ########################################################

            "research": {

                "queries":

                    search_queries,

                "documents":

                    documentos,

                "search_results":

                    search_results,

                "documents_found":

                    len(

                        documentos

                    ),

                "status": research_status,

                "warnings": ([{"code": "SEARCH_FAILED",
                    "message": "Una o más consultas de investigación no pudieron verificarse en el repositorio jurídico."}]
                    if research_failed else []),
                "sources": verified_sources,

            },

            ########################################################
            ################ FUTUROS MODULOS ########################
            ########################################################

            "risk_analysis":

                risk_analysis,

            "legal_arguments":

                legal_arguments,

            "evidence_analysis":

                evidence_analysis,

            "counter_arguments":

                counter_arguments,

            "timeline":

                timeline,

            "report": report,
            "report_document": report_document,
            "report_status": report_status,
            "report_error": report_error,
            "final_strategy": final_plan,
            "facts": fact_records,
            "issues": issue_records,
            "status": "partial" if report_status == "failed" else "completed",

        }

        result["sources"] = report_sources
        result["citations"] = citations
        result["sources_used"] = cited_sources
        result["warnings"] = result["research"]["warnings"] + report_warnings + ([report_error] if report_error else [])
        result["case_id"] = case_id
        result["document_ids"] = list(document_ids or [])
        result["research"]["case_sources"] = [item["source_reference"] for item in case_sources]
        execution_metrics = metrics.snapshot()
        result["metadata"] = {"case_id": case_id, "document_ids": list(document_ids or []),
                               "case_source_references": result["research"]["case_sources"],
                               "research_query_count": len(search_queries),
                               "retrieved_source_count": len(verified_sources),
                               "case_chunk_count": len(case_sources),
                               "report_context_source_count": len(report_sources),
                               "report_context_characters": sum(len(source["excerpt"]) for source in report_sources),
                               "input_characters": {"user_statement": len(case_text or ""),
                                    "case_context": sum(len(source["excerpt"]) for source in case_source_contracts),
                                    "research_queries": sum(len(query) for query in search_queries),
                                    "downstream_documents": sum(len(item.get("texto", "")) for item in downstream_documents)},
                               **execution_metrics}
        return normalize_case_result(result)
