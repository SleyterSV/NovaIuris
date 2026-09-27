import logging
import threading

from flask import Blueprint, current_app, g
from flask import jsonify
from flask import request

from app.services.search_service import SearchService, SearchPipelineError
from app.services.legal_repository import LegalSearchError
from app.models.task import TaskManager, TaskStatus
from app.utils.cancellation import OperationCancelled, check_cancelled
from app.utils.api_response import api_error


# ===============================================================
# BLUEPRINT
# ===============================================================

search_bp = Blueprint(
    "search",
    __name__
)

SEARCH_STAGES = (
    ("query_analysis", "Interpretando la consulta"),
    ("embedding", "Preparando la búsqueda semántica"),
    ("retrieval", "Buscando en el corpus jurídico"),
    ("fusion", "Consolidando resultados"),
    ("reranking", "Evaluando relevancia"),
    ("context", "Preparando fuentes"),
    ("answer", "Redactando el análisis"),
    ("citations", "Verificando referencias"),
)


def task_manager():
    manager = current_app.extensions.get("task_manager")
    if manager is None:
        manager = TaskManager()
        current_app.extensions["task_manager"] = manager
    return manager


def run_search_task(app, manager, task_id, query, filters, options):
    stages = [{"id": stage, "label": label, "status": "pending"} for stage, label in SEARCH_STAGES]
    lookup = {item["id"]: item for item in stages}

    with app.app_context():
        token = manager.cancellation_token(task_id)
        try:
            manager.update_task(task_id, status=TaskStatus.PROCESSING,
                                message="Búsqueda iniciada", progress_detail={
                                    "current_stage": "query_analysis", "stages": stages,
                                    "progress_kind": "completed_stages", "counts": {}})

            def progress(stage, status, details):
                check_cancelled(token)
                item = lookup.get(stage)
                if item:
                    item["status"] = status
                detail = manager.get_task(task_id).progress_detail or {}
                counts = dict(detail.get("counts", {}))
                timings = dict(detail.get("timings_ms", {}))
                for key in ("retrieved_count", "reranked_count", "used_source_count"):
                    if key in details:
                        counts[key] = details[key]
                if "duration_ms" in details:
                    timings[{"citations": "citation_validation"}.get(stage, stage)] = details["duration_ms"]
                done = sum(row["status"] in {"completed", "skipped", "failed"} for row in stages)
                manager.update_task(task_id, status=TaskStatus.PROCESSING,
                    progress=int(done * 100 / len(stages)), message=item["label"] if item else stage,
                    progress_detail={"current_stage": stage, "stages": [dict(row) for row in stages],
                                     "progress_kind": "completed_stages", "counts": counts,
                                     "timings_ms": timings})

            result = get_search_service().search(query=query, filtros=filters,
                generate_answer=options["generate_answer"], build_context=options["build_context"],
                use_reranker=options["use_reranker"], cancellation_token=token,
                progress_callback=progress)
            check_cancelled(token)
            for row in stages:
                if row["status"] == "pending":
                    row["status"] = "skipped"
            manager.update_task(task_id, progress_detail={"current_stage": "completed", "stages": stages,
                "progress_kind": "completed_stages", "counts": result.get("metadata", {}).get("counts", {}),
                "timings_ms": result.get("metadata", {}).get("timings_ms", {})})
            manager.complete_task(task_id, result)
        except OperationCancelled:
            manager.cancel_task(task_id)
        except LegalSearchError:
            logger.warning("NovaSearch task failed: public repository unavailable")
            manager.fail_task(task_id, {"code": "SEARCH_FAILED", "message": "No se pudo consultar el repositorio jurídico."})
        except SearchPipelineError as error:
            code = error.code if error.code in {"EMBEDDING_FAILED", "ANSWER_FAILED"} else "SEARCH_FAILED"
            logger.warning("NovaSearch task failed: stage=%s", code)
            manager.fail_task(task_id, {"code": code, "message": "No fue posible completar la búsqueda jurídica."})
        except Exception as error:
            logger.warning("NovaSearch task failed (%s)", type(error).__name__)
            manager.fail_task(task_id, {"code": "SEARCH_FAILED", "message": "No fue posible completar la búsqueda jurídica."})


def task_payload(task):
    detail = task.progress_detail or {}
    metadata = task.metadata or {}
    status = {TaskStatus.PENDING: "queued", TaskStatus.PROCESSING: "running",
              TaskStatus.COMPLETED: "completed", TaskStatus.FAILED: "failed",
              TaskStatus.CANCELLED: "cancelled"}[task.status]
    return {"task_id": task.task_id, "tool": "search", "status": status,
            "stage": detail.get("current_stage"), "progress": task.progress,
            "stages": detail.get("stages", []), "partial_result": {},
            "final_result": task.result, "warnings": (task.result or {}).get("warnings", []),
            "error": task.error, "counts": detail.get("counts", {}),
            "timings_ms": detail.get("timings_ms", {}), "metadata": metadata}


