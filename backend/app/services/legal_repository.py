import os
import logging

from typing import List

from dotenv import load_dotenv
from supabase import Client, create_client


load_dotenv()


logger = logging.getLogger(
    "NovaIuris.Repository"
)


class LegalSearchError(RuntimeError):
    """The public legal corpus failed, which is not an empty search."""


class LegalRepository:
    """
    Repositorio central de conocimiento jurídico.

    Toda comunicación con Supabase debe pasar por este servicio.

    Utilizado por:

        - NovaSearch
        - NovaCase
        - NovaCourt

    Responsabilidades:

        1. Conexión con Supabase.
        2. Búsqueda semántica.
        3. Validación de parámetros.
        4. Normalización de resultados.
        5. Manejo controlado de errores.

    El repositorio no contiene lógica de IA.
    Su responsabilidad es únicamente recuperar
    información jurídica desde la base de datos.
    """

    DEFAULT_LIMIT = 20

    DEFAULT_THRESHOLD = 0.30

    MAX_LIMIT = 50

    MIN_THRESHOLD = 0.0

    MAX_THRESHOLD = 1.0

    @staticmethod
    def normalize_rama(rama: str | None) -> str | None:

        if not rama:
            return None

        rama = rama.strip()

        if not rama or rama.lower() == "todos":
            return None

        mapa = {
            "laboral": "Derecho Laboral",
            "civil": "Derecho Civil",
            "penal": "Derecho Penal",
            "constitucional": "Derecho Constitucional",
            "administrativo": "Derecho Administrativo",
            "familia": "Derecho de Familia",
            "tributario": "Derecho Tributario",
            "corporativo": "Derecho Corporativo",
            "consumidor": "Derecho del Consumidor",
            "procesal civil": "Derecho Procesal Civil",
            "procesal penal": "Derecho Procesal Penal",
            "jurisprudencia": "Jurisprudencia",
        }

        return mapa.get(
            rama.lower(),
            rama
        )

    # ============================================================
    # INICIALIZACIÓN
    # ============================================================

    def __init__(self):

        url = os.getenv(
            "SUPABASE_URL"
        )

        key = os.getenv(
            "SUPABASE_KEY"
        )


        if not url:

            raise ValueError(
                "No existe SUPABASE_URL."
            )


        if not key:

            raise ValueError(
                "No existe SUPABASE_KEY."
            )


        self.supabase: Client = create_client(

            url,

            key

        )


        logger.info(
            "LegalRepository inicializado correctamente."
        )


    # ============================================================
    # BÚSQUEDA SEMÁNTICA
    # ============================================================

    def semantic_search(

        self,

        embedding: List[float],

        modulo: str = "Todos",

        limit: int = DEFAULT_LIMIT,

        threshold: float = DEFAULT_THRESHOLD

    ) -> List[dict]:

        """
        Ejecuta una búsqueda semántica mediante
        el RPC match_legal_knowledge.

        Parameters
        ----------
        embedding:
            Vector generado por EmbeddingService.

        modulo:
            Módulo o rama jurídica solicitada.
            Actualmente se conserva como parámetro
            para compatibilidad. El filtro solo se
            enviará al RPC cuando dicho RPC lo soporte.

        limit:
            Número máximo de documentos solicitados.

        threshold:
            Similaridad mínima aceptada.
        """


        # --------------------------------------------------------
        # VALIDAR EMBEDDING
        # --------------------------------------------------------

        if not embedding:

            raise ValueError(
                "El embedding no puede estar vacío."
            )


        if not isinstance(
            embedding,
            list
        ):

            raise TypeError(
                "El embedding debe ser una lista de números."
            )


        # --------------------------------------------------------
        # VALIDAR LIMIT
        # --------------------------------------------------------

        try:

            limit = int(
                limit
            )

        except (
            TypeError,
            ValueError
        ):

            limit = self.DEFAULT_LIMIT


        limit = max(

            1,

            min(
                limit,
                self.MAX_LIMIT
            )

        )


        # --------------------------------------------------------
        # VALIDAR THRESHOLD
        # --------------------------------------------------------

        try:

            threshold = float(
                threshold
            )

        except (
            TypeError,
            ValueError
        ):

            threshold = self.DEFAULT_THRESHOLD


        threshold = max(

            self.MIN_THRESHOLD,

            min(
                threshold,
                self.MAX_THRESHOLD
            )

        )

        # --------------------------------------------------------
        # PARAMETROS RPC
        # --------------------------------------------------------

        rama_normalizada = self.normalize_rama(
            modulo
        )

        params = {

            "query_embedding": embedding,

            "match_threshold": threshold,

            "match_count": limit,

            "filtro_rama": rama_normalizada,

            "filtro_tipo_documento": None,

            "filtro_jerarquia": None,

            "solo_vigentes": True

        }
        
        # --------------------------------------------------------
        # LOG
        # --------------------------------------------------------

        logger.info(

            "Búsqueda semántica iniciada | "
            "módulo=%s | límite=%s | threshold=%.2f",

            modulo,

            limit,

            threshold

        )


        # --------------------------------------------------------
        # EJECUTAR RPC
        # --------------------------------------------------------

        try:

            response = (

                self.supabase

                .rpc(

                    "match_legal_knowledge",

                    params

                )

                .execute()

            )


            resultados = (

                response.data
                or []

            )


            # ----------------------------------------------------
            # VALIDAR RESULTADOS
            # ----------------------------------------------------

            if not isinstance(
                resultados,
                list
            ):

                logger.warning(

                    "Supabase devolvió un formato inesperado."
                )

                raise LegalSearchError("Legal source search returned an invalid response")


            logger.info(

                "Búsqueda semántica completada | "
                "resultados=%s",

                len(resultados)

            )


            return resultados


        except Exception as error:
            logger.error("Legal corpus query failed error_type=%s", type(error).__name__)
            raise LegalSearchError("Legal source search failed") from error
