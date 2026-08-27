"""
Servicio profesional de construcción y consulta de grafos.

Este servicio se encarga de:

1. Crear grafos Standalone en Zep.
2. Configurar dinámicamente una ontología jurídica.
3. Dividir textos extensos en fragmentos procesables.
4. Enviar los fragmentos a Zep mediante episodios.
5. Esperar el procesamiento de los episodios.
6. Obtener información y datos completos del grafo.
7. Eliminar grafos cuando sea necesario.

El servicio está preparado para Nova Iuris / NovaCourt y mantiene
compatibilidad con la estructura actual del backend.
"""

import logging
import threading
import time
import uuid

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional

from zep_cloud import EpisodeData, EntityEdgeSourceTarget
from zep_cloud.client import Zep

from ..config import Config
from ..models.task import TaskManager, TaskStatus
from ..utils.locale import get_locale, set_locale, t
from ..utils.zep_paging import fetch_all_edges, fetch_all_nodes
from ..services.text_processor import TextProcessor


logger = logging.getLogger(__name__)


# ============================================================
# CONFIGURACIÓN Y CONSTANTES
# ============================================================

NOMBRES_RESERVADOS_ZEP = {
    "uuid",
    "name",
    "group_id",
    "name_embedding",
    "summary",
    "created_at",
}


# ============================================================
# EXCEPCIONES
# ============================================================

class GraphBuilderError(Exception):
    """
    Excepción principal para errores relacionados con la
    construcción o consulta de grafos.
    """

    pass


class GraphProcessingTimeoutError(GraphBuilderError):
    """
    Se genera cuando Zep no termina de procesar todos los
    episodios dentro del tiempo máximo establecido.
    """

    pass


# ============================================================
# MODELO DE INFORMACIÓN DEL GRAFO
# ============================================================

@dataclass
class GraphInfo:
    """
    Información resumida de un grafo almacenado en Zep.
    """

    graph_id: str
    node_count: int
    edge_count: int
    entity_types: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """
        Convierte la información del grafo a un diccionario.
        """

        return {
            "graph_id": self.graph_id,
            "node_count": self.node_count,
            "edge_count": self.edge_count,
            "entity_types": sorted(self.entity_types),
        }


# ============================================================
# SERVICIO PRINCIPAL
# ============================================================

