"""
SERVICIO DE CONSTRUCCIÓN Y CONSULTA DE GRAFOS
=============================================

Este servicio centraliza la integración entre NEXUS y Zep Cloud para:

1. Crear grafos independientes.
2. Configurar la ontología de entidades y relaciones.
3. Procesar textos extensos por bloques.
4. Enviar episodios a Zep.
5. Esperar el procesamiento de la información.
6. Obtener estadísticas del grafo.
7. Recuperar nodos y relaciones para su visualización.
8. Eliminar grafos cuando sea necesario.

El servicio es reutilizable por los diferentes módulos del sistema,
incluyendo NovaIuris y NovaCourt.

NovaCourt utilizará posteriormente los datos obtenidos para representar:

- Jueces.
- Abogados.
- Fiscalías.
- Demandantes y demandados.
- Argumentos.
- Posturas jurídicas.
- Normas y artículos.
- Jurisprudencia.
- Evidencia.
- Decisiones y conclusiones.
- Relaciones entre los diferentes elementos del proceso.
"""

import logging
import threading
import time
import traceback
import uuid

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional

from pydantic import Field

from zep_cloud import EpisodeData, EntityEdgeSourceTarget
from zep_cloud.client import Zep
from zep_cloud.external_clients.ontology import (
    EdgeModel,
    EntityModel,
    EntityText,
)

from ..config import Config
from ..models.task import TaskManager, TaskStatus
from ..utils.locale import get_locale, set_locale, t
from ..utils.zep_paging import fetch_all_edges, fetch_all_nodes
from ..services.text_processor import TextProcessor


# ============================================================
# LOGGER
# ============================================================

logger = logging.getLogger(__name__)


# ============================================================
# INFORMACIÓN RESUMIDA DEL GRAFO
# ============================================================

@dataclass
class GraphInfo:
    """
    Representa la información general de un grafo construido en Zep.
    """

    graph_id: str
    node_count: int
    edge_count: int
    entity_types: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """
        Convierte la información del grafo a un diccionario serializable.
        """

        return {
            "graph_id": self.graph_id,
            "node_count": self.node_count,
            "edge_count": self.edge_count,
            "entity_types": self.entity_types,
        }


# ============================================================
# SERVICIO PRINCIPAL
# ============================================================

