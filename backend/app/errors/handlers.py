from flask import jsonify
from app.services.exceptions import NotFoundError, IllegalOperationError

def register_error_handlers(app):
    """Register custom error handlers for the Flask app."""

    @app.errorhandler(NotFoundError)
    def handle_not_found_error(e):
        return jsonify({
            "error": str(e),
            "type": "NotFoundError"
        }), 404

    @app.errorhandler(IllegalOperationError)
    def handle_illegal_operation_error(e):
        return jsonify({
            "error": str(e),
            "type": "IllegalOperationError"
        }), 400

    @app.errorhandler(Exception)
    def handle_generic_exception(e):
        # Only handle unexpected exceptions
        return jsonify({
            "error": str(e),
            "type": type(e).__name__
        }), 500
