from datetime import date, datetime

import click # type: ignore
from flask import Flask, jsonify # type: ignore
from flask_cors import CORS # type: ignore
from flask_jwt_extended import JWTManager # type: ignore
from flask.json.provider import DefaultJSONProvider # type: ignore
from app.api.auth_routes import auth_bp, test_auth_bp
from app.api.visor_routes import visor_bp
from app.api.access_routes import access_bp
from app.api.file_routes import file_bp
from app.api.report_routes import report_bp
from app.api.simulator_routes import simulator_bp
from app.api.documents_presentation_routes import documents_presentation_bp
from app.api.permission_routes import permission_bp
from app.api.role_routes import role_bp
from app.api.data_source_routes import data_source_bp
from app.models.base import db
from app.config import Config, TestingConfig
from app.error_handlers import (
    register_api_error_handlers,
    register_app_logger,
    register_jwt_error_handlers,
)
from app.services.bootstrap_service import BootstrapService
from app.services.file_garbage_collector_service import (
    FileGarbageCollectorService,
    start_orphaned_files_cleanup_daemon,
)
from app.services.profile_image_fs_cache_service import (
    ProfileImageFsCacheService,
    start_profile_image_cleanup_daemon,
)
import logging
import os
from datetime import timedelta

jwt = JWTManager()


class ISODateJSONProvider(DefaultJSONProvider):
    def default(self, obj):
        if isinstance(obj, datetime):
            return super().default(obj)

        if isinstance(obj, date):
            return obj.isoformat()

        return super().default(obj)

def create_app(config_name="production"):
    """Create and configure the Flask app.
    
    Args:
        config_name (str): The configuration to use ('production' or 'testing').
    
    Returns:
        Flask: The configured Flask application instance.
    """
    app = Flask(__name__, instance_relative_config=True)
    app.json_provider_class = ISODateJSONProvider
    app.json = app.json_provider_class(app)
    
    if config_name == "testing":
        app.config.from_object(TestingConfig)
    else:
        app.config.from_object(Config)

    app.url_map.strict_slashes = False
    
    app.secret_key = app.config.get("FLASK_SECRET_KEY", "dev-secret-key")

    logging.basicConfig(level=logging.INFO)
    app.logger.setLevel(logging.INFO)

    db.init_app(app)
    jwt.init_app(app)
    register_api_error_handlers(app)
    register_jwt_error_handlers(jwt, app)
    
    # Configure CORS to support credentials (session cookies)
    CORS(app, 
         supports_credentials=True,
         origins=["*"])  # In production, specify exact origins
    
    # Configure secure session handling
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'None'
    app.config['SESSION_COOKIE_NAME'] = 'observatorio_session'
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(
        seconds=int(app.config.get("SESSION_LIFETIME_SECONDS", 7200))
    )

    @app.route('/favicon.ico')
    def favicon():
        return '', 204

    @app.route("/", methods=["GET"])
    def index():
        return jsonify({"status": "ok", "message": "El backend está en funcionamiento"}), 200

    # Include all blueprints (API routes)
    # Register mock auth routes if and only if test mode is explicitly enabled.
    is_test_mode = app.config.get("TEST") is True
    if is_test_mode:
        register_app_logger(app)
        app.register_blueprint(test_auth_bp)
        
    app.register_blueprint(auth_bp)
    app.logger.info(f"TEST MODE: {is_test_mode}")
    app.register_blueprint(visor_bp)
    app.register_blueprint(access_bp)
    app.register_blueprint(file_bp)
    app.register_blueprint(report_bp)
    app.register_blueprint(simulator_bp)
    app.register_blueprint(documents_presentation_bp)
    app.register_blueprint(permission_bp)
    app.register_blueprint(role_bp)
    app.register_blueprint(data_source_bp)
    
    populate = app.config.get("POPULATE") is True
    if populate:
        with app.app_context():
            BootstrapService.initialize_minimals()

    os.makedirs(app.config["FILE_STORAGE_ROOT"], exist_ok=True)
    os.makedirs(app.config["PROFILE_IMAGE_CACHE_DIR"], exist_ok=True)

    @app.cli.command("cleanup-profile-images")
    def cleanup_profile_images_command():
        ttl_seconds = int(app.config.get("PROFILE_IMAGE_CACHE_TTL_SECONDS", 86400))
        removed = ProfileImageFsCacheService.cleanup_expired_images(ttl_seconds=ttl_seconds)
        app.logger.info(f"Removed {removed} expired profile images")

    @app.cli.command("cleanup-orphaned-files")
    @click.option(
        "--grace-period-seconds",
        default=0,
        type=int,
        help=(
            "Minimum age, in seconds, an unlinked/untracked file must have "
            "before this command will remove it. This is a manually-run "
            "command, not the automated sweep, so it defaults to 0 (no "
            "grace period) - pass this to keep a safety margin instead."
        ),
    )
    def cleanup_orphaned_files_command(grace_period_seconds):
        result = FileGarbageCollectorService.collect(
            grace_period_seconds=grace_period_seconds, logger=app.logger
        )
        app.logger.info(
            f"Removed {result['orphaned_file_records']} orphaned file record(s) and "
            f"{result['untracked_disk_files']} untracked file(s) ({result['removed']} total)"
        )

    if not is_test_mode:
        start_profile_image_cleanup_daemon(app)
        start_orphaned_files_cleanup_daemon(app)

    return app