class GraphBuilderService:
    """
    Servicio responsable de construir y administrar grafos
    Standalone utilizando Zep Cloud.

    Flujo principal:

    Texto jurídico
        ↓
    División en fragmentos
        ↓
    Creación del grafo
        ↓
    Configuración de ontología
        ↓
    Creación de episodios
        ↓
    Procesamiento en Zep
        ↓
    Extracción de nodos y relaciones
        ↓
    Grafo disponible para NovaCourt
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Inicializa el servicio y el cliente de Zep.

        Args:
            api_key:
                Clave de API de Zep. Si no se proporciona,
                se utilizará Config.ZEP_API_KEY.

        Raises:
            GraphBuilderError:
                Si la clave de Zep no está configurada.
        """

        self.api_key = api_key or Config.ZEP_API_KEY

        if not self.api_key:
            raise GraphBuilderError(
                "No se encontró la configuración ZEP_API_KEY. "
                "Verifica las variables de entorno del backend."
            )

        self.client = Zep(api_key=self.api_key)
        self.task_manager = TaskManager()

        logger.info("GraphBuilderService inicializado correctamente.")


    # ========================================================
    # CONSTRUCCIÓN ASÍNCRONA
    # ========================================================

    def build_graph_async(
        self,
        text: str,
        ontology: Dict[str, Any],
        graph_name: str = "Nova Iuris Graph",
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        batch_size: int = 3,
    ) -> str:
        """
        Inicia la construcción de un grafo en segundo plano.

        Args:
            text:
                Texto que será procesado para construir el grafo.

            ontology:
                Definición de entidades y relaciones que será
                utilizada por Zep.

            graph_name:
                Nombre descriptivo del grafo.

            chunk_size:
                Tamaño máximo de cada fragmento de texto.

            chunk_overlap:
                Cantidad de texto compartido entre fragmentos.

            batch_size:
                Número de episodios enviados a Zep por lote.

        Returns:
            str:
                Identificador de la tarea creada.
        """

        self._validate_build_request(
            text=text,
            ontology=ontology,
            graph_name=graph_name,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            batch_size=batch_size,
        )

        task_id = self.task_manager.create_task(
            task_type="graph_build",
            metadata={
                "graph_name": graph_name,
                "text_length": len(text),
                "chunk_size": chunk_size,
                "chunk_overlap": chunk_overlap,
                "batch_size": batch_size,
            },
        )

        current_locale = get_locale()

        thread = threading.Thread(
            target=self._build_graph_worker,
            args=(
                task_id,
                text,
                ontology,
                graph_name,
                chunk_size,
                chunk_overlap,
                batch_size,
                current_locale,
            ),
            daemon=True,
            name=f"graph-builder-{task_id[:8]}",
        )

        thread.start()

        logger.info(
            "Tarea de construcción de grafo iniciada. "
            "task_id=%s graph_name=%s",
            task_id,
            graph_name,
        )

        return task_id


    def _build_graph_worker(
        self,
        task_id: str,
        text: str,
        ontology: Dict[str, Any],
        graph_name: str,
        chunk_size: int,
        chunk_overlap: int,
        batch_size: int,
        locale: str = "es",
    ) -> None:
        """
        Ejecuta el proceso completo de construcción del grafo
        dentro de un hilo independiente.
        """

        set_locale(locale)

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

            logger.info(
                "Iniciando construcción del grafo. task_id=%s",
                task_id,
            )


            # ------------------------------------------------
            # ETAPA 2: CREACIÓN DEL GRAFO
            # ------------------------------------------------

            graph_id = self.create_graph(graph_name)

            self.task_manager.update_task(
                task_id,
                progress=10,
                message=t(
                    "progress.graphCreated",
                    graphId=graph_id,
                ),
            )


            # ------------------------------------------------
            # ETAPA 3: CONFIGURACIÓN DE LA ONTOLOGÍA
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
            # ETAPA 4: DIVISIÓN DEL TEXTO
            # ------------------------------------------------

            chunks = TextProcessor.split_text(
                text,
                chunk_size,
                chunk_overlap,
            )

            total_chunks = len(chunks)

            if total_chunks == 0:
                raise GraphBuilderError(
                    "No fue posible generar fragmentos de texto "
                    "para construir el grafo."
                )

            self.task_manager.update_task(
                task_id,
                progress=20,
                message=t(
                    "progress.textSplit",
                    count=total_chunks,
                ),
            )


            # ------------------------------------------------
            # ETAPA 5: ENVÍO DE EPISODIOS
            # ------------------------------------------------

            episode_uuids = self.add_text_batches(
                graph_id=graph_id,
                chunks=chunks,
                batch_size=batch_size,
                progress_callback=lambda message, progress:
                    self.task_manager.update_task(
                        task_id,
                        progress=min(
                            60,
                            20 + int(progress * 40),
                        ),
                        message=message,
                    ),
            )


            # ------------------------------------------------
            # ETAPA 6: ESPERA DEL PROCESAMIENTO EN ZEP
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
                        progress=min(
                            90,
                            60 + int(progress * 30),
                        ),
                        message=message,
                    ),
            )


            # ------------------------------------------------
            # ETAPA 7: OBTENCIÓN DE INFORMACIÓN
            # ------------------------------------------------

            self.task_manager.update_task(
                task_id,
                progress=90,
                message=t("progress.fetchingGraphInfo"),
            )

            graph_info = self._get_graph_info(graph_id)


            # ------------------------------------------------
            # ETAPA 8: FINALIZACIÓN
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
                "Construcción del grafo completada. "
                "task_id=%s graph_id=%s nodes=%s edges=%s",
                task_id,
                graph_id,
                graph_info.node_count,
                graph_info.edge_count,
            )

        except Exception as error:

            logger.exception(
                "Error durante la construcción del grafo. "
                "task_id=%s",
                task_id,
            )

            error_message = str(error).strip()

            if not error_message:
                error_message = (
                    "Ocurrió un error desconocido durante "
                    "la construcción del grafo."
                )

            self.task_manager.fail_task(
                task_id,
                error_message,
            )


    # ========================================================
    # VALIDACIONES
    # ========================================================

    @staticmethod
    def _validate_build_request(
        text: str,
        ontology: Dict[str, Any],
        graph_name: str,
        chunk_size: int,
        chunk_overlap: int,
        batch_size: int,
    ) -> None:
        """
        Valida los parámetros antes de iniciar una construcción.
        """

        if not isinstance(text, str) or not text.strip():
            raise GraphBuilderError(
                "El texto para construir el grafo no puede estar vacío."
            )

        if not isinstance(ontology, dict):
            raise GraphBuilderError(
                "La ontología debe ser un diccionario válido."
            )

        if not isinstance(graph_name, str) or not graph_name.strip():
            raise GraphBuilderError(
                "El nombre del grafo no es válido."
            )

        if chunk_size <= 0:
            raise GraphBuilderError(
                "chunk_size debe ser mayor que cero."
            )

        if chunk_overlap < 0:
            raise GraphBuilderError(
                "chunk_overlap no puede ser negativo."
            )

        if chunk_overlap >= chunk_size:
            raise GraphBuilderError(
                "chunk_overlap debe ser menor que chunk_size."
            )

        if batch_size <= 0:
            raise GraphBuilderError(
                "batch_size debe ser mayor que cero."
            )


    @staticmethod
    def _safe_attribute_name(attribute_name: str) -> str:
        """
        Evita utilizar nombres reservados por Zep como
        atributos personalizados de entidades o relaciones.
        """

        normalized_name = str(attribute_name).strip()

        if not normalized_name:
            return "entity_attribute"

        if normalized_name.lower() in NOMBRES_RESERVADOS_ZEP:
            return f"entity_{normalized_name}"

        return normalized_name


    # ========================================================
    # CREACIÓN DEL GRAFO
    # ========================================================

    def create_graph(self, name: str) -> str:
        """
        Crea un nuevo Standalone Graph en Zep.

        Args:
            name:
                Nombre descriptivo del grafo.

        Returns:
            str:
                Identificador único del grafo creado.
        """

        graph_id = f"NovaIuris_{uuid.uuid4().hex[:16]}"

        self.client.graph.create(
            graph_id=graph_id,
            name=name.strip(),
            description=(
                "Grafo jurídico generado por Nova Iuris "
                "para análisis, simulación y visualización "
                "de relaciones entre actores, argumentos, "
                "evidencias y normas."
            ),
        )

        logger.info(
            "Grafo creado correctamente. graph_id=%s",
            graph_id,
        )

        return graph_id


    # ========================================================
    # CONFIGURACIÓN DE LA ONTOLOGÍA
    # ========================================================

    def set_ontology(
        self,
        graph_id: str,
        ontology: Dict[str, Any],
    ) -> None:
        """
        Configura dinámicamente la ontología de un grafo en Zep.

        La ontología puede incluir:

        - Tipos de entidades.
        - Atributos de entidades.
        - Tipos de relaciones.
        - Atributos de relaciones.
        - Restricciones de origen y destino.
        """

        import warnings

        from pydantic import Field
        from zep_cloud.external_clients.ontology import (
            EdgeModel,
            EntityModel,
            EntityText,
        )

        warnings.filterwarnings(
            "ignore",
            category=UserWarning,
            module="pydantic",
        )

        entity_types: Dict[str, Any] = {}
        edge_definitions: Dict[str, Any] = {}


        # ----------------------------------------------------
        # ENTIDADES
        # ----------------------------------------------------

        for entity_definition in ontology.get(
            "entity_types",
            [],
        ):

            if not isinstance(entity_definition, dict):
                continue

            entity_name = str(
                entity_definition.get("name", "")
            ).strip()

            if not entity_name:
                logger.warning(
                    "Se ignoró una entidad sin nombre en la ontología."
                )
                continue

            description = entity_definition.get(
                "description",
                f"Entidad jurídica de tipo {entity_name}.",
            )

            attributes: Dict[str, Any] = {
                "__doc__": description,
            }

            annotations: Dict[str, Any] = {}

            for attribute_definition in entity_definition.get(
                "attributes",
                [],
            ):

                if not isinstance(attribute_definition, dict):
                    continue

                raw_name = attribute_definition.get(
                    "name",
                    "",
                )

                attribute_name = self._safe_attribute_name(
                    raw_name,
                )

                attribute_description = attribute_definition.get(
                    "description",
                    attribute_name,
                )

                attributes[attribute_name] = Field(
                    default=None,
                    description=attribute_description,
                )

                annotations[attribute_name] = Optional[EntityText]

            attributes["__annotations__"] = annotations

            entity_class = type(
                entity_name,
                (EntityModel,),
                attributes,
            )

            entity_class.__doc__ = description

            entity_types[entity_name] = entity_class


        # ----------------------------------------------------
        # RELACIONES
        # ----------------------------------------------------

        for edge_definition in ontology.get(
            "edge_types",
            [],
        ):

            if not isinstance(edge_definition, dict):
                continue

            edge_name = str(
                edge_definition.get("name", "")
            ).strip()

            if not edge_name:
                logger.warning(
                    "Se ignoró una relación sin nombre en la ontología."
                )
                continue

            description = edge_definition.get(
                "description",
                f"Relación jurídica de tipo {edge_name}.",
            )

            attributes: Dict[str, Any] = {
                "__doc__": description,
            }

            annotations: Dict[str, Any] = {}

            for attribute_definition in edge_definition.get(
                "attributes",
                [],
            ):

                if not isinstance(attribute_definition, dict):
                    continue

                raw_name = attribute_definition.get(
                    "name",
                    "",
                )

                attribute_name = self._safe_attribute_name(
                    raw_name,
                )

                attribute_description = attribute_definition.get(
                    "description",
                    attribute_name,
                )

                attributes[attribute_name] = Field(
                    default=None,
                    description=attribute_description,
                )

                annotations[attribute_name] = Optional[str]

            attributes["__annotations__"] = annotations

            class_name = "".join(
                word.capitalize()
                for word in edge_name.split("_")
            )

            edge_class = type(
                class_name,
                (EdgeModel,),
                attributes,
            )

            edge_class.__doc__ = description


            # ------------------------------------------------
            # ORÍGENES Y DESTINOS PERMITIDOS
            # ------------------------------------------------

            source_targets = []

            for source_target in edge_definition.get(
                "source_targets",
                [],
            ):

                if not isinstance(source_target, dict):
                    continue

                source = str(
                    source_target.get(
                        "source",
                        "Entity",
                    )
                ).strip()

                target = str(
                    source_target.get(
                        "target",
                        "Entity",
                    )
                ).strip()

                source_targets.append(
                    EntityEdgeSourceTarget(
                        source=source,
                        target=target,
                    )
                )

            if source_targets:
                edge_definitions[edge_name] = (
                    edge_class,
                    source_targets,
                )


        # ----------------------------------------------------
        # ENVÍO DE LA ONTOLOGÍA A ZEP
        # ----------------------------------------------------

        if not entity_types and not edge_definitions:

            logger.warning(
                "No se encontraron entidades ni relaciones "
                "válidas para configurar en la ontología. "
                "graph_id=%s",
                graph_id,
            )

            return

        self.client.graph.set_ontology(
            graph_ids=[graph_id],
            entities=entity_types or None,
            edges=edge_definitions or None,
        )

        logger.info(
            "Ontología configurada correctamente. "
            "graph_id=%s entities=%s edges=%s",
            graph_id,
            len(entity_types),
            len(edge_definitions),
        )


    # ========================================================
    # ENVÍO DE TEXTO A ZEP
    # ========================================================

    def add_text_batches(
        self,
        graph_id: str,
        chunks: List[str],
        batch_size: int = 3,
        progress_callback: Optional[
            Callable[[str, float], None]
        ] = None,
    ) -> List[str]:
        """
        Envía los fragmentos de texto a Zep por lotes.

        Args:
            graph_id:
                Identificador del grafo.

            chunks:
                Fragmentos de texto procesados.

            batch_size:
                Número de fragmentos enviados en cada lote.

            progress_callback:
                Función opcional para informar el progreso.

        Returns:
            List[str]:
                UUID de los episodios creados.
        """

        if not chunks:
            raise GraphBuilderError(
                "No existen fragmentos de texto para enviar a Zep."
            )

        episode_uuids: List[str] = []

        total_chunks = len(chunks)

        total_batches = (
            total_chunks + batch_size - 1
        ) // batch_size


        for start_index in range(
            0,
            total_chunks,
            batch_size,
        ):

            batch_chunks = chunks[
                start_index:start_index + batch_size
            ]

            batch_number = (
                start_index // batch_size
            ) + 1


            # ------------------------------------------------
            # PROGRESO
            # ------------------------------------------------

            if progress_callback:

                progress = (
                    start_index + len(batch_chunks)
                ) / total_chunks

                progress_callback(
                    t(
                        "progress.sendingBatch",
                        current=batch_number,
                        total=total_batches,
                        chunks=len(batch_chunks),
                    ),
                    progress,
                )


            # ------------------------------------------------
            # CREACIÓN DE EPISODIOS
            # ------------------------------------------------

            episodes = [
                EpisodeData(
                    data=chunk,
                    type="text",
                )
                for chunk in batch_chunks
                if isinstance(chunk, str) and chunk.strip()
            ]

            if not episodes:
                logger.warning(
                    "El lote %s no contiene episodios válidos.",
                    batch_number,
                )
                continue


            # ------------------------------------------------
            # ENVÍO A ZEP
            # ------------------------------------------------

            try:

                batch_result = self.client.graph.add_batch(
                    graph_id=graph_id,
                    episodes=episodes,
                )

                if isinstance(batch_result, list):

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
                            episode_uuids.append(
                                str(episode_uuid)
                            )

                logger.info(
                    "Lote enviado correctamente a Zep. "
                    "graph_id=%s batch=%s/%s",
                    graph_id,
                    batch_number,
                    total_batches,
                )


                # Pequeña pausa para evitar solicitudes
                # excesivamente rápidas al servicio.
                if batch_number < total_batches:
                    time.sleep(1)


            except Exception as error:

                logger.exception(
                    "Error enviando lote a Zep. "
                    "graph_id=%s batch=%s",
                    graph_id,
                    batch_number,
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

                raise GraphBuilderError(
                    f"No fue posible enviar el lote "
                    f"{batch_number} a Zep: {error}"
                ) from error


        return episode_uuids


    # ========================================================
    # ESPERA DEL PROCESAMIENTO
    # ========================================================

    def _wait_for_episodes(
        self,
        episode_uuids: List[str],
        progress_callback: Optional[
            Callable[[str, float], None]
        ] = None,
        timeout: int = 600,
        poll_interval: int = 3,
    ) -> None:
        """
        Espera hasta que todos los episodios hayan sido
        procesados por Zep.

        Raises:
            GraphProcessingTimeoutError:
                Si el procesamiento no finaliza dentro del
                tiempo máximo establecido.
        """

        if not episode_uuids:

            if progress_callback:
                progress_callback(
                    t("progress.noEpisodesWait"),
                    1.0,
                )

            logger.warning(
                "No se recibieron UUID de episodios para esperar."
            )

            return


        start_time = time.time()

        pending_episodes = set(episode_uuids)

        completed_count = 0

        total_episodes = len(pending_episodes)


        if progress_callback:

            progress_callback(
                t(
                    "progress.waitingEpisodes",
                    count=total_episodes,
                ),
                0.0,
            )


        while pending_episodes:

            elapsed_seconds = time.time() - start_time

            if elapsed_seconds >= timeout:

                message = (
                    "Zep no terminó de procesar todos los episodios "
                    f"dentro del tiempo máximo de {timeout} segundos. "
                    f"Procesados: {completed_count}/{total_episodes}. "
                    f"Pendientes: {len(pending_episodes)}."
                )

                logger.error(message)

                if progress_callback:

                    progress_callback(
                        t(
                            "progress.episodesTimeout",
                            completed=completed_count,
                            total=total_episodes,
                        ),
                        completed_count / total_episodes,
                    )

                raise GraphProcessingTimeoutError(
                    message
                )


            # ------------------------------------------------
            # CONSULTAR ESTADO DE CADA EPISODIO
            # ------------------------------------------------

            for episode_uuid in list(pending_episodes):

                try:

                    episode = self.client.graph.episode.get(
                        uuid_=episode_uuid
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

                    # Un fallo temporal de consulta no detiene
                    # todo el proceso inmediatamente.
                    logger.warning(
                        "No fue posible consultar temporalmente "
                        "el episodio %s: %s",
                        episode_uuid,
                        error,
                    )


            # ------------------------------------------------
            # ACTUALIZAR PROGRESO
            # ------------------------------------------------

            elapsed = int(
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
                        elapsed=elapsed,
                    ),
                    progress,
                )


            if pending_episodes:

                time.sleep(
                    max(1, poll_interval)
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


        logger.info(
            "Todos los episodios fueron procesados. "
            "completed=%s total=%s",
            completed_count,
            total_episodes,
        )


    # ========================================================
    # INFORMACIÓN RESUMIDA DEL GRAFO
    # ========================================================

    def _get_graph_info(
        self,
        graph_id: str,
    ) -> GraphInfo:
        """
        Obtiene información resumida de un grafo.
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
            entity_types=sorted(entity_types),
        )


    # ========================================================
    # OBTENER DATOS COMPLETOS DEL GRAFO
    # ========================================================

    def get_graph_data(
        self,
        graph_id: str,
    ) -> Dict[str, Any]:
        """
        Obtiene todos los nodos y relaciones de un grafo.

        La respuesta está preparada para ser consumida por
        el frontend de NovaCourt y posteriormente visualizada
        mediante un componente interactivo de red.

        Returns:
            Dict[str, Any]:
                graph_id
                nodes
                edges
                node_count
                edge_count
        """

        if not graph_id or not str(graph_id).strip():
            raise GraphBuilderError(
                "Se requiere un graph_id válido."
            )


        nodes = fetch_all_nodes(
            self.client,
            graph_id,
        )

        edges = fetch_all_edges(
            self.client,
            graph_id,
        )


        # ----------------------------------------------------
        # MAPA DE NODOS
        # ----------------------------------------------------

        node_map: Dict[str, str] = {}

        for node in nodes:

            node_uuid = (
                getattr(node, "uuid_", None)
                or getattr(node, "uuid", None)
            )

            if node_uuid:

                node_map[str(node_uuid)] = (
                    getattr(node, "name", None)
                    or ""
                )


        # ----------------------------------------------------
        # NODOS
        # ----------------------------------------------------

        nodes_data: List[Dict[str, Any]] = []

        for node in nodes:

            node_uuid = (
                getattr(node, "uuid_", None)
                or getattr(node, "uuid", None)
            )

            created_at = getattr(
                node,
                "created_at",
                None,
            )

            nodes_data.append(
                {
                    "uuid": str(node_uuid)
                    if node_uuid
                    else "",

                    "name": getattr(
                        node,
                        "name",
                        "",
                    ) or "",

                    "labels": getattr(
                        node,
                        "labels",
                        None,
                    ) or [],

                    "summary": getattr(
                        node,
                        "summary",
                        "",
                    ) or "",

                    "attributes": getattr(
                        node,
                        "attributes",
                        None,
                    ) or {},

                    "created_at": (
                        str(created_at)
                        if created_at
                        else None
                    ),
                }
            )


        # ----------------------------------------------------
        # RELACIONES
        # ----------------------------------------------------

        edges_data: List[Dict[str, Any]] = []

        for edge in edges:

            edge_uuid = (
                getattr(edge, "uuid_", None)
                or getattr(edge, "uuid", None)
            )

            source_uuid = getattr(
                edge,
                "source_node_uuid",
                None,
            )

            target_uuid = getattr(
                edge,
                "target_node_uuid",
                None,
            )

            created_at = getattr(
                edge,
                "created_at",
                None,
            )

            valid_at = getattr(
                edge,
                "valid_at",
                None,
            )

            invalid_at = getattr(
                edge,
                "invalid_at",
                None,
            )

            expired_at = getattr(
                edge,
                "expired_at",
                None,
            )


            # ----------------------------------------------
            # EPISODIOS RELACIONADOS
            # ----------------------------------------------

            episodes = (
                getattr(edge, "episodes", None)
                or getattr(edge, "episode_ids", None)
            )

            if episodes and not isinstance(
                episodes,
                list,
            ):

                episodes = [
                    str(episodes)
                ]

            elif episodes:

                episodes = [
                    str(episode)
                    for episode in episodes
                ]

            else:

                episodes = []


            # ----------------------------------------------
            # TIPO DE HECHO / RELACIÓN
            # ----------------------------------------------

            fact_type = (
                getattr(
                    edge,
                    "fact_type",
                    None,
                )
                or getattr(
                    edge,
                    "name",
                    None,
                )
                or ""
            )


            edges_data.append(
                {
                    "uuid": (
                        str(edge_uuid)
                        if edge_uuid
                        else ""
                    ),

                    "name": getattr(
                        edge,
                        "name",
                        "",
                    ) or "",

                    "fact": getattr(
                        edge,
                        "fact",
                        "",
                    ) or "",

                    "fact_type": fact_type,

                    "source_node_uuid": (
                        str(source_uuid)
                        if source_uuid
                        else ""
                    ),

                    "target_node_uuid": (
                        str(target_uuid)
                        if target_uuid
                        else ""
                    ),

                    "source_node_name": node_map.get(
                        str(source_uuid),
                        "",
                    ),

                    "target_node_name": node_map.get(
                        str(target_uuid),
                        "",
                    ),

                    "attributes": getattr(
                        edge,
                        "attributes",
                        None,
                    ) or {},

                    "created_at": (
                        str(created_at)
                        if created_at
                        else None
                    ),

                    "valid_at": (
                        str(valid_at)
                        if valid_at
                        else None
                    ),

                    "invalid_at": (
                        str(invalid_at)
                        if invalid_at
                        else None
                    ),

                    "expired_at": (
                        str(expired_at)
                        if expired_at
                        else None
                    ),

                    "episodes": episodes,
                }
            )


        # ----------------------------------------------------
        # RESPUESTA FINAL
        # ----------------------------------------------------

        result = {
            "graph_id": graph_id,
            "nodes": nodes_data,
            "edges": edges_data,
            "node_count": len(nodes_data),
            "edge_count": len(edges_data),
        }

        logger.info(
            "Datos del grafo obtenidos. "
            "graph_id=%s nodes=%s edges=%s",
            graph_id,
            result["node_count"],
            result["edge_count"],
        )

        return result


    # ========================================================
    # ELIMINAR GRAFO
    # ========================================================

    def delete_graph(
        self,
        graph_id: str,
    ) -> None:
        """
        Elimina un grafo de Zep.

        Args:
            graph_id:
                Identificador del grafo que será eliminado.
        """

        if not graph_id or not str(graph_id).strip():
            raise GraphBuilderError(
                "Se requiere un graph_id válido para eliminar el grafo."
            )

        self.client.graph.delete(
            graph_id=graph_id
        )

        logger.info(
            "Grafo eliminado correctamente. graph_id=%s",
            graph_id,
        )