class GraphBuilderService:
    """
    Servicio encargado de construir, consultar y administrar grafos
    de conocimiento mediante Zep Cloud.

    El servicio es genérico y puede utilizarse desde diferentes módulos
    del sistema.

    Ejemplos de uso:

    - NovaIuris:
      Construcción de grafos jurídicos documentales.

    - NovaCourt:
      Construcción de grafos generados durante una simulación judicial,
      relacionando actores, argumentos, evidencia, normas y decisiones.
    """

    # --------------------------------------------------------
    # CONFIGURACIÓN
    # --------------------------------------------------------

    DEFAULT_GRAPH_NAME = "NEXUS Knowledge Graph"

    RESERVED_ATTRIBUTE_NAMES = {
        "uuid",
        "uuid_",
        "name",
        "group_id",
        "name_embedding",
        "summary",
        "created_at",
        "updated_at",
    }

    def __init__(
        self,
        api_key: Optional[str] = None,
    ):
        """
        Inicializa el cliente de Zep.

        Args:
            api_key:
                Clave de acceso a Zep Cloud.
                Si no se proporciona, se utilizará la configuración
                definida en Config.ZEP_API_KEY.
        """

        self.api_key = api_key or Config.ZEP_API_KEY

        if not self.api_key:
            raise ValueError(
                "No se encontró la configuración ZEP_API_KEY. "
                "Configura una clave válida antes de utilizar el servicio de grafos."
            )

        self.client = Zep(
            api_key=self.api_key
        )

        self.task_manager = TaskManager()

        logger.info(
            "GraphBuilderService inicializado correctamente."
        )


    # ========================================================
    # CONSTRUCCIÓN ASÍNCRONA
    # ========================================================

    def build_graph_async(
        self,
        text: str,
        ontology: Dict[str, Any],
        graph_name: str = DEFAULT_GRAPH_NAME,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        batch_size: int = 3,
    ) -> str:
        """
        Inicia la construcción de un grafo en segundo plano.

        El método crea una tarea y ejecuta el procesamiento en un hilo
        independiente para evitar bloquear la solicitud HTTP.

        Args:
            text:
                Texto que será procesado para construir el grafo.

            ontology:
                Definición de entidades y relaciones que será utilizada
                para configurar la ontología del grafo.

            graph_name:
                Nombre descriptivo del grafo.

            chunk_size:
                Tamaño aproximado de cada bloque de texto.

            chunk_overlap:
                Cantidad de texto compartido entre bloques consecutivos.

            batch_size:
                Número de bloques enviados por lote a Zep.

        Returns:
            str:
                Identificador de la tarea creada.
        """

        self._validate_build_request(
            text=text,
            ontology=ontology,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            batch_size=batch_size,
        )

        normalized_name = (
            graph_name.strip()
            if isinstance(graph_name, str) and graph_name.strip()
            else self.DEFAULT_GRAPH_NAME
        )

        task_id = self.task_manager.create_task(
            task_type="graph_build",
            metadata={
                "graph_name": normalized_name,
                "text_length": len(text),
                "chunk_size": chunk_size,
                "chunk_overlap": chunk_overlap,
                "batch_size": batch_size,
            },
        )

        current_locale = get_locale()

        logger.info(
            "Iniciando construcción asíncrona del grafo. "
            "task_id=%s, graph_name=%s",
            task_id,
            normalized_name,
        )

        thread = threading.Thread(
            target=self._build_graph_worker,
            args=(
                task_id,
                text,
                ontology,
                normalized_name,
                chunk_size,
                chunk_overlap,
                batch_size,
                current_locale,
            ),
            daemon=True,
            name=f"graph-builder-{task_id}",
        )

        thread.start()

        return task_id


    # ========================================================
    # TRABAJADOR DE CONSTRUCCIÓN
    # ========================================================

    def _build_graph_worker(
        self,
        task_id: str,
        text: str,
        ontology: Dict[str, Any],
        graph_name: str,
        chunk_size: int,
        chunk_overlap: int,
        batch_size: int,
        locale: Optional[str] = None,
    ):
        """
        Ejecuta el proceso completo de construcción del grafo.

        Etapas:

        1. Crear el grafo.
        2. Configurar la ontología.
        3. Dividir el texto.
        4. Enviar los bloques a Zep.
        5. Esperar el procesamiento.
        6. Obtener las estadísticas finales.
        """

        if locale:
            set_locale(locale)

        graph_id = None

        try:

            # ------------------------------------------------
            # ETAPA 1: INICIO
            # ------------------------------------------------

            self.task_manager.update_task(
                task_id,
                status=TaskStatus.PROCESSING,
                progress=5,
                message=t("progress.startBuildingGraph"),
            )


            # ------------------------------------------------
            # ETAPA 2: CREAR EL GRAFO
            # ------------------------------------------------

            graph_id = self.create_graph(
                name=graph_name
            )

            self.task_manager.update_task(
                task_id,
                progress=10,
                message=t(
                    "progress.graphCreated",
                    graphId=graph_id,
                ),
            )

            logger.info(
                "Grafo creado correctamente. task_id=%s, graph_id=%s",
                task_id,
                graph_id,
            )


            # ------------------------------------------------
            # ETAPA 3: CONFIGURAR ONTOLOGÍA
            # ------------------------------------------------

            self.set_ontology(
                graph_id=graph_id,
                ontology=ontology,
            )

            self.task_manager.update_task(
                task_id,
                progress=15,
                message=t("progress.ontologySet"),
            )


            # ------------------------------------------------
            # ETAPA 4: DIVIDIR EL TEXTO
            # ------------------------------------------------

            chunks = TextProcessor.split_text(
                text,
                chunk_size,
                chunk_overlap,
            )

            if not chunks:
                raise ValueError(
                    "No fue posible generar bloques de texto para construir el grafo."
                )

            total_chunks = len(chunks)

            self.task_manager.update_task(
                task_id,
                progress=20,
                message=t(
                    "progress.textSplit",
                    count=total_chunks,
                ),
            )

            logger.info(
                "Texto dividido en %s bloques. graph_id=%s",
                total_chunks,
                graph_id,
            )


            # ------------------------------------------------
            # ETAPA 5: ENVIAR BLOQUES A ZEP
            # ------------------------------------------------

            episode_uuids = self.add_text_batches(
                graph_id=graph_id,
                chunks=chunks,
                batch_size=batch_size,
                progress_callback=lambda message, progress:
                    self.task_manager.update_task(
                        task_id,
                        progress=20 + int(progress * 40),
                        message=message,
                    ),
            )


            # ------------------------------------------------
            # ETAPA 6: ESPERAR PROCESAMIENTO
            # ------------------------------------------------

            self.task_manager.update_task(
                task_id,
                progress=60,
                message=t("progress.waitingZepProcess"),
            )

            self._wait_for_episodes(
                episode_uuids=episode_uuids,
                progress_callback=lambda message, progress:
                    self.task_manager.update_task(
                        task_id,
                        progress=60 + int(progress * 30),
                        message=message,
                    ),
            )


            # ------------------------------------------------
            # ETAPA 7: OBTENER INFORMACIÓN FINAL
            # ------------------------------------------------

            self.task_manager.update_task(
                task_id,
                progress=90,
                message=t("progress.fetchingGraphInfo"),
            )

            graph_info = self._get_graph_info(
                graph_id=graph_id
            )


            # ------------------------------------------------
            # ETAPA 8: COMPLETAR TAREA
            # ------------------------------------------------

            result = {
                "graph_id": graph_id,
                "graph_info": graph_info.to_dict(),
                "chunks_processed": total_chunks,
                "episodes_created": len(episode_uuids),
            }

            self.task_manager.complete_task(
                task_id,
                result,
            )

            logger.info(
                "Construcción del grafo finalizada correctamente. "
                "task_id=%s, graph_id=%s, nodes=%s, edges=%s",
                task_id,
                graph_id,
                graph_info.node_count,
                graph_info.edge_count,
            )


        except Exception as error:

            logger.exception(
                "Error durante la construcción del grafo. "
                "task_id=%s, graph_id=%s",
                task_id,
                graph_id,
            )

            error_message = (
                f"Error al construir el grafo: {str(error)}\n\n"
                f"{traceback.format_exc()}"
            )

            self.task_manager.fail_task(
                task_id,
                error_message,
            )


    # ========================================================
    # CREAR GRAFO
    # ========================================================

    def create_graph(
        self,
        name: str,
        description: Optional[str] = None,
    ) -> str:
        """
        Crea un nuevo grafo independiente en Zep.

        Args:
            name:
                Nombre descriptivo del grafo.

            description:
                Descripción opcional.

        Returns:
            str:
                Identificador único del nuevo grafo.
        """

        normalized_name = (
            name.strip()
            if isinstance(name, str) and name.strip()
            else self.DEFAULT_GRAPH_NAME
        )

        graph_id = (
            f"nexus_{uuid.uuid4().hex}"
        )

        graph_description = (
            description.strip()
            if isinstance(description, str) and description.strip()
            else (
                f"Grafo de conocimiento generado por NEXUS: "
                f"{normalized_name}"
            )
        )

        self.client.graph.create(
            graph_id=graph_id,
            name=normalized_name,
            description=graph_description,
        )

        logger.info(
            "Nuevo grafo creado. graph_id=%s, name=%s",
            graph_id,
            normalized_name,
        )

        return graph_id


    # ========================================================
    # CONFIGURAR ONTOLOGÍA
    # ========================================================

    def set_ontology(
        self,
        graph_id: str,
        ontology: Dict[str, Any],
    ):
        """
        Configura las entidades y relaciones del grafo.

        La ontología recibida debe tener una estructura similar a:

        {
            "entity_types": [
                {
                    "name": "Juez",
                    "description": "...",
                    "attributes": [...]
                }
            ],
            "edge_types": [
                {
                    "name": "presenta_argumento",
                    "description": "...",
                    "source_targets": [...]
                }
            ]
        }
        """

        if not graph_id or not graph_id.strip():
            raise ValueError(
                "Se requiere un graph_id válido para configurar la ontología."
            )

        if not isinstance(ontology, dict):
            raise ValueError(
                "La ontología debe ser un diccionario válido."
            )

        entity_definitions = (
            ontology.get("entity_types")
            or []
        )

        edge_definitions_input = (
            ontology.get("edge_types")
            or []
        )

        entity_types = self._build_entity_models(
            entity_definitions
        )

        edge_types = self._build_edge_models(
            edge_definitions_input
        )

        if not entity_types and not edge_types:
            logger.warning(
                "No se encontraron entidades ni relaciones para configurar. "
                "graph_id=%s",
                graph_id,
            )
            return

        self.client.graph.set_ontology(
            graph_ids=[graph_id],
            entities=entity_types or None,
            edges=edge_types or None,
        )

        logger.info(
            "Ontología configurada correctamente. graph_id=%s, "
            "entities=%s, edges=%s",
            graph_id,
            len(entity_types),
            len(edge_types),
        )


    # ========================================================
    # CREAR MODELOS DE ENTIDADES
    # ========================================================

    def _build_entity_models(
        self,
        entity_definitions: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Construye dinámicamente los modelos de entidades requeridos
        por la SDK de Zep.
        """

        entity_types = {}

        for entity_def in entity_definitions:

            if not isinstance(entity_def, dict):
                continue

            name = str(
                entity_def.get("name") or ""
            ).strip()

            if not name:
                logger.warning(
                    "Se omitió una entidad sin nombre."
                )
                continue

            description = str(
                entity_def.get(
                    "description",
                    f"Entidad {name}.",
                )
            )

            attributes = {
                "__doc__": description,
            }

            annotations = {}

            for attribute in (
                entity_def.get("attributes")
                or []
            ):

                if not isinstance(attribute, dict):
                    continue

                raw_name = str(
                    attribute.get("name") or ""
                ).strip()

                if not raw_name:
                    continue

                attribute_name = self._safe_attribute_name(
                    raw_name
                )

                attribute_description = str(
                    attribute.get(
                        "description",
                        raw_name,
                    )
                )

                attributes[attribute_name] = Field(
                    default=None,
                    description=attribute_description,
                )

                annotations[attribute_name] = Optional[
                    EntityText
                ]

            attributes["__annotations__"] = annotations

            entity_class = type(
                self._safe_class_name(name),
                (EntityModel,),
                attributes,
            )

            entity_class.__doc__ = description

            entity_types[name] = entity_class

        return entity_types


    # ========================================================
    # CREAR MODELOS DE RELACIONES
    # ========================================================

    def _build_edge_models(
        self,
        edge_definitions: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Construye dinámicamente los modelos de relaciones requeridos
        por la SDK de Zep.
        """

        edge_types = {}

        for edge_def in edge_definitions:

            if not isinstance(edge_def, dict):
                continue

            name = str(
                edge_def.get("name") or ""
            ).strip()

            if not name:
                logger.warning(
                    "Se omitió una relación sin nombre."
                )
                continue

            description = str(
                edge_def.get(
                    "description",
                    f"Relación {name}.",
                )
            )

            attributes = {
                "__doc__": description,
            }

            annotations = {}

            for attribute in (
                edge_def.get("attributes")
                or []
            ):

                if not isinstance(attribute, dict):
                    continue

                raw_name = str(
                    attribute.get("name") or ""
                ).strip()

                if not raw_name:
                    continue

                attribute_name = self._safe_attribute_name(
                    raw_name
                )

                attribute_description = str(
                    attribute.get(
                        "description",
                        raw_name,
                    )
                )

                attributes[attribute_name] = Field(
                    default=None,
                    description=attribute_description,
                )

                annotations[attribute_name] = Optional[str]

            attributes["__annotations__"] = annotations

            edge_class = type(
                self._safe_class_name(name),
                (EdgeModel,),
                attributes,
            )

            edge_class.__doc__ = description

            source_targets = []

            for relation in (
                edge_def.get("source_targets")
                or []
            ):

                if not isinstance(relation, dict):
                    continue

                source = str(
                    relation.get("source") or "Entity"
                )

                target = str(
                    relation.get("target") or "Entity"
                )

                source_targets.append(
                    EntityEdgeSourceTarget(
                        source=source,
                        target=target,
                    )
                )

            if source_targets:

                edge_types[name] = (
                    edge_class,
                    source_targets,
                )

            else:

                logger.warning(
                    "La relación '%s' fue omitida porque no tiene "
                    "source_targets válidos.",
                    name,
                )

        return edge_types


    # ========================================================
    # ENVIAR TEXTO POR LOTES
    # ========================================================

    def add_text_batches(
        self,
        graph_id: str,
        chunks: List[str],
        batch_size: int = 3,
        progress_callback: Optional[Callable] = None,
    ) -> List[str]:
        """
        Envía bloques de texto a Zep por lotes.

        Returns:
            Lista de identificadores de episodios creados.
        """

        if not graph_id or not graph_id.strip():
            raise ValueError(
                "Se requiere un graph_id válido."
            )

        valid_chunks = [
            chunk
            for chunk in chunks
            if isinstance(chunk, str) and chunk.strip()
        ]

        if not valid_chunks:
            raise ValueError(
                "No existen bloques de texto válidos para enviar a Zep."
            )

        episode_uuids = []

        total_chunks = len(valid_chunks)

        total_batches = (
            total_chunks + batch_size - 1
        ) // batch_size

        for start_index in range(
            0,
            total_chunks,
            batch_size,
        ):

            batch_chunks = valid_chunks[
                start_index:start_index + batch_size
            ]

            batch_number = (
                start_index // batch_size
            ) + 1

            progress = (
                start_index + len(batch_chunks)
            ) / total_chunks

            if progress_callback:

                progress_callback(
                    t(
                        "progress.sendingBatch",
                        current=batch_number,
                        total=total_batches,
                        chunks=len(batch_chunks),
                    ),
                    progress,
                )

            episodes = [
                EpisodeData(
                    data=chunk,
                    type="text",
                )
                for chunk in batch_chunks
            ]

            try:

                logger.info(
                    "Enviando lote %s de %s al grafo %s.",
                    batch_number,
                    total_batches,
                    graph_id,
                )

                batch_result = (
                    self.client.graph.add_batch(
                        graph_id=graph_id,
                        episodes=episodes,
                    )
                )

                episode_uuids.extend(
                    self._extract_episode_uuids(
                        batch_result
                    )
                )

                # Pequeña pausa para evitar enviar solicitudes
                # demasiado rápido a la API.
                if batch_number < total_batches:
                    time.sleep(1)

            except Exception as error:

                logger.exception(
                    "Error al enviar el lote %s al grafo %s.",
                    batch_number,
                    graph_id,
                )

                if progress_callback:

                    progress_callback(
                        t(
                            "progress.batchFailed",
                            batch=batch_number,
                            error=str(error),
                        ),
                        0,
                    )

                raise

        return episode_uuids


    # ========================================================
    # ESPERAR PROCESAMIENTO DE EPISODIOS
    # ========================================================

    def _wait_for_episodes(
        self,
        episode_uuids: List[str],
        progress_callback: Optional[Callable] = None,
        timeout: int = 600,
        polling_interval: int = 3,
    ):
        """
        Espera hasta que Zep procese todos los episodios.

        Si se supera el tiempo máximo, se finaliza la espera y se
        registra el estado alcanzado.
        """

        if not episode_uuids:

            logger.warning(
                "No se recibieron episodios para verificar."
            )

            if progress_callback:
                progress_callback(
                    t("progress.noEpisodesWait"),
                    1.0,
                )

            return

        start_time = time.time()

        pending_episodes = set(
            str(item)
            for item in episode_uuids
            if item
        )

        total_episodes = len(
            pending_episodes
        )

        completed_count = 0

        if progress_callback:

            progress_callback(
                t(
                    "progress.waitingEpisodes",
                    count=total_episodes,
                ),
                0,
            )

        while pending_episodes:

            elapsed_time = (
                time.time() - start_time
            )

            if elapsed_time > timeout:

                logger.warning(
                    "Tiempo máximo de espera alcanzado. "
                    "completed=%s, total=%s, pending=%s",
                    completed_count,
                    total_episodes,
                    len(pending_episodes),
                )

                if progress_callback:

                    progress_callback(
                        t(
                            "progress.episodesTimeout",
                            completed=completed_count,
                            total=total_episodes,
                        ),
                        completed_count / total_episodes,
                    )

                break

            for episode_uuid in list(
                pending_episodes
            ):

                try:

                    episode = (
                        self.client.graph.episode.get(
                            uuid_=episode_uuid
                        )
                    )

                    is_processed = bool(
                        getattr(
                            episode,
                            "processed",
                            False,
                        )
                    )

                    if is_processed:

                        pending_episodes.remove(
                            episode_uuid
                        )

                        completed_count += 1

                except Exception as error:

                    logger.debug(
                        "No fue posible verificar temporalmente "
                        "el episodio %s: %s",
                        episode_uuid,
                        str(error),
                    )

            elapsed_seconds = int(
                time.time() - start_time
            )

            progress = (
                completed_count / total_episodes
                if total_episodes > 0
                else 1.0
            )

            if progress_callback:

                progress_callback(
                    t(
                        "progress.zepProcessing",
                        completed=completed_count,
                        total=total_episodes,
                        pending=len(pending_episodes),
                        elapsed=elapsed_seconds,
                    ),
                    progress,
                )

            if pending_episodes:

                time.sleep(
                    max(
                        1,
                        polling_interval,
                    )
                )

        if progress_callback:

            progress_callback(
                t(
                    "progress.processingComplete",
                    completed=completed_count,
                    total=total_episodes,
                ),
                1.0,
            )


    # ========================================================
    # OBTENER INFORMACIÓN GENERAL DEL GRAFO
    # ========================================================

    def _get_graph_info(
        self,
        graph_id: str,
    ) -> GraphInfo:
        """
        Obtiene estadísticas generales del grafo.
        """

        nodes = fetch_all_nodes(
            self.client,
            graph_id,
        )

        edges = fetch_all_edges(
            self.client,
            graph_id,
        )

        entity_types = set()

        for node in nodes:

            labels = getattr(
                node,
                "labels",
                None,
            ) or []

            for label in labels:

                if label not in {
                    "Entity",
                    "Node",
                }:

                    entity_types.add(
                        str(label)
                    )

        return GraphInfo(
            graph_id=graph_id,
            node_count=len(nodes),
            edge_count=len(edges),
            entity_types=sorted(
                entity_types
            ),
        )


    # ========================================================
    # OBTENER DATOS COMPLETOS PARA VISUALIZACIÓN
    # ========================================================

    def get_graph_data(
        self,
        graph_id: str,
    ) -> Dict[str, Any]:
        """
        Recupera la estructura completa de un grafo.

        Esta información está diseñada para ser consumida posteriormente
        por el frontend.

        La respuesta incluye:

        - Identificador del grafo.
        - Nodos.
        - Relaciones.
        - Resumen de cada nodo.
        - Atributos.
        - Fechas.
        - Episodios relacionados.
        - Información de origen y destino de cada relación.

        NovaCourt utilizará esta información como base para:

        - Colorear nodos según el tipo de actor o información.
        - Diferenciar jueces, abogados, fiscales y partes.
        - Diferenciar argumentos, normas y evidencia.
        - Mostrar el detalle de un nodo seleccionado.
        - Mostrar el contenido en español en un panel lateral.
        - Construir una visualización interactiva de la audiencia.
        """

        if not graph_id or not graph_id.strip():
            raise ValueError(
                "Se requiere un identificador de grafo válido."
            )

        normalized_graph_id = graph_id.strip()

        logger.info(
            "Obteniendo datos del grafo %s.",
            normalized_graph_id,
        )

        nodes = fetch_all_nodes(
            self.client,
            normalized_graph_id,
        )

        edges = fetch_all_edges(
            self.client,
            normalized_graph_id,
        )


        # ----------------------------------------------------
        # MAPA DE NODOS
        # ----------------------------------------------------

        node_map = {}

        for node in nodes:

            node_uuid = self._get_object_uuid(
                node
            )

            if not node_uuid:
                continue

            node_map[node_uuid] = (
                getattr(node, "name", None)
                or ""
            )


        # ----------------------------------------------------
        # NORMALIZAR NODOS
        # ----------------------------------------------------

        nodes_data = []

        for node in nodes:

            node_uuid = self._get_object_uuid(
                node
            )

            if not node_uuid:
                continue

            labels = list(
                getattr(
                    node,
                    "labels",
                    None,
                ) or []
            )

            attributes = getattr(
                node,
                "attributes",
                None,
            ) or {}

            if not isinstance(
                attributes,
                dict,
            ):
                attributes = {
                    "value": str(
                        attributes
                    )
                }

            nodes_data.append(
                {
                    "uuid": node_uuid,
                    "name": getattr(
                        node,
                        "name",
                        None,
                    ) or "",
                    "labels": labels,
                    "summary": getattr(
                        node,
                        "summary",
                        None,
                    ) or "",
                    "attributes": attributes,
                    "created_at": self._serialize_datetime(
                        getattr(
                            node,
                            "created_at",
                            None,
                        )
                    ),
                }
            )


        # ----------------------------------------------------
        # NORMALIZAR RELACIONES
        # ----------------------------------------------------

        edges_data = []

        for edge in edges:

            edge_uuid = self._get_object_uuid(
                edge
            )

            source_node_uuid = getattr(
                edge,
                "source_node_uuid",
                None,
            )

            target_node_uuid = getattr(
                edge,
                "target_node_uuid",
                None,
            )

            edge_attributes = getattr(
                edge,
                "attributes",
                None,
            ) or {}

            if not isinstance(
                edge_attributes,
                dict,
            ):
                edge_attributes = {
                    "value": str(
                        edge_attributes
                    )
                }

            episodes = self._normalize_episodes(
                edge
            )

            edge_name = (
                getattr(edge, "name", None)
                or ""
            )

            fact = (
                getattr(edge, "fact", None)
                or ""
            )

            fact_type = (
                getattr(
                    edge,
                    "fact_type",
                    None,
                )
                or edge_name
            )

            edges_data.append(
                {
                    "uuid": edge_uuid,
                    "name": edge_name,
                    "fact": fact,
                    "fact_type": fact_type,
                    "source_node_uuid": source_node_uuid,
                    "target_node_uuid": target_node_uuid,
                    "source_node_name": node_map.get(
                        source_node_uuid,
                        "",
                    ),
                    "target_node_name": node_map.get(
                        target_node_uuid,
                        "",
                    ),
                    "attributes": edge_attributes,
                    "created_at": self._serialize_datetime(
                        getattr(
                            edge,
                            "created_at",
                            None,
                        )
                    ),
                    "valid_at": self._serialize_datetime(
                        getattr(
                            edge,
                            "valid_at",
                            None,
                        )
                    ),
                    "invalid_at": self._serialize_datetime(
                        getattr(
                            edge,
                            "invalid_at",
                            None,
                        )
                    ),
                    "expired_at": self._serialize_datetime(
                        getattr(
                            edge,
                            "expired_at",
                            None,
                        )
                    ),
                    "episodes": episodes,
                }
            )


        # ----------------------------------------------------
        # RESPUESTA NORMALIZADA
        # ----------------------------------------------------

        return {
            "graph_id": normalized_graph_id,
            "nodes": nodes_data,
            "edges": edges_data,
            "node_count": len(nodes_data),
            "edge_count": len(edges_data),
        }


    # ========================================================
    # ELIMINAR GRAFO
    # ========================================================

    def delete_graph(
        self,
        graph_id: str,
    ):
        """
        Elimina permanentemente un grafo de Zep.
        """

        if not graph_id or not graph_id.strip():
            raise ValueError(
                "Se requiere un identificador de grafo válido."
            )

        normalized_graph_id = graph_id.strip()

        self.client.graph.delete(
            graph_id=normalized_graph_id
        )

        logger.info(
            "Grafo eliminado correctamente. graph_id=%s",
            normalized_graph_id,
        )


    # ========================================================
    # MÉTODOS AUXILIARES
    # ========================================================

    def _validate_build_request(
        self,
        text: str,
        ontology: Dict[str, Any],
        chunk_size: int,
        chunk_overlap: int,
        batch_size: int,
    ):
        """
        Valida los parámetros necesarios antes de iniciar
        la construcción del grafo.
        """

        if not isinstance(
            text,
            str,
        ) or not text.strip():

            raise ValueError(
                "Se requiere un texto válido para construir el grafo."
            )

        if not isinstance(
            ontology,
            dict,
        ):

            raise ValueError(
                "La ontología debe ser un diccionario válido."
            )

        if chunk_size <= 0:

            raise ValueError(
                "chunk_size debe ser mayor que cero."
            )

        if chunk_overlap < 0:

            raise ValueError(
                "chunk_overlap no puede ser negativo."
            )

        if chunk_overlap >= chunk_size:

            raise ValueError(
                "chunk_overlap debe ser menor que chunk_size."
            )

        if batch_size <= 0:

            raise ValueError(
                "batch_size debe ser mayor que cero."
            )


    def _safe_attribute_name(
        self,
        attribute_name: str,
    ) -> str:
        """
        Evita conflictos con nombres reservados por Zep o Pydantic.
        """

        normalized_name = (
            str(attribute_name)
            .strip()
            .replace(" ", "_")
            .replace("-", "_")
        )

        if normalized_name.lower() in {
            item.lower()
            for item in self.RESERVED_ATTRIBUTE_NAMES
        }:

            return (
                f"entity_{normalized_name}"
            )

        return normalized_name


    def _safe_class_name(
        self,
        name: str,
    ) -> str:
        """
        Genera un nombre seguro para una clase dinámica.
        """

        parts = (
            str(name)
            .replace("-", "_")
            .replace(" ", "_")
            .split("_")
        )

        result = "".join(
            part[:1].upper() + part[1:]
            for part in parts
            if part
        )

        return result or "NexusEntity"


    @staticmethod
    def _extract_episode_uuids(
        batch_result: Any,
    ) -> List[str]:
        """
        Extrae los identificadores de episodios devueltos por Zep.
        """

        if not batch_result:
            return []

        if not isinstance(
            batch_result,
            list,
        ):
            batch_result = [
                batch_result
            ]

        result = []

        for episode in batch_result:

            episode_uuid = (
                getattr(
                    episode,
                    "uuid_",
                    None,
                )
                or getattr(
                    episode,
                    "uuid",
                    None,
                )
            )

            if episode_uuid:
                result.append(
                    str(episode_uuid)
                )

        return result


    @staticmethod
    def _get_object_uuid(
        obj: Any,
    ) -> Optional[str]:
        """
        Obtiene de forma segura el UUID de un objeto de Zep.
        """

        value = (
            getattr(
                obj,
                "uuid_",
                None,
            )
            or getattr(
                obj,
                "uuid",
                None,
            )
        )

        return (
            str(value)
            if value
            else None
        )


    @staticmethod
    def _serialize_datetime(
        value: Any,
    ) -> Optional[str]:
        """
        Convierte una fecha a un formato serializable.
        """

        if value is None:
            return None

        return str(value)


    @staticmethod
    def _normalize_episodes(
        edge: Any,
    ) -> List[str]:
        """
        Normaliza los episodios asociados a una relación.
        """

        episodes = (
            getattr(
                edge,
                "episodes",
                None,
            )
            or getattr(
                edge,
                "episode_ids",
                None,
            )
            or []
        )

        if not isinstance(
            episodes,
            list,
        ):
            episodes = [
                episodes
            ]

        return [
            str(episode)
            for episode in episodes
            if episode is not None
        ]