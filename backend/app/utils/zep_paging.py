"""
Utilidades de paginación para Zep Cloud.

Las API de nodos y relaciones de Zep utilizan paginación basada en UUID.
Este módulo centraliza la obtención completa y segura de los elementos de
un grafo, gestionando automáticamente:

- Paginación mediante cursor UUID.
- Reintentos ante errores transitorios.
- Espera exponencial entre reintentos.
- Límites de seguridad para evitar cargas excesivas.
- Detección de cursores repetidos.
- Registro detallado de eventos y errores.

El objetivo es que los servicios consumidores puedan solicitar todos los
nodos o relaciones de un grafo sin preocuparse por la lógica interna de
paginación.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from typing import Any

from zep_cloud import InternalServerError
from zep_cloud.client import Zep

from .logger import get_logger


logger = get_logger("NovaIuris.zep_paging")


# ============================================================
# CONFIGURACIÓN Y LÍMITES
# ============================================================

TAMANO_PAGINA_PREDETERMINADO = 100

MAXIMO_NODOS_PREDETERMINADO = 2000

MAXIMO_RELACIONES_PREDETERMINADO = 5000

MAXIMO_REINTENTOS_PREDETERMINADO = 3

RETRASO_REINTENTO_PREDETERMINADO = 2.0


# ============================================================
# VALIDACIÓN DE PARÁMETROS
# ============================================================

def _validar_parametros_paginacion(
    page_size: int,
    max_items: int,
    max_retries: int,
    retry_delay: float,
) -> None:
    """
    Valida los parámetros utilizados durante la paginación.

    Raises:
        ValueError: Si alguno de los parámetros tiene un valor inválido.
    """

    if page_size < 1:
        raise ValueError(
            "page_size debe ser mayor o igual a 1."
        )

    if max_items < 1:
        raise ValueError(
            "max_items debe ser mayor o igual a 1."
        )

    if max_retries < 1:
        raise ValueError(
            "max_retries debe ser mayor o igual a 1."
        )

    if retry_delay < 0:
        raise ValueError(
            "retry_delay no puede ser negativo."
        )


# ============================================================
# EJECUCIÓN DE UNA PÁGINA CON REINTENTOS
# ============================================================

def _obtener_pagina_con_reintentos(
    api_call: Callable[..., list[Any]],
    *args: Any,
    max_retries: int = MAXIMO_REINTENTOS_PREDETERMINADO,
    retry_delay: float = RETRASO_REINTENTO_PREDETERMINADO,
    page_description: str = "página",
    **kwargs: Any,
) -> list[Any]:
    """
    Ejecuta una solicitud de una página de Zep con reintentos.

    Los reintentos se aplican únicamente ante errores considerados
    transitorios, utilizando espera exponencial entre intentos.

    Args:
        api_call:
            Función de Zep que realizará la solicitud.

        *args:
            Argumentos posicionales para la función.

        max_retries:
            Número máximo de intentos.

        retry_delay:
            Tiempo inicial de espera entre reintentos.

        page_description:
            Descripción utilizada en los registros.

        **kwargs:
            Argumentos adicionales para la función.

    Returns:
        Lista de elementos obtenidos desde Zep.

    Raises:
        ValueError:
            Si max_retries o retry_delay son inválidos.

        Exception:
            Propaga el último error transitorio si se agotan los intentos.
    """

    if max_retries < 1:
        raise ValueError(
            "max_retries debe ser mayor o igual a 1."
        )

    if retry_delay < 0:
        raise ValueError(
            "retry_delay no puede ser negativo."
        )

    ultimo_error: Exception | None = None

    espera_actual = retry_delay

    for intento in range(1, max_retries + 1):

        try:

            resultado = api_call(
                *args,
                **kwargs,
            )

            return resultado or []

        except (
            ConnectionError,
            TimeoutError,
            OSError,
            InternalServerError,
        ) as error:

            ultimo_error = error

            if intento >= max_retries:

                logger.error(
                    "Error definitivo al obtener %s después de %s intentos: %s",
                    page_description,
                    max_retries,
                    str(error),
                )

                break

            logger.warning(
                "Error al obtener %s. "
                "Intento %s/%s. "
                "Nuevo intento en %.1f segundos. "
                "Detalle: %s",
                page_description,
                intento,
                max_retries,
                espera_actual,
                str(error)[:300],
            )

            if espera_actual > 0:
                time.sleep(espera_actual)

            espera_actual *= 2

    if ultimo_error is not None:
        raise ultimo_error

    raise RuntimeError(
        f"No fue posible obtener {page_description}."
    )


# ============================================================
# OBTENER UUID DE UN ELEMENTO
# ============================================================

def _obtener_uuid_elemento(
    elemento: Any,
) -> str | None:
    """
    Obtiene el UUID de un nodo o relación devuelto por Zep.

    Algunas versiones o representaciones del SDK pueden exponer el
    identificador como 'uuid_' o como 'uuid', por lo que se soportan
    ambas variantes.

    Args:
        elemento:
            Nodo o relación de Zep.

    Returns:
        UUID del elemento o None si no está disponible.
    """

    uuid = getattr(
        elemento,
        "uuid_",
        None,
    )

    if uuid:
        return str(uuid)

    uuid = getattr(
        elemento,
        "uuid",
        None,
    )

    if uuid:
        return str(uuid)

    return None


# ============================================================
# PAGINACIÓN GENÉRICA
# ============================================================

def _obtener_todos_los_elementos(
    api_call: Callable[..., list[Any]],
    graph_id: str,
    *,
    tipo_elemento: str,
    page_size: int,
    max_items: int,
    max_retries: int,
    retry_delay: float,
) -> list[Any]:
    """
    Obtiene todos los elementos de una API paginada de Zep.

    Implementa la lógica común para nodos y relaciones:

    - Solicitud paginada.
    - Cursor UUID.
    - Reintentos.
    - Límite máximo de elementos.
    - Protección contra cursores repetidos.
    - Finalización segura.

    Args:
        api_call:
            Método de Zep utilizado para recuperar los elementos.

        graph_id:
            Identificador del grafo.

        tipo_elemento:
            Nombre descriptivo del elemento para logs.

        page_size:
            Cantidad solicitada por página.

        max_items:
            Máximo total de elementos permitidos.

        max_retries:
            Máximo de intentos por página.

        retry_delay:
            Espera inicial entre reintentos.

    Returns:
        Lista completa de elementos obtenidos dentro del límite definido.
    """

    _validar_parametros_paginacion(
        page_size=page_size,
        max_items=max_items,
        max_retries=max_retries,
        retry_delay=retry_delay,
    )

    if not graph_id or not str(graph_id).strip():
        raise ValueError(
            "graph_id es obligatorio para realizar la paginación."
        )

    elementos: list[Any] = []

    cursor: str | None = None

    cursores_utilizados: set[str] = set()

    numero_pagina = 0

    logger.debug(
        "Iniciando obtención paginada de %s para el grafo %s.",
        tipo_elemento,
        graph_id,
    )

    while True:

        numero_pagina += 1

        kwargs: dict[str, Any] = {
            "limit": page_size,
        }

        if cursor is not None:
            kwargs["uuid_cursor"] = cursor

        descripcion_pagina = (
            f"{tipo_elemento}, página {numero_pagina}, "
            f"grafo={graph_id}"
        )

        lote = _obtener_pagina_con_reintentos(
            api_call,
            graph_id,
            max_retries=max_retries,
            retry_delay=retry_delay,
            page_description=descripcion_pagina,
            **kwargs,
        )

        if not lote:

            logger.debug(
                "No se encontraron más %s. "
                "Total recuperado: %s.",
                tipo_elemento,
                len(elementos),
            )

            break

        elementos.extend(lote)

        logger.debug(
            "Recuperada página %s de %s para el grafo %s. "
            "Elementos en página: %s. Total acumulado: %s.",
            numero_pagina,
            tipo_elemento,
            graph_id,
            len(lote),
            len(elementos),
        )

        # ----------------------------------------------------
        # LÍMITE DE SEGURIDAD
        # ----------------------------------------------------

        if len(elementos) >= max_items:

            elementos = elementos[:max_items]

            logger.warning(
                "Se alcanzó el límite máximo de %s (%s) "
                "para el grafo %s. "
                "La paginación se detendrá.",
                tipo_elemento,
                max_items,
                graph_id,
            )

            break

        # ----------------------------------------------------
        # ÚLTIMA PÁGINA
        # ----------------------------------------------------

        if len(lote) < page_size:

            logger.debug(
                "Se alcanzó la última página de %s "
                "para el grafo %s.",
                tipo_elemento,
                graph_id,
            )

            break

        # ----------------------------------------------------
        # OBTENER CURSOR PARA LA SIGUIENTE PÁGINA
        # ----------------------------------------------------

        siguiente_cursor = _obtener_uuid_elemento(
            lote[-1],
        )

        if siguiente_cursor is None:

            logger.warning(
                "No fue posible obtener el UUID del último %s "
                "en la página %s del grafo %s. "
                "La paginación se detendrá para evitar resultados "
                "duplicados o un ciclo infinito.",
                tipo_elemento,
                numero_pagina,
                graph_id,
            )

            break

        # ----------------------------------------------------
        # PROTECCIÓN CONTRA CURSOR REPETIDO
        # ----------------------------------------------------

        if siguiente_cursor in cursores_utilizados:

            logger.warning(
                "Se detectó un cursor repetido durante la paginación "
                "de %s para el grafo %s: %s. "
                "La operación se detendrá para evitar un ciclo infinito.",
                tipo_elemento,
                graph_id,
                siguiente_cursor,
            )

            break

        cursores_utilizados.add(
            siguiente_cursor,
        )

        cursor = siguiente_cursor

    logger.info(
        "Obtención de %s finalizada para el grafo %s. "
        "Total recuperado: %s.",
        tipo_elemento,
        graph_id,
        len(elementos),
    )

    return elementos


# ============================================================
# OBTENER TODOS LOS NODOS
# ============================================================

def fetch_all_nodes(
    client: Zep,
    graph_id: str,
    page_size: int = TAMANO_PAGINA_PREDETERMINADO,
    max_items: int = MAXIMO_NODOS_PREDETERMINADO,
    max_retries: int = MAXIMO_REINTENTOS_PREDETERMINADO,
    retry_delay: float = RETRASO_REINTENTO_PREDETERMINADO,
) -> list[Any]:
    """
    Obtiene todos los nodos disponibles de un grafo de Zep.

    La función gestiona automáticamente la paginación mediante UUID,
    los reintentos ante errores transitorios y el límite máximo de
    nodos recuperados.

    Args:
        client:
            Cliente de Zep Cloud.

        graph_id:
            Identificador del grafo.

        page_size:
            Cantidad máxima de nodos solicitados por página.

        max_items:
            Cantidad máxima total de nodos a recuperar.

        max_retries:
            Número máximo de intentos por página.

        retry_delay:
            Tiempo inicial de espera entre reintentos.

    Returns:
        Lista de nodos recuperados.
    """

    return _obtener_todos_los_elementos(
        api_call=client.graph.node.get_by_graph_id,
        graph_id=graph_id,
        tipo_elemento="nodos",
        page_size=page_size,
        max_items=max_items,
        max_retries=max_retries,
        retry_delay=retry_delay,
    )


# ============================================================
# OBTENER TODAS LAS RELACIONES
# ============================================================

def fetch_all_edges(
    client: Zep,
    graph_id: str,
    page_size: int = TAMANO_PAGINA_PREDETERMINADO,
    max_items: int = MAXIMO_RELACIONES_PREDETERMINADO,
    max_retries: int = MAXIMO_REINTENTOS_PREDETERMINADO,
    retry_delay: float = RETRASO_REINTENTO_PREDETERMINADO,
) -> list[Any]:
    """
    Obtiene todas las relaciones disponibles de un grafo de Zep.

    La función gestiona automáticamente la paginación mediante UUID,
    los reintentos ante errores transitorios y el límite máximo de
    relaciones recuperadas.

    Args:
        client:
            Cliente de Zep Cloud.

        graph_id:
            Identificador del grafo.

        page_size:
            Cantidad máxima de relaciones solicitadas por página.

        max_items:
            Cantidad máxima total de relaciones a recuperar.

        max_retries:
            Número máximo de intentos por página.

        retry_delay:
            Tiempo inicial de espera entre reintentos.

    Returns:
        Lista de relaciones recuperadas.
    """

    return _obtener_todos_los_elementos(
        api_call=client.graph.edge.get_by_graph_id,
        graph_id=graph_id,
        tipo_elemento="relaciones",
        page_size=page_size,
        max_items=max_items,
        max_retries=max_retries,
        retry_delay=retry_delay,
    )