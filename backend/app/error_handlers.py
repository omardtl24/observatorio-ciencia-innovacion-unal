from flask import jsonify, request
from werkzeug.exceptions import HTTPException

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
        return jsonify({
            "code": "unauthorized",
            "message": reason,
            "details": None,
        }), 401

    @jwt.invalid_token_loader
    def handle_jwt_invalid_token(reason):
        app.logger.error(f"JWT invalid: {reason}")
        return jsonify({
            "code": "invalid_token",
            "message": reason,
            "details": None,
        }), 401

    @jwt.expired_token_loader
    def handle_jwt_expired_token(jwt_header, jwt_payload):
        app.logger.error("JWT expired")
        return jsonify({
            "code": "token_expired",
            "message": "Token has expired",
            "details": None,
        }), 401

    @jwt.needs_fresh_token_loader
    def handle_jwt_needs_fresh_token(jwt_header, jwt_payload):
        app.logger.error("JWT needs fresh token")
        return jsonify({
            "code": "fresh_token_required",
            "message": "Fresh token required",
            "details": None,
        }), 401

    @jwt.revoked_token_loader
    def handle_jwt_revoked_token(jwt_header, jwt_payload):
        app.logger.error("JWT revoked")
        return jsonify({
            "code": "token_revoked",
            "message": "Token has been revoked",
            "details": None,
        }), 401


def register_api_error_handlers(app):
    @app.errorhandler(DomainError)
    def handle_domain_error(error):
        return jsonify(error.to_dict()), error.code or 400

    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        return jsonify({
            "code": "http_error",
            "message": error.description or "HTTP error",
            "details": None,
        }), error.code or 500

    @app.errorhandler(Exception)
    def handle_unexpected_exception(error):
        app.logger.exception("Unhandled exception", exc_info=error)
        return jsonify({
            "code": "internal_server_error",
            "message": "Internal server error",
            "details": None,
        }), 500
