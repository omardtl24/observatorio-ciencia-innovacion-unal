from urllib.parse import urlencode
from flask import Blueprint, jsonify, current_app, redirect
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.domain.exceptions import DomainError, UnauthorizedError

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")
test_auth_bp = Blueprint("test_auth", __name__, url_prefix="/auth")

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
    Backend redirects to frontend with query params and tokens or error.
    """
    auth_service = AuthService(current_app)
    frontend_url = current_app.config.get("FRONTEND_URL")
    
    try:
        query_params = auth_service.process_callback_for_redirect()
        redirect_url = f"{frontend_url}/login?{urlencode(query_params)}"
        return redirect(redirect_url)
    except DomainError as exc:
        params = {
            "error_code": exc.error_code,
            "message": exc.message
        }
        redirect_url = f"{frontend_url}/login?{urlencode(params)}"
        return redirect(redirect_url)


@test_auth_bp.get("/testLogin")
def test_mock_callback():
    token = AuthService(current_app).test_auth_callback()
    return token , 200
