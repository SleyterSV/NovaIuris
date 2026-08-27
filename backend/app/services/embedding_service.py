import os
import time
import hashlib
import logging

from typing import List

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


logger = logging.getLogger(
    "NovaIuris.Embedding"
)


class EmbeddingService:
    """
    Servicio centralizado de embeddings de Nova Iuris.

    Utilizado por:

        - NovaSearch
        - NovaCase
        - NovaCourt

    Responsabilidades:

        1. Limpieza y normalización del texto.
        2. Generación de embeddings individuales.
        3. Generación de embeddings por lote.
        4. Reintentos ante errores temporales.
        5. Cache en memoria para consultas repetidas.
        6. Configuración centralizada del modelo.

    El proveedor puede cambiarse posteriormente
    sin modificar los servicios que consumen embeddings.
    """

    DEFAULT_MODEL = "text-embedding-3-small"

    DEFAULT_RETRIES = 3

    DEFAULT_TIMEOUT = 60.0

    MAX_CACHE_SIZE = 500


    def __init__(self):

        # --------------------------------------------------------
        # CONFIGURACIÓN
        # --------------------------------------------------------

        api_key = os.getenv(
            "OPENAI_API_KEY"
        )

        if not api_key:

            raise ValueError(
                "No existe OPENAI_API_KEY."
            )


        self.MODEL = os.getenv(

            "OPENAI_EMBEDDING_MODEL",

            self.DEFAULT_MODEL

        )


        self.TIMEOUT = float(

            os.getenv(

                "OPENAI_EMBEDDING_TIMEOUT",

                self.DEFAULT_TIMEOUT

            )

        )


        # --------------------------------------------------------
        # CLIENTE OPENAI
        # --------------------------------------------------------

        self.client = OpenAI(

            api_key=api_key,

            timeout=self.TIMEOUT

        )


        # --------------------------------------------------------
        # CACHE
        # --------------------------------------------------------

        self._cache = {}


        logger.info(
            "EmbeddingService iniciado. Modelo: %s",
            self.MODEL
        )


    # ============================================================
    # LIMPIAR TEXTO
    # ============================================================

    @staticmethod
    def clean_text(
        text: str
    ) -> str:

        if text is None:

            return ""


        text = str(
            text
        )


        text = text.replace(
            "\n",
            " "
        )


        text = text.replace(
            "\r",
            " "
        )


        text = text.replace(
            "\t",
            " "
        )


        text = " ".join(
            text.split()
        )


        return text.strip()


    # ============================================================
    # GENERAR CLAVE DE CACHE
    # ============================================================

    def _cache_key(
        self,
        text: str
    ) -> str:

        normalized = self.clean_text(
            text
        )

        return hashlib.sha256(

            (
                self.MODEL
                + ":"
                + normalized
            ).encode(
                "utf-8"
            )

        ).hexdigest()


    # ============================================================
    # GENERAR EMBEDDING
    # ============================================================

    def generate_embedding(
        self,
        text: str,
        retries: int = DEFAULT_RETRIES
    ) -> List[float]:

        text = self.clean_text(
            text
        )


        if not text:

            raise ValueError(
                "No se puede generar un embedding de un texto vacío."
            )


        cache_key = self._cache_key(
            text
        )


        # --------------------------------------------------------
        # CACHE
        # --------------------------------------------------------

        cached_embedding = self._cache.get(
            cache_key
        )


        if cached_embedding is not None:

            logger.info(
                "Embedding recuperado desde cache."
            )

            return cached_embedding


        # --------------------------------------------------------
        # OPENAI
        # --------------------------------------------------------

        last_error = None


        for attempt in range(
            1,
            retries + 1
        ):

            try:

                logger.info(

                    "Generando embedding. "
                    "Intento %s/%s.",

                    attempt,

                    retries

                )


                response = (

                    self.client.embeddings.create(

                        model=self.MODEL,

                        input=[text]

                    )

                )


                embedding = (

                    response
                    .data[0]
                    .embedding

                )


                if not embedding:

                    raise RuntimeError(
                        "OpenAI devolvió un embedding vacío."
                    )


                self._store_cache(

                    cache_key,

                    embedding

                )


                logger.info(
                    "Embedding generado correctamente."
                )


                return embedding


            except Exception as error:

                last_error = error


                logger.warning(

                    "Error generando embedding "
                    "(intento %s/%s): %s",

                    attempt,

                    retries,

                    error

                )


                if attempt < retries:

                    delay = 2 ** (
                        attempt - 1
                    )

                    time.sleep(
                        delay
                    )


        logger.error(

            "No fue posible generar el embedding "
            "después de %s intentos.",

            retries

        )


        raise RuntimeError(

            "Error generando embedding: "
            f"{last_error}"

        ) from last_error


    # ============================================================
    # GENERAR EMBEDDINGS POR LOTE
    # ============================================================

    def generate_embeddings(
        self,
        texts: List[str],
        retries: int = DEFAULT_RETRIES
    ) -> List[List[float]]:

        if not texts:

            return []


        cleaned_texts = [

            self.clean_text(
                text
            )

            for text in texts

        ]


        if any(
            not text
            for text in cleaned_texts
        ):

            raise ValueError(
                "La lista contiene textos vacíos."
            )


        embeddings = [None] * len(
            cleaned_texts
        )


        missing_texts = []

        missing_indexes = []


        # --------------------------------------------------------
        # REVISAR CACHE
        # --------------------------------------------------------

        for index, text in enumerate(
            cleaned_texts
        ):

            cache_key = self._cache_key(
                text
            )


            cached = self._cache.get(
                cache_key
            )


            if cached is not None:

                embeddings[index] = cached

            else:

                missing_texts.append(
                    text
                )

                missing_indexes.append(
                    index
                )


        # --------------------------------------------------------
        # NO HAY NADA NUEVO
        # --------------------------------------------------------

        if not missing_texts:

            logger.info(
                "Todos los embeddings fueron recuperados desde cache."
            )

            return embeddings


        # --------------------------------------------------------
        # GENERACIÓN POR LOTE
        # --------------------------------------------------------

        last_error = None


        for attempt in range(
            1,
            retries + 1
        ):

            try:

                logger.info(

                    "Generando %s embeddings "
                    "en lote. Intento %s/%s.",

                    len(missing_texts),

                    attempt,

                    retries

                )


                response = (

                    self.client.embeddings.create(

                        model=self.MODEL,

                        input=missing_texts

                    )

                )


                generated = [

                    item.embedding

                    for item in response.data

                ]


                if len(generated) != len(
                    missing_texts
                ):

                    raise RuntimeError(

                        "La cantidad de embeddings "
                        "devueltos no coincide con "
                        "la cantidad solicitada."

                    )


                for index, text, embedding in zip(

                    missing_indexes,

                    missing_texts,

                    generated

                ):

                    embeddings[index] = embedding


                    self._store_cache(

                        self._cache_key(
                            text
                        ),

                        embedding

                    )


                logger.info(
                    "Embeddings generados correctamente."
                )


                return embeddings


            except Exception as error:

                last_error = error


                logger.warning(

                    "Error generando embeddings "
                    "en lote: %s",

                    error

                )


                if attempt < retries:

                    delay = 2 ** (
                        attempt - 1
                    )

                    time.sleep(
                        delay
                    )


        raise RuntimeError(

            "Error generando embeddings en lote: "
            f"{last_error}"

        ) from last_error


    # ============================================================
    # CACHE INTERNA
    # ============================================================

    def _store_cache(
        self,
        key: str,
        embedding: List[float]
    ):

        if len(
            self._cache
        ) >= self.MAX_CACHE_SIZE:

            first_key = next(
                iter(
                    self._cache
                )
            )

            del self._cache[
                first_key
            ]


        self._cache[
            key
        ] = embedding


    # ============================================================
    # CAMBIAR MODELO
    # ============================================================

    def set_model(
        self,
        model_name: str
    ):

        if not model_name:

            raise ValueError(
                "El nombre del modelo no puede estar vacío."
            )


        logger.info(

            "Cambiando modelo de embeddings: %s",

            model_name

        )


        self.MODEL = model_name


        # El cache anterior corresponde
        # al modelo anterior.

        self._cache.clear()


        logger.info(
            "Cache de embeddings limpiado."
        )