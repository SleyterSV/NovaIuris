import logging
from typing import List
from typing import Dict


logger = logging.getLogger(
    "NovaIuris.Fusion"
)


class FusionService:
    """
    ==========================================================

                    NOVA FUSION ENGINE

    Fusiona múltiples rankings jurídicos.

    Actualmente soporta:

        • Vector Search

    Preparado para:

        • BM25
        • Keyword Search
        • ElasticSearch
        • PostgreSQL FullText
        • Citation Search
        • Knowledge Graph

    Será utilizado por:

        • NovaSearch

        • NovaCase

        • NovaCourt

    ==========================================================
    """

    def __init__(self):

        pass

    ####################################################################
    ######################## FUSIÓN PRINCIPAL ###########################
    ####################################################################

    def fuse(
        self,
        vector_results: List[Dict],
        keyword_results: List[Dict] | None = None,
        citation_results: List[Dict] | None = None
    ) -> List[Dict]:

        """
        Fusiona múltiples rankings en uno solo.
        """

        if keyword_results is None:
            keyword_results = []

        if citation_results is None:
            citation_results = []

        documentos = {}

        self._merge_results(
            documentos,
            vector_results,
            source="vector"
        )

        self._merge_results(
            documentos,
            keyword_results,
            source="keyword"
        )

        self._merge_results(
            documentos,
            citation_results,
            source="citation"
        )

        resultados = list(documentos.values())

        resultados.sort(

            key=lambda x: (

                x.get("fusion_score", 0),

                x.get("similarity", 0)

            ),

            reverse=True

        )

        logger.info(

            f"Fusion completada. {len(resultados)} documentos."

        )

        return resultados

    ####################################################################
    ######################## API PÚBLICA ###############################
    ####################################################################

    def merge(
        self,
        vector_results: List[Dict],
        keyword_results: List[Dict] | None = None,
        citation_results: List[Dict] | None = None
    ) -> List[Dict]:
        """
        Punto de entrada principal del FusionService.

        Actualmente es un alias de fuse(), pero permitirá
        ampliar la lógica en el futuro sin modificar
        SearchService.
        """

        return self.fuse(
            vector_results=vector_results,
            keyword_results=keyword_results,
            citation_results=citation_results
        )

    ####################################################################
    ###################### UNIFICAR RESULTADOS ##########################
    ####################################################################

    def _merge_results(
        self,
        documentos: Dict,
        resultados: List[Dict],
        source: str
    ) -> None:

        """
        Fusiona documentos provenientes de una fuente.

        Si un documento ya existe, incrementa su
        fusion_score en lugar de duplicarlo.
        """

        pesos = {

            "vector": 1.00,

            "keyword": 0.80,

            "citation": 0.90,

            "bm25": 0.85,

            "graph": 0.75

        }

        peso = pesos.get(
            source,
            1.00
        )

        for posicion, doc in enumerate(resultados):

            document_id = str(
                doc.get("id")
            )

            similarity = float(
                doc.get(
                    "similarity",
                    0
                )
            )

            # Bonificación por posición
            ranking_bonus = max(
                0,
                1 - (posicion * 0.03)
            )

            partial_score = (
                similarity
                * peso
                * ranking_bonus
            )

            if document_id not in documentos:

                nuevo = doc.copy()

                nuevo["fusion_score"] = partial_score

                nuevo["fusion_sources"] = [
                    source
                ]

                documentos[document_id] = nuevo

            else:

                documentos[document_id]["fusion_score"] += partial_score

                if source not in documentos[document_id]["fusion_sources"]:

                    documentos[document_id]["fusion_sources"].append(
                        source
                    )

    ####################################################################
    ######################## ESTADÍSTICAS ###############################
    ####################################################################

    @staticmethod
    def statistics(
        documentos: List[Dict]
    ) -> Dict:

        """
        Devuelve estadísticas del proceso de fusión.
        """

        total = len(documentos)

        if total == 0:

            return {

                "total": 0,

                "average_score": 0,

                "max_score": 0,

                "min_score": 0

            }

        scores = [

            float(

                doc.get(

                    "fusion_score",

                    0

                )

            )

            for doc in documentos

        ]

        return {

            "total": total,

            "average_score": round(

                sum(scores) / total,

                4

            ),

            "max_score": round(

                max(scores),

                4

            ),

            "min_score": round(

                min(scores),

                4

            )

        }

    ####################################################################
    ######################## DEBUG #####################################
    ####################################################################

    @staticmethod
    def print_debug(
        documentos: List[Dict]
    ) -> None:

        """
        Imprime el ranking generado.

        Solo para desarrollo.
        """

        logger.info("========== FUSION RANK ==========")

        for i, doc in enumerate(documentos, start=1):

            logger.info(

                f"{i}. "

                f"ID={doc.get('id')} | "

                f"Score={round(doc.get('fusion_score',0),4)} | "

                f"Sources={doc.get('fusion_sources',[])}"

            )

        logger.info("=================================")