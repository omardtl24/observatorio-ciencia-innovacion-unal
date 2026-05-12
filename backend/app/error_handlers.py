from flask import jsonify, request # type: ignore
from werkzeug.exceptions import HTTPException # type: ignore

from app.domain.exceptions import DomainError


def register_app_logger(app):
    @app.before_request
    def log_request():
        app.logger.info(f"Request: {request.method} {request.path}")

    @app.after_request
    def log_response(response):
        status = response.status_code
        if status >= 400:
            message = response.get_data(as_text=True)
            app.logger.error(
                f"Response: {response.status} {request.method} {request.path} | Message: {message}"
            )
        else:
            app.logger.info(
                f"Response: {response.status} {request.method} {request.path}"
            )
        return response

def register_jwt_error_handlers(jwt, app):
    @jwt.unauthorized_loader
    def handle_jwt_missing_token(reason):
        app.logger.error(f"JWT unauthorized: {reason}")

        msg = "Debes iniciar sesión para continuar"
        if reason:
            low = str(reason).lower()
            if "missing" in low and "authorization" in low:
                msg = "Falta la cabecera 'Authorization'. Incluye 'Authorization: Bearer <token>'"
            elif "missing" in low and "cookie" in low:
                msg = "Falta la cookie de sesión. Inicia sesión para continuar."
            elif "query" in low or "param" in low:
                msg = "Falta un parámetro requerido en la URL."

        return jsonify({
            "code": "unauthorized",
            "message": msg,
            "details": None,
        }), 401

    @jwt.invalid_token_loader
    def handle_jwt_invalid_token(reason):
        app.logger.error(f"JWT invalid: {reason}")

        msg = "La sesión no es válida. Inicia sesión nuevamente"
        if reason:
            low = str(reason).lower()
            if "signature" in low or "invalid" in low or "decode" in low:
                msg = "Token inválido o manipulado. Inicia sesión nuevamente."
            elif "expired" in low:
                msg = "La sesión expiró. Inicia sesión nuevamente."

        return jsonify({
            "code": "invalid_token",
            "message": msg,
            "details": None,
        }), 401

    @jwt.expired_token_loader
    def handle_jwt_expired_token(jwt_header, jwt_payload):
        app.logger.error("JWT expired")
        return jsonify({
            "code": "token_expired",
            "message": "La sesión expiró. Inicia sesión nuevamente",
            "details": None,
        }), 401

    @jwt.needs_fresh_token_loader
    def handle_jwt_needs_fresh_token(jwt_header, jwt_payload):
        app.logger.error("JWT needs fresh token")
        return jsonify({
            "code": "fresh_token_required",
            "message": "Por seguridad, vuelve a iniciar sesión",
            "details": None,
        }), 401

    @jwt.revoked_token_loader
    def handle_jwt_revoked_token(jwt_header, jwt_payload):
        app.logger.error("JWT revoked")
        return jsonify({
            "code": "token_revoked",
            "message": "La sesión fue cerrada. Inicia sesión nuevamente",
            "details": None,
        }), 401


def register_api_error_handlers(app):
    @app.errorhandler(DomainError)
    def handle_domain_error(error):
        return jsonify(error.to_dict()), error.code or 400

    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        # Map common HTTP statuses to friendlier Spanish messages
        status = error.code or 500
        if status == 404:
            message = "No se encontró el recurso solicitado"
        elif status == 403:
            message = "No tienes permiso para acceder a este recurso"
        elif status == 401:
            message = "No estás autorizado. Autentícate para continuar"
        else:
            message = error.description or "Ocurrió un error al procesar la solicitud"

        return jsonify({
            "code": "http_error",
            "message": message,
            "details": None,
        }), status

    @app.errorhandler(Exception)
    def handle_unexpected_exception(error):
        app.logger.exception("Unhandled exception", exc_info=error)
        return jsonify({
            "code": "internal_server_error",
            "message": "Ocurrió un error interno del servidor",
            "details": None,
        }), 500