logger = logging.getLogger(
    "NovaIuris.Search"
)


@search_bp.route("/tasks", methods=["POST"])
def start_search_task():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return api_error("INVALID_SEARCH", "El cuerpo debe ser un objeto JSON válido.", g.request_id, 400)
    query = data.get("query")
    if not isinstance(query, str) or not query.strip() or len(query) > 10000:
        return api_error("INVALID_SEARCH", "Ingresa una consulta válida de hasta 10.000 caracteres.", g.request_id, 400)
    filters = data.get("filtros", {})
    if not isinstance(filters, dict):
        return api_error("INVALID_FILTERS", "Los filtros deben ser un objeto.", g.request_id, 400)
    allowed = {"modulo", "solo_vigentes"}
    if set(filters) - allowed:
        return api_error("UNSUPPORTED_FILTER", "Uno o más filtros no están disponibles.", g.request_id, 400)
    modulo = filters.get("modulo", "Todos")
    if not isinstance(modulo, str) or len(modulo) > 80:
        return api_error("INVALID_FILTERS", "El área jurídica no es válida.", g.request_id, 400)
    solo_vigentes = filters.get("solo_vigentes", True)
    if not isinstance(solo_vigentes, bool):
        return api_error("INVALID_FILTERS", "El filtro de vigencia debe ser booleano.", g.request_id, 400)
    options = {name: data.get(name, True) for name in ("generate_answer", "build_context", "use_reranker")}
    if not all(isinstance(value, bool) for value in options.values()):
        return api_error("INVALID_SEARCH", "Las opciones de búsqueda deben ser booleanas.", g.request_id, 400)
    manager = task_manager()
    manager.cleanup_old_tasks()
    task_id = manager.create_task("search", {"tool": "search", "filters": filters})
    app = current_app._get_current_object()
    threading.Thread(target=run_search_task, args=(app, manager, task_id, query.strip(),
        {"modulo": modulo, "solo_vigentes": solo_vigentes}, options), daemon=True).start()
    return jsonify(success=True, task_id=task_id, tool="search", status="queued"), 202


@search_bp.route("/tasks/<task_id>", methods=["GET"])
def search_task_status(task_id):
    task = task_manager().get_task(task_id)
    if not task or task.task_type != "search":
        return api_error("TASK_NOT_FOUND", "No se encontró la búsqueda.", g.request_id, 404)
    return jsonify(success=True, **task_payload(task))


@search_bp.route("/tasks/<task_id>/cancel", methods=["POST"])
def cancel_search_task(task_id):
    task = task_manager().get_task(task_id)
    if not task or task.task_type != "search":
        return api_error("TASK_NOT_FOUND", "No se encontró la búsqueda.", g.request_id, 404)
    task_manager().cancel_task(task_id)
    updated = task_manager().get_task(task_id)
    return jsonify(success=True, **task_payload(updated))


# ===============================================================
# SERVICIO
# ===============================================================

def get_search_service():
    from flask import current_app
    factory = current_app.config.get("SEARCH_SERVICE_FACTORY", SearchService)
    return factory()


# ===============================================================
# ENDPOINT
# ===============================================================

