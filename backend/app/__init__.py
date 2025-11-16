from flask import Flask, jsonify, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from app.api.auth_routes import auth_bp
from app.api.bi_test_route import visor_bp
from app.models.base import db
from app.config import Config
import logging
import traceback
from app.errors.handlers import register_error_handlers


jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    logging.basicConfig(level=logging.INFO)
    app.logger.setLevel(logging.INFO)

    @app.before_request
    def log_request():
        app.logger.info(f"Request: {request.method} {request.path}")

    @app.after_request
    def log_response(response):
        app.logger.info(f"Response: {response.status} {request.method} {request.path}")
        return response

    
    register_error_handlers(app)


    db.init_app(app)
    jwt.init_app(app)

    @app.route("/", methods=["GET"])
    def index():
        return jsonify({"status": "ok", "message": "Backend is running"}), 200

    app.register_blueprint(auth_bp)
    app.register_blueprint(visor_bp)

    return app