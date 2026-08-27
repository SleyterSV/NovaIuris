import logging

from typing import Dict
from typing import Any

from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed

from app.services.case_analyzer import CaseAnalyzer
from app.services.strategy_builder import StrategyBuilder
from app.services.search_service import SearchService
from app.services.legal_argument_service import LegalArgumentService
from app.services.evidence_analyzer import EvidenceAnalyzer
from app.services.risk_analyzer import RiskAnalyzer
from app.services.counter_argument_service import CounterArgumentService
from app.services.case_report_service import CaseReportService

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

    ####################################################################
    ######################## ANALISIS DEL CASO ##########################
    ####################################################################

    def analyze_case(
        self,
        case_text: str,
        filtros: Dict[str, Any] | None = None
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

        if filtros is None:

            filtros = {}

        ############################################################
        ###################### ANALIZAR CASO ########################
        ############################################################

        analysis = self.case_analyzer.analyze_case(

            case_text

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

            try:

                logger.info(
                    "NovaSearch ejecutando consulta: %s",
                    query[:100]
                )

                result = self.search_service.search(

                    query=query,

                    filtros=filtros,

                    generate_answer=False,

                    build_context=False,

                    use_reranker=False,

                )

                if not result:
                    return None

                return {
                    "query": query,
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

            except Exception as error:

                logger.exception(
                    "Error ejecutando NovaSearch para query: %s",
                    query
                )

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

        def analyze_evidence():

            return self.evidence_analyzer.analyze(

                analysis=analysis,

                strategy=strategy,

                arguments=legal_arguments,

                documents=documentos

            )


        def analyze_risk():

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

        return {

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

                    )

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
