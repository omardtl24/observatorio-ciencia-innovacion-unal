from flask import Blueprint, jsonify, current_app, redirect, app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.auth_service import AuthService
from app.models.user import User
import os

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.get("/login")
def login():
    """Redirect user to Auth0 login."""
    auth_service = AuthService(current_app)
    redirect_uri = current_app.config.get("AUTH0_CALLBACK_URL")
    return auth_service.auth0.authorize_redirect(redirect_uri=redirect_uri,
                                                 prompt='login',
                                                 connection="google-oauth2")


@auth_bp.get("/callback")
def callback():
    """
    Auth0 sends users here after login.
    Backend returns JSON with JWT & profile.
    Frontend consumes this endpoint directly.
    """
    auth_service = AuthService(current_app)
    # Errors are handled inside the service and propagated to frontend via query params
    redirect_url = auth_service.process_callback_for_redirect()
    return redirect(redirect_url)


@auth_bp.get("/me")
@jwt_required()
def me():
    email = get_jwt_identity()
    if not email:
        return jsonify({"error": "Unauthorized"}), 401

    user = User.query.get(email)
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "email": user.email,
        "names": user.names,
        "last_names": user.last_names,
    }), 200
