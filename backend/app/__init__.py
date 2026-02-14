from flask import Flask, jsonify, request, session
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from sqlalchemy.exc import OperationalError
from app.api.auth_routes import auth_bp
from app.api.visor_routes import visor_bp
from app.models.base import db
from app.config import Config
from app.domain.exceptions import DomainError, DatabaseConnectionError
import logging
import traceback
#from app.errors.handlers import register_error_handlers


jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.secret_key = app.config.get("FLASK_SECRET_KEY")

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
    app.register_blueprint(auth_bp)
    app.register_blueprint(visor_bp)
    return app