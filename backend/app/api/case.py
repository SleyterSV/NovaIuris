"""
NovaIuris Backend - API de análisis de casos
"""

import logging

from flask import Blueprint, jsonify, request

from app.services.case_service import CaseService


logger = logging.getLogger("NovaIuris.API.Case")


# ============================================================
# BLUEPRINT
# ============================================================

case_bp = Blueprint(
    "case",
    __name__
)


# ============================================================
# SERVICE
# ============================================================

case_service = CaseService()


# ============================================================
# ANALIZAR CASO
# ============================================================

@case_bp.route(
    "/case",
    methods=["POST"]
)
@case_bp.route(
    "/novacourt/analyze",
    methods=["POST"]
)
def analyze_case():
    """
    Endpoint principal de análisis jurídico.

    Rutas disponibles:
        POST /api/case
        POST /api/novacourt/analyze

    Recibe un caso jurídico en formato JSON y ejecuta
    el análisis integral mediante CaseService.
    """

    try:

        # ----------------------------------------------------
        # REGISTRAR SOLICITUD
        # ----------------------------------------------------

        logger.info(
            "Solicitud de análisis recibida: %s %s",
            request.method,
            request.path
        )


        # ----------------------------------------------------
        # VALIDAR JSON
        # ----------------------------------------------------

        data = request.get_json(
            silent=True
        )

        if not isinstance(data, dict):

            logger.warning(
                "Solicitud rechazada: cuerpo JSON inválido."
            )

            return jsonify({
                "success": False,
                "error": (
                    "El cuerpo de la solicitud "
                    "debe ser JSON válido."
                )
            }), 400


        # ----------------------------------------------------
        # OBTENER TEXTO DEL CASO
        # ----------------------------------------------------
        #
        # Se aceptan ambos formatos:
        #
        #   { "case_text": "..." }
        #   { "case": "..." }
        #
        # Esto mantiene compatibilidad con NovaCase/NovaCourt.
        # ----------------------------------------------------

        case_text = (
            data.get("case_text")
            or data.get("case")
            or ""
        )

        case_text = str(case_text).strip()


        # ----------------------------------------------------
        # VALIDAR EXISTENCIA DEL CASO
        # ----------------------------------------------------

        if not case_text:

            logger.warning(
                "Solicitud rechazada: no se proporcionó "
                "ningún caso jurídico."
            )

            return jsonify({
                "success": False,
                "error": (
                    "Debe proporcionar un caso jurídico."
                )
            }), 400


        # ----------------------------------------------------
        # VALIDAR LONGITUD MÍNIMA
        # ----------------------------------------------------

        if len(case_text) < 50:

            logger.warning(
                "Solicitud rechazada: caso demasiado corto "
                "(%s caracteres).",
                len(case_text)
            )

            return jsonify({
                "success": False,
                "error": (
                    "El caso debe contener información "
                    "suficiente para realizar el análisis."
                )
            }), 400


        # ----------------------------------------------------
        # VALIDAR LONGITUD MÁXIMA
        # ----------------------------------------------------

        if len(case_text) > 50000:

            logger.warning(
                "Solicitud rechazada: caso demasiado largo "
                "(%s caracteres).",
                len(case_text)
            )

            return jsonify({
                "success": False,
                "error": (
                    "El caso excede el límite permitido "
                    "de 50,000 caracteres."
                )
            }), 400


        # ----------------------------------------------------
        # LOG DEL CASO
        # ----------------------------------------------------

        logger.info(
            "Iniciando análisis jurídico. "
            "Longitud del caso: %s caracteres.",
            len(case_text)
        )


        # ----------------------------------------------------
        # EJECUTAR CASE SERVICE
        # ----------------------------------------------------

        result = case_service.analyze_case(
            case_text=case_text
        )


        # ----------------------------------------------------
        # VALIDAR RESULTADO
        # ----------------------------------------------------

        if not isinstance(result, dict):

            logger.error(
                "CaseService devolvió un resultado "
                "que no es un diccionario."
            )

            return jsonify({
                "success": False,
                "error": (
                    "NovaIuris devolvió una "
                    "respuesta inválida."
                )
            }), 500


        # ----------------------------------------------------
        # ANALISIS NO COMPLETADO
        # ----------------------------------------------------

        if not result.get("success", False):

            logger.warning(
                "El análisis jurídico no pudo completarse."
            )

            return jsonify(
                result
            ), 400


        # ----------------------------------------------------
        # ANÁLISIS EXITOSO
        # ----------------------------------------------------

        logger.info(
            "Análisis jurídico completado correctamente."
        )

        return jsonify(
            result
        ), 200


    # ========================================================
    # MANEJO DE ERRORES
    # ========================================================

    except Exception as e:

        logger.exception(
            "Error interno ejecutando el análisis jurídico."
        )

        return jsonify({
            "success": False,
            "error": (
                "Ocurrió un error interno durante "
                "el análisis del caso."
            ),
            "details": str(e)
        }), 500