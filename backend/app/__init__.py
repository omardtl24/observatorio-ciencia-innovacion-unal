from flask import Flask, jsonify, request, session
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from sqlalchemy.exc import OperationalError
from app.api.auth_routes import auth_bp, test_auth_bp
from app.api.visor_routes import visor_bp
from app.api.file_routes import file_bp
from app.api.report_routes import report_bp
from app.models.base import db
from app.config import Config, TestingConfig
from app.domain.exceptions import DomainError, DatabaseConnectionError
from werkzeug.exceptions import HTTPException
from app.services.bootstrap_service import BootstrapService
import logging
import traceback
import os

jwt = JWTManager()

def create_app(config_name="production"):
    """Create and configure the Flask app.
    
    Args:
        config_name (str): The configuration to use ('production' or 'testing').
    
    Returns:
        Flask: The configured Flask application instance.
    """
    app = Flask(__name__, instance_relative_config=True)
    
    if config_name == "testing":
        app.config.from_object(TestingConfig)
    else:
        app.config.from_object(Config)
    
    app.secret_key = app.config.get("FLASK_SECRET_KEY", "dev-secret-key")

    logging.basicConfig(level=logging.INFO)
    app.logger.setLevel(logging.INFO)

    @app.before_request
    def log_request():
        app.logger.info(f"Request: {request.method} {request.path}")

    @app.after_request
    def log_response(response):
        app.logger.info(f"Response: {response.status} {request.method} {request.path}")
        return response

    @app.errorhandler(DomainError)
    def handle_domain_error(error):
        app.logger.error(f"Domain error: {error.message}")
        response = jsonify(error.to_dict())
        response.status_code = error.code
        return response

    @app.errorhandler(OperationalError)
    def handle_database_connection_error(error):
        """Handle database connection errors with a 503 Service Unavailable response."""
        db_error = DatabaseConnectionError(
            "Database service is currently unavailable. Please check the database connection and try again later."
        )
        response = jsonify(db_error.to_dict())
        response.status_code = db_error.code
        return response

    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        description = getattr(error, "description", str(error))
        app.logger.error(f"HTTP exception: {type(error).__name__} - {description}")

        if isinstance(error, DomainError):
            response = jsonify(error.to_dict())
            response.status_code = error.code
            app.logger.error(f"Domain error: {error.message}")
            return response

        response = jsonify({
            "code": "http_exception",
            "message": error.description,
            "details": None,
        })
        response.status_code = error.code or 500
        return response

    db.init_app(app)
    jwt.init_app(app)
    
    # Configure CORS to support credentials (session cookies)
    CORS(app, 
         supports_credentials=True,
         origins=["*"])  # In production, specify exact origins
    
    # Configure secure session handling
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'None'
    app.config['SESSION_COOKIE_NAME'] = 'observatorio_session'
    app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour for session

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

    @app.route("/", methods=["GET"])
    def index():
        return jsonify({"status": "ok", "message": "Backend is running"}), 200

    #Include all blueprints (API routes)
    #Include auth or mock auth
    if app.config.get("TEST"):
        app.register_blueprint(test_auth_bp)
    else:
        app.register_blueprint(auth_bp)
    app.logger.info(f'TEST MODE: {app.config.get("TEST")}')
    app.register_blueprint(visor_bp)
    app.register_blueprint(file_bp)
    app.register_blueprint(report_bp)

    with app.app_context():
        BootstrapService.initialize_minimals()

    os.makedirs(app.config["FILE_STORAGE_ROOT"], exist_ok=True)

    return app