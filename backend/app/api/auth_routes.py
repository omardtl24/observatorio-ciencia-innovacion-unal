from flask import Blueprint, jsonify, current_app, request, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.services.profile_image_fs_cache_service import ProfileImageFsCacheService
from app.api.utils.auth import build_auth_popup_html
from app.domain.exceptions import DomainError, UnauthorizedError

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")
test_auth_bp = Blueprint("test_auth", __name__, url_prefix="/test_auth")


@auth_bp.get("/login")
def login():
    """Redirect user to Auth0 login."""
    auth_service = AuthService(current_app)
    redirect_uri = current_app.config.get("AUTH0_CALLBACK_URL")
    oauth_state, oauth_nonce = auth_service.generate_oauth_state()
    return auth_service.auth0.authorize_redirect(redirect_uri=redirect_uri,
                                                 state=oauth_state,
                                                 nonce=oauth_nonce,
                                                 prompt='login',
                                                 connection="google-oauth2")


@auth_bp.get("/callback")
def callback():
    """
    Auth0 sends users here after login.
    Backend processes the callback, creates a secure session cookie,
    and returns HTML that communicates success to the opener window via postMessage.
    """
    auth_service = AuthService(current_app)
    
    try:
        state = request.args.get("state")
        code = request.args.get("code")

        if not state or not code:
            raise UnauthorizedError("Faltan datos para completar el inicio de sesión")

        state_payload = auth_service.validate_oauth_state(state)

        # Validate Auth0 callback and get user info
        user_info = auth_service.process_callback_for_redirect(
            authorization_code=code,
            nonce=state_payload.get("nonce")
        )

        image_id = None
        profile_picture_url = user_info.get("picture")
        if profile_picture_url:
            try:
                image_id = ProfileImageFsCacheService.cache_profile_image_at_login(
                    user_id=user_info["email"],
                    image_url=profile_picture_url,
                )
            except Exception as exc:
                current_app.logger.warning(
                    f"Profile image cache failed for {user_info.get('email')}: {str(exc)}"
                )

        user_info["image_id"] = image_id
        user = UserService.get_by_id(user_info["email"])
        user_info["roles"] = [role.name for role in user.roles] if getattr(user, "roles", None) else []
        
        # Create server-side session (stored server-side, cookie reference only)
        auth_service.create_session(user_info)
        
        current_app.logger.info(f"Profile image ID: {image_id}")
        
        message_data = {
            "status": "ok",
            "image_id": image_id,
            "roles": user_info.get("roles", []),
        }
        html_response = build_auth_popup_html(
            title='<span class="ok">Autenticacion completada</span>',
            subtitle="Inicio de sesion exitoso. Puede volver a la aplicacion.",
            payload=message_data,
            auto_close=True,
        )
        response = current_app.make_response(html_response)
        # Session cookie is automatically set by Flask session management
        return response, 200
        
    except DomainError as exc:
        message_data = {
            "status": "error",
            "error_code": exc.error_code,
            "message": exc.message,
        }
        html_response = build_auth_popup_html(
            title='<span class="error">Error de autenticacion</span>',
            subtitle="No fue posible completar el inicio de sesion.",
            payload=message_data,
            auto_close=False,
            error_message=exc.message,
        )
        response = current_app.make_response(html_response)
        return response, exc.code
    except Exception as exc:
        message_data = {
            "status": "error",
            "error_code": "internal_error",
            "message": "Ocurrió un error inesperado durante la autenticación",
        }
        html_response = build_auth_popup_html(
            title='<span class="error">Error inesperado</span>',
            subtitle="Ocurrio un error durante la autenticacion.",
            payload=message_data,
            auto_close=False,
            error_message=str(exc),
        )
        response = current_app.make_response(html_response)
        return response, 500



@test_auth_bp.get("/testLogin")
def test_mock_callback():
    token = AuthService(current_app).test_auth_callback()
    return token , 200

@auth_bp.post("/session")
def get_session():
    """
    Retrieve an access token for the authenticated user.
    Validates the HttpOnly session cookie and returns a short-lived access token.
    
    Returns:
        JSON: { access_token, expires_in } if authenticated
        401: If not authenticated (no valid session)
    """
    auth_service = AuthService(current_app)
    user_info = auth_service.get_session_user()
    
    if not user_info:
        current_app.logger.warning("Session access attempt without valid session")
        return jsonify({
            "code": "unauthorized",
            "message": "No hay una sesión activa. Inicia sesión para continuar.",
            "details": None
        }), 401
    
    try:
        access_token, expires_in = auth_service.issue_access_token(
            user_info['email'],
            image_id=user_info.get('image_id')
        )
        current_app.logger.info(f"Access token issued for user: {user_info['email']}")
        return jsonify({
            "access_token": access_token,
            "expires_in": expires_in
        }), 200
    except Exception as exc:
        current_app.logger.error(f"Error issuing access token: {str(exc)}")
        return jsonify({
            "code": "token_error",
            "message": "No fue posible generar el token de acceso",
            "details": None
        }), 401


@auth_bp.get("/images/<string:image_id>")
@jwt_required()
def get_cached_profile_image(image_id):
    user_id = get_jwt_identity()
    expected_image_id = ProfileImageFsCacheService.build_image_id(user_id)

    if image_id != expected_image_id:
        return jsonify({
            "code": "forbidden",
            "message": "La imagen solicitada no pertenece al usuario autenticado",
            "details": None
        }), 403

    image_path = ProfileImageFsCacheService.resolve_image_path(image_id)
    if not image_path:
        return jsonify({
            "code": "not_found",
            "message": "No se encontró la imagen solicitada",
            "details": None
        }), 404

    ProfileImageFsCacheService.touch_image(image_path)
    content_type = ProfileImageFsCacheService.guess_content_type(image_path)

    response = send_file(image_path, mimetype=content_type, conditional=True)
    response.headers["Cache-Control"] = "private, max-age=86400"
    return response, 200