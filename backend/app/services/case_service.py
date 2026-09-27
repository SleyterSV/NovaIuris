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
        def stage(name, status):
            check_cancelled(cancellation_token)
            if progress_callback:
                progress_callback(name, status)
        stage('intake', 'completed')
        if filtros is None:

            filtros = {}

        case_sources = []
        analysis_case_text = case_text
        if document_ids:
            stage("documents", "running")
            if self.case_corpus_repository is None:
                raise ValueError("El corpus documental del caso no está disponible.")
            from app.services.case_corpus import CaseContextService
            from app.services.embedding_service import EmbeddingService
            from app.config import Config
            context_service = CaseContextService(self.case_corpus_repository, EmbeddingService())
            case_sources = context_service.relevant_context(
                case_id, case_text, document_ids=document_ids,
                top_k=Config.CASE_DOCUMENT_CONTEXT_TOP_K,
                cancellation_token=cancellation_token)
            if case_sources:
                excerpts = "\n\n".join(
                    f"[Fuente document_id={item['document_id']} page={item['source_reference'].get('page_start')} "
                    f"chunk_id={item['chunk_id']}]\n{item['text']}" for item in case_sources)
                analysis_case_text = f"{case_text}\n\nDOCUMENTOS DEL MISMO CASO (fragmentos recuperados):\n{excerpts}"
            stage("documents", "completed")
        else:
            stage("documents", "skipped")

        ############################################################
        ###################### ANALIZAR CASO ########################
        ############################################################

        stage('facts', 'running')
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

        ############################################################
        ################ CONSTRUIR ESTRATEGIA #######################
        ############################################################

        stage('facts', 'completed')
        stage('strategy', 'running')
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
        search_queries = list(
            dict.fromkeys(
                query.strip()
                for query in strategy.get(
                    "search_queries",
                    []
                )
                if isinstance(query, str)
                and query.strip()
            )
        )

        search_results = []


        def execute_search(query):
            check_cancelled(cancellation_token)

            try:

                logger.info(
                    "NovaSearch ejecutando consulta: %s",
                    "[redacted]"
                )

                result = self.search_service.search(

                    query=query,

                    filtros=filtros,

                    generate_answer=False,

                    build_context=False,

                    use_reranker=False,
                    cancellation_token=cancellation_token,

                )

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
                    )
                }

            except OperationCancelled:
                raise
            except LegalSearchError:
                return {"query": query, "result_status": "search_failed", "documents": [],
                        "answer": "", "analysis": {}}
            except Exception as error:

                logger.error("Search stage failed error_type=%s", type(error).__name__)

                return None


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

        search_results.sort(

            key=lambda item:
            search_queries.index(
                item["query"]
            )

            if item["query"] in search_queries
            else 999

        )

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
        
        ############################################################
        ################ LEGAL ARGUMENT SERVICE ####################
        ############################################################

        stage('research', 'completed')
        stage('arguments', 'running')
        legal_arguments = (

            self.argument_service.generate_arguments(

                analysis=analysis,

                strategy=strategy,

                documents=documentos

            )

        )

        if not self.argument_service.validate_arguments(

            legal_arguments

        ):

            return {

                "success": False,

                "error": "No fue posible generar los argumentos jurídicos."

            }

        ############################################################
        ################ EVIDENCE + RISK ##########################
        ############################################################

        stage('arguments', 'completed')
        def analyze_evidence():
            stage("evidence", "running")

            return self.evidence_analyzer.analyze(

                analysis=analysis,

                strategy=strategy,

                arguments=legal_arguments,

                documents=documentos

            )


        def analyze_risk():
            stage("risks", "running")

            return self.risk_analyzer.analyze(

                analysis=analysis,

                strategy=strategy,

                arguments=legal_arguments,

                documents=documentos

            )


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
        
        ############################################################
        ################ COUNTER ARGUMENTS #########################
        ############################################################

        stage('evidence', 'completed')
        stage('risks', 'completed')
        stage('counter_arguments', 'running')
        counter_arguments = (

            self.counter_argument_service.generate_counterarguments(

                analysis=analysis,

                strategy=strategy,

                arguments=legal_arguments,

                evidence=evidence_analysis,

                risk=risk_analysis,

                documents=documentos

            )

        )

        if not self.counter_argument_service.validate_counterarguments(

            counter_arguments

        ):

            return {

                "success": False,

                "error": "No fue posible generar los contraargumentos."

            }

        ############################################################
        ################ TIMELINE #################################
        ############################################################

        stage('counter_arguments', 'completed')
        timeline = []

        # timeline =
        #
        # self.timeline_service.build(
        #
        #     analysis
        #
        # )

        ############################################################
        ################ CASE REPORT ###############################
        ############################################################

        stage('report', 'running')
        report = (

            self.report_service.generate_report(

                case_text=case_text,

                analysis=analysis,

                strategy=strategy,

                legal_arguments=legal_arguments,

                evidence_analysis=evidence_analysis,

                risk_analysis=risk_analysis,

                counter_arguments=counter_arguments,

                research={

                    "documents": documentos,

                    "search_results": search_results

                }

            )

        )

        if not self.report_service.validate_report(

            report

        ):

            return {

                "success": False,

                "error": "No fue posible generar el informe jurídico."

            }

        ############################################################
        ###################### RESPUESTA FINAL ######################
        ############################################################

        stage('report', 'completed')
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

                    strategy.get(

                        "search_queries",

                        []

                    ),

                "documents":

                    documentos,

                "search_results":

                    search_results,

                "documents_found":

                    len(

                        documentos

                    ),

                "status": (
                    "partial" if any(item.get("result_status") == "search_failed" for item in search_results)
                    and documentos else "search_failed" if any(
                        item.get("result_status") == "search_failed" for item in search_results
                    ) else "completed"
                ),

                "warnings": ([{"code": "SEARCH_FAILED",
                    "message": "Una o más consultas de investigación no pudieron verificarse en el repositorio jurídico."}]
                    if any(item.get("result_status") == "search_failed" for item in search_results) else [])

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

            "report":

                report

        }

        from app.services.source_contracts import normalize_case_source
        public_sources = []
        for document in documentos:
            source = document.get("source") if isinstance(document, dict) else None
            if isinstance(source, dict) and source.get("source_scope") == "public":
                public_sources.append(source)
            elif isinstance(document, dict):
                from app.services.source_contracts import normalize_public_source
                public_sources.append(normalize_public_source(
                    document, excerpt=document.get("extracto_exacto", "")))
        document_names = {}
        if case_sources and self.case_corpus_repository is not None:
            document_names = {doc["document_id"]: doc.get("filename")
                              for doc in self.case_corpus_repository.list_documents(case_id)}
        result["sources"] = public_sources + [normalize_case_source({
            **item, "filename": document_names.get(item.get("document_id"))
        }) for item in case_sources]
        result["case_id"] = case_id
        result["document_ids"] = list(document_ids or [])
        result["research"]["case_sources"] = [item["source_reference"] for item in case_sources]
        result["metadata"] = {"case_id": case_id, "document_ids": list(document_ids or []),
                               "case_source_references": result["research"]["case_sources"]}
        return normalize_case_result(result)
