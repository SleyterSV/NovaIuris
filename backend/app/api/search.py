import logging

from flask import Blueprint
from flask import jsonify
from flask import request

from app.services.search_service import SearchService
from app.services.legal_repository import LegalSearchError


# ===============================================================
# BLUEPRINT
# ===============================================================

search_bp = Blueprint(
    "search",
    __name__
)


logger = logging.getLogger(
    "NovaIuris.Search"
)


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

            filtros,

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

    except Exception as error:

        logger.exception(

            "Error durante la búsqueda de NovaSearch: %s",

            error

        )

        return jsonify({

            "success": False,

            "error":
                "Ocurrió un error interno al procesar la búsqueda."

        }), 500
