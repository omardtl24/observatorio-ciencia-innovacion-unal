import json
from urllib.parse import urlencode
from flask import Blueprint, jsonify, current_app, redirect, session, render_template_string
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
    Backend processes the callback, creates a secure session cookie,
    and returns HTML that communicates success to the opener window via postMessage.
    """
    auth_service = AuthService(current_app)
    
    try:
        # Validate Auth0 callback and get user info
        user_info = auth_service.process_callback_for_redirect()
        
        # Create server-side session (stored server-side, cookie reference only)
        auth_service.create_session(user_info)
        
        # Get profile picture URL to send to frontend
        profile_picture = user_info.get('picture', '')
        current_app.logger.info(f"Profile picture URL: {profile_picture}")
        
        # Create message data and JSON encode it for safe JavaScript embedding
        message_data = {
            "status": "ok",
            "picture": profile_picture
        }
        message_json = json.dumps(message_data)
        
        # Return HTML that sends postMessage to opener and closes popup
        html_response = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Authentication Complete</title>
        </head>
        <body>
            <script type="text/javascript">
                const messageData = {message_json};
                console.log("Auth callback - sending data:", messageData);
                window.opener.postMessage(messageData, "*");
                window.close();
            </script>
            <p>Authentication successful. This window will close automatically.</p>
        </body>
        </html>
        """
        response = current_app.make_response(html_response)
        # Session cookie is automatically set by Flask session management
        return response, 200
        
    except DomainError as exc:
        # Return error HTML with postMessage
        html_response = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Authentication Error</title>
        </head>
        <body>
            <script type="text/javascript">
                window.opener.postMessage(
                    {{ 
                        status: "error", 
                        error_code: "{exc.error_code}",
                        message: "{exc.message}"
                    }},
                    "*"
                );
                window.close();
            </script>
            <p>Authentication failed: {exc.message}</p>
        </body>
        </html>
        """
        response = current_app.make_response(html_response)
        return response, 400
    except Exception as exc:
        current_app.logger.error(f"Unexpected error in callback: {str(exc)}")
        html_response = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Authentication Error</title>
        </head>
        <body>
            <script type="text/javascript">
                window.opener.postMessage(
                    { 
                        status: "error", 
                        error_code: "internal_error",
                        message: "An unexpected error occurred during authentication"
                    },
                    "*"
                );
                window.close();
            </script>
            <p>An unexpected error occurred.</p>
        </body>
        </html>
        """
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
        access_token, expires_in = auth_service.issue_access_token(user_info['email'])
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