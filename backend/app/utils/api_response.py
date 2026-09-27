"""Helpers for public API responses that must not expose internals."""

from flask import jsonify


def api_error(code: str, message: str, request_id: str, status: int):
    """Return the stable public error contract used by API middleware."""
    return jsonify({
        "success": False,
        "error": {"code": code, "message": message},
        # Kept at the top level for older clients that display `message`.
        "message": message,
        "request_id": request_id,
    }), status