@search_bp.route(
    "",
    methods=["POST"]
)
def semantic_search():

    try:

        # ---------------------------------------------------------
        # VALIDAR JSON
        # ---------------------------------------------------------

        data = request.get_json(
            silent=True
        )

        if not isinstance(
            data,
            dict
        ):

            return jsonify({

                "success": False,

                "error":
                    "El cuerpo de la solicitud debe ser JSON válido."

            }), 400


        # ---------------------------------------------------------
        # OBTENER CONSULTA
        # ---------------------------------------------------------

        query = str(

            data.get(
                "query",
                ""
            )

        ).strip()


        # ---------------------------------------------------------
        # VALIDAR CONSULTA
        # ---------------------------------------------------------

        if not query:

            return jsonify({

                "success": False,

                "error":
                    "Debe ingresar una consulta."

            }), 400


        if len(query) > 10000:

            return jsonify({

                "success": False,

                "error":
                    "La consulta excede el límite permitido."

            }), 400


        # ---------------------------------------------------------
        # FILTROS
        # ---------------------------------------------------------

        filtros = data.get(
            "filtros",
            {}
        )


        if not isinstance(
            filtros,
            dict
        ):

            return jsonify({

                "success": False,

                "error":
                    "El campo 'filtros' debe ser un objeto JSON."

            }), 400

        if "modulo" in filtros and (not isinstance(filtros["modulo"], str) or len(filtros["modulo"]) > 80):
            return jsonify({"success": False, "error": {"code": "INVALID_FILTERS",
                "message": "El área jurídica no es válida."}}), 400
        if "solo_vigentes" in filtros and not isinstance(filtros["solo_vigentes"], bool):
            return jsonify({"success": False, "error": {"code": "INVALID_FILTERS",
                "message": "El filtro de vigencia debe ser booleano."}}), 400

        allowed_filters = {"modulo", "solo_vigentes"}
        if set(filtros) - allowed_filters:
            return jsonify({"success": False, "error": {"code": "UNSUPPORTED_FILTER",
                "message": "Uno o más filtros no están disponibles."}}), 400


        # ---------------------------------------------------------
        # OPCIONES DE BÚSQUEDA
        # ---------------------------------------------------------

        generate_answer = data.get(
            "generate_answer",
            True
        )

        build_context = data.get(
            "build_context",
            True
        )

        use_reranker = data.get(
            "use_reranker",
            True
        )


        # ---------------------------------------------------------
        # VALIDAR OPCIONES
        # ---------------------------------------------------------

        if not isinstance(
            generate_answer,
            bool
        ):

            return jsonify({

                "success": False,

                "error":
                    "'generate_answer' debe ser booleano."

            }), 400


        if not isinstance(
            build_context,
            bool
        ):

            return jsonify({

                "success": False,

                "error":
                    "'build_context' debe ser booleano."

            }), 400


        if not isinstance(
            use_reranker,
            bool
        ):

            return jsonify({

                "success": False,

                "error":
                    "'use_reranker' debe ser booleano."

            }), 400


        # ---------------------------------------------------------
        # LOG
        # ---------------------------------------------------------

        logger.info(

            "NovaSearch: consulta recibida | "
            "longitud=%s | filtros=%s | "
            "generate_answer=%s | "
            "build_context=%s | "
            "use_reranker=%s",

            len(query),

            {"modulo": filtros.get("modulo", "Todos"),
             "solo_vigentes": filtros.get("solo_vigentes", True)},

            generate_answer,

            build_context,

            use_reranker

        )


        # ---------------------------------------------------------
        # EJECUTAR BÚSQUEDA
        # ---------------------------------------------------------

        resultado = get_search_service().search(

            query=query,

            filtros=filtros,

            generate_answer=generate_answer,

            build_context=build_context,

            use_reranker=use_reranker

        )


        # ---------------------------------------------------------
        # DOCUMENTOS
        # ---------------------------------------------------------

        documents = resultado.get(
            "documents",
            []
        )


        # ---------------------------------------------------------
        # RESPUESTA
        # ---------------------------------------------------------

        return jsonify({

            "success": True,

            "query": resultado.get(
                "query",
                query
            ),

            "query_normalizada": resultado.get(
                "query_normalizada",
                query
            ),

            "analysis": resultado.get(
                "analysis",
                {}
            ),

            "result_status": resultado.get("result_status", "completed"),

            "sources": resultado.get("sources", []),

            "citations": resultado.get("citations", []),

            "warnings": resultado.get("warnings", []),

            "detected_legal_mentions": resultado.get("detected_legal_mentions", []),

            "metadata": resultado.get("metadata", {}),

            "answer": resultado.get(
                "answer",
                ""
            ),

            "documents": documents,

            "context": resultado.get(
                "context",
                ""
            ),

            "total": len(
                documents
            ),

            "is_fallback": not bool(
                documents
            )

        }), 200


    # ===========================================================
    # ERRORES
    # ===========================================================

    except LegalSearchError:
        logger.warning("NovaSearch public corpus unavailable")
        return jsonify({
            "success": False,
            "result_status": "search_failed",
            "error": {"code": "SEARCH_FAILED", "message": "No se pudo consultar el repositorio jurídico."}
        }), 503

    except SearchPipelineError as error:
        code = error.code if error.code in {"EMBEDDING_FAILED", "ANSWER_FAILED"} else "SEARCH_FAILED"
        return jsonify(success=False, result_status=code.lower(),
            error={"code": code, "message": "No fue posible completar la búsqueda jurídica."}), 503

    except Exception as error:
        logger.error("NovaSearch request failed error_type=%s", type(error).__name__)

        return jsonify({

            "success": False,

            "error":
                "Ocurrió un error interno al procesar la búsqueda."

        }), 500
