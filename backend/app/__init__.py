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

    db.init_app(app)
    jwt.init_app(app)
    CORS(app)

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