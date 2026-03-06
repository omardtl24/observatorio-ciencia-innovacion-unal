import json
from html import escape
from urllib.parse import urlencode
from flask import Blueprint, jsonify, current_app, request, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.services.profile_image_fs_cache_service import ProfileImageFsCacheService
from app.domain.exceptions import DomainError, UnauthorizedError

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")
test_auth_bp = Blueprint("test_auth", __name__, url_prefix="/test_auth")


def _build_auth_popup_html(title, subtitle, payload, auto_close=True, error_message=None):
    payload_json = json.dumps(payload)
    safe_subtitle = escape(subtitle)
    safe_error_message = escape(error_message) if error_message else ""
    safe_status_text = (
        "Notificando a la aplicacion principal y cerrando esta ventana..."
        if auto_close
        else "Puede revisar el detalle del error y cerrar esta ventana manualmente."
    )
    actions_display = "none" if auto_close else "flex"
    error_detail_html = (
        f'<div class="error-box"><strong>Detalle:</strong> {safe_error_message}</div>'
        if safe_error_message
        else ""
    )

    return f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>{title}</title>
        <style>
            :root {{
                --bg: #f3f7ff;
                --card: #ffffff;
                --text: #0f172a;
                --muted: #475569;
                --ok: #0f766e;
                --error: #b91c1c;
                --btn: #1d4ed8;
                --btn-hover: #1e40af;
            }}
            * {{ box-sizing: border-box; }}
            body {{
                margin: 0;
                min-height: 100vh;
                display: grid;
                place-items: center;
                font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
                background: radial-gradient(circle at 20% 20%, #dbeafe 0%, var(--bg) 60%);
                color: var(--text);
                padding: 20px;
            }}
            .card {{
                width: min(460px, 100%);
                background: var(--card);
                border: 1px solid #dbeafe;
                border-radius: 16px;
                box-shadow: 0 10px 30px rgba(15, 23, 42, 0.08);
                padding: 24px;
                text-align: center;
            }}
            .title {{
                margin: 0;
                font-size: 1.25rem;
                font-weight: 700;
            }}
            .subtitle {{
                margin: 10px 0 0;
                color: var(--muted);
                line-height: 1.5;
            }}
            .ok {{ color: var(--ok); }}
            .error {{ color: var(--error); }}
            .hint {{
                margin-top: 14px;
                color: var(--muted);
                font-size: 0.92rem;
            }}
            .actions {{
                margin-top: 18px;
                display: {actions_display};
                justify-content: center;
            }}
            .error-box {{
                margin-top: 14px;
                border: 1px solid #fecaca;
                background: #fef2f2;
                color: #991b1b;
                border-radius: 10px;
                padding: 12px;
                text-align: left;
                font-size: 0.92rem;
            }}
            .close-btn {{
                border: 0;
                border-radius: 10px;
                background: var(--btn);
                color: #fff;
                padding: 10px 18px;
                font-weight: 600;
                cursor: pointer;
            }}
            .close-btn:hover {{ background: var(--btn-hover); }}
        </style>
    </head>
    <body>
        <div class="card">
            <h1 class="title">{title}</h1>
            <p class="subtitle">{safe_subtitle}</p>
            {error_detail_html}
            <p id="status-text" class="hint">{safe_status_text}</p>
            <div id="actions" class="actions">
                <button class="close-btn" onclick="window.close()">Cerrar ventana</button>
            </div>
        </div>
        <script type="text/javascript">
            const messageData = {payload_json};
            try {{
                if (window.opener && !window.opener.closed) {{
                    window.opener.postMessage(messageData, "*");
                }}
            }} catch (error) {{
                console.error("Failed to notify opener window:", error);
            }}

            const autoClose = {str(auto_close).lower()};
            if (autoClose) {{
                window.close();
                setTimeout(() => {{
                    const statusText = document.getElementById("status-text");
                    const actions = document.getElementById("actions");
                    if (statusText) {{
                        statusText.textContent = "Si la ventana no se cierra automaticamente, use el boton de abajo.";
                    }}
                    if (actions) {{
                        actions.style.display = "flex";
                    }}
                }}, 1200);
            }}
        </script>
    </body>
    </html>
    """

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
            raise UnauthorizedError("Missing OAuth callback parameters")

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
        html_response = _build_auth_popup_html(
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
        html_response = _build_auth_popup_html(
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
            "message": "An unexpected error occurred during authentication",
        }
        html_response = _build_auth_popup_html(
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
            "message": "No active session. Please authenticate first.",
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
            "message": "Failed to issue access token",
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
            "message": "Image does not belong to authenticated user",
            "details": None
        }), 403

    image_path = ProfileImageFsCacheService.resolve_image_path(image_id)
    if not image_path:
        return jsonify({
            "code": "not_found",
            "message": "Image not found",
            "details": None
        }), 404

    ProfileImageFsCacheService.touch_image(image_path)
    content_type = ProfileImageFsCacheService.guess_content_type(image_path)

    response = send_file(image_path, mimetype=content_type, conditional=True)
    response.headers["Cache-Control"] = "private, max-age=86400"
    return response, 200