import logging

from flask import Blueprint
from flask import jsonify
from flask import request

from app.services.case_service import CaseService


logger = logging.getLogger(
    "NovaIuris.API.Case"
)


case_bp = Blueprint(
    "case",
    __name__
)


case_service = CaseService()


# ============================================================
# ANALIZAR CASO
# ============================================================

@case_bp.route(
    "/case",
    methods=["POST"]
)
def analyze_case():

    """
    Endpoint principal de NovaCase.

    Recibe un caso jurídico y ejecuta el
    análisis integral mediante CaseService.
    """

    try:

        # ----------------------------------------------------
        # VALIDAR JSON
        # ----------------------------------------------------

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


        # ----------------------------------------------------
        # OBTENER CASO
        # ----------------------------------------------------

        case_text = str(

            data.get(
                "case",
                ""
            )

        ).strip()


        # ----------------------------------------------------
        # VALIDAR CASO
        # ----------------------------------------------------

        if not case_text:

            return jsonify({

                "success": False,

                "error":
                    "Debe proporcionar un caso jurídico."

            }), 400


        if len(case_text) < 50:

            return jsonify({

                "success": False,

                "error":
                    "El caso debe contener información suficiente para realizar el análisis."

            }), 400


        # Límite razonable para evitar solicitudes
        # accidentalmente gigantes durante desarrollo.

        if len(case_text) > 50000:

            return jsonify({

                "success": False,

                "error":
                    "El caso excede el límite permitido de caracteres."

            }), 400


        # ----------------------------------------------------
        # LOG
        # ----------------------------------------------------

        logger.info(
            "NovaCase: caso recibido (%s caracteres).",
            len(case_text)
        )


        # ----------------------------------------------------
        # EJECUTAR NOVACASE
        # ----------------------------------------------------

        result = case_service.analyze_case(

            case_text=case_text

        )


        # ----------------------------------------------------
        # VALIDAR RESULTADO
        # ----------------------------------------------------

        if not isinstance(
            result,
            dict
        ):

            logger.error(
                "CaseService devolvió un resultado inválido."
            )

            return jsonify({

                "success": False,

                "error":
                    "NovaCase devolvió una respuesta inválida."

            }), 500


        if not result.get(
            "success",
            False
        ):

            logger.warning(
                "NovaCase no pudo completar el análisis."
            )

            return jsonify(
                result
            ), 400


        # ----------------------------------------------------
        # RESPUESTA EXITOSA
        # ----------------------------------------------------

        logger.info(
            "NovaCase finalizó correctamente."
        )

        return jsonify(
            result
        ), 200


    # ========================================================
    # ERRORES
    # ========================================================

    except Exception as e:

        logger.exception(
            "Error ejecutando NovaCase."
        )

        return jsonify({

            "success": False,

            "error":
                "Ocurrió un error interno durante el análisis del caso.",

            "details":
                str(e)

        }), 500