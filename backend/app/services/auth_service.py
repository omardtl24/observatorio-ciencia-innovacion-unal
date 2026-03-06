import secrets

from flask import current_app, session
from authlib.integrations.flask_client import OAuth
from itsdangerous import URLSafeTimedSerializer, BadSignature
from app.models import db
from flask_jwt_extended import create_access_token
from app.services.user_service import UserService
from app.services.role_service import RoleService
from app.services.relations.user_role_relation import UserRoleRelation
from app.domain.exceptions import ForbiddenError, IllegalOperationError, NotFoundError, UnauthorizedError
from datetime import datetime, timedelta

class AuthService:
    def __init__(self, app):
        self.oauth = OAuth(app)
        self.auth0 = self.oauth.register(
            'auth0',
            client_id=current_app.config.get("AUTH0_CLIENT_ID"),
            client_secret=current_app.config.get("AUTH0_CLIENT_SECRET"),
            client_kwargs={'scope': 'openid profile email'},
            server_metadata_url=f'https://{current_app.config.get("AUTH0_DOMAIN")}/.well-known/openid-configuration'
        )

    def _state_serializer(self):
        secret = current_app.config.get("FLASK_SECRET_KEY") or current_app.config.get("AUTH0_CLIENT_SECRET")
        return URLSafeTimedSerializer(secret_key=secret, salt="oauth-state-v1")

    def generate_oauth_state(self):
        nonce = secrets.token_urlsafe(24)
        payload = {
            "nonce": nonce,
            "purpose": "oauth_state",
        }
        serializer = self._state_serializer()
        return serializer.dumps(payload), nonce

    def validate_oauth_state(self, state_token):
        serializer = self._state_serializer()
        max_age = int(current_app.config.get("OAUTH_STATE_TTL_SECONDS", 300))

        try:
            payload = serializer.loads(state_token, max_age=max_age)
        except BadSignature as exc:
            raise UnauthorizedError("Invalid OAuth state") from exc
        except Exception as exc:
            raise UnauthorizedError("OAuth state expired or malformed") from exc

        if payload.get("purpose") != "oauth_state" or not payload.get("nonce"):
            raise UnauthorizedError("Invalid OAuth state payload")

        return payload

    def _exchange_code_for_token(self, authorization_code):
        redirect_uri = current_app.config.get("AUTH0_CALLBACK_URL")
        return self.auth0.fetch_access_token(
            code=authorization_code,
            grant_type="authorization_code",
            redirect_uri=redirect_uri,
        )

    @staticmethod
    def _extract_role_names(user):
        user_roles = getattr(user, "roles", None)
        if not user_roles:
            return []

        try:
            return [role.name for role in user_roles if getattr(role, "name", None)]
        except TypeError:
            return []

    def process_callback_for_redirect(self, authorization_code=None, nonce=None):
        """
        Process the Auth0 callback and return user info for session creation.
        This method validates the Auth0 authorization code and returns user information
        that will be stored in a secure, HttpOnly session cookie.
        """
        token = self._exchange_code_for_token(authorization_code) if authorization_code else self.auth0.authorize_access_token()
        user_info = token.get('userinfo')
        if not user_info:
            if nonce is not None:
                user_info = self.auth0.parse_id_token(token, nonce=nonce)
            else:
                user_info = self.auth0.parse_id_token(token)

        if not user_info:
            raise NotFoundError("No se pudo obtener el perfil del usuario desde Auth0")

        email = user_info.get("email")
        if not email:
            raise NotFoundError("El proveedor de identidad no proporcionó un correo electrónico")

        try:
            user = UserService.create(
                email=email,
                names=user_info.get("given_name", ""),
                last_names=user_info.get("family_name", "")
            )
        except IllegalOperationError:
            user = UserService.get_by_id(email)

        user = UserService.update(user.email,
                                  names=user_info.get("given_name", ""),
                                  last_names=user_info.get("family_name", ""),
                                  last_login_at=db.func.now())

        #If user email belongs to the community domain, ensure they have the "community" role
        email_community = current_app.config.get("RESTRICTED_EMAIL_DOMAIN")
        if email_community and email.endswith(f"@{email_community}"):
            try:
                community_rol = RoleService.get_by_name("Comunidad")
                if community_rol not in user.roles:
                    UserRoleRelation.add_role_to_user(user_email=email,
                                                      role_id=community_rol.id)
            except NotFoundError:
                pass

        current_app.logger.info(f"Auth callback successful for user: {email}")

        access_token = create_access_token(identity=email)

        return {
            "access_token": access_token,
            "email": email,
            "names": user.names,
            "last_names": user.last_names,
            "picture": user_info.get("picture"),
        }

    def create_session(self, user_info):
        """
        Create a secure server-side session for an authenticated user.
        
        Args:
            user_info: Dictionary with keys: email, names, last_names, picture
        
        Returns:
            None (session is stored server-side)
        """
        session['user_email'] = user_info.get('email')
        session['user_names'] = user_info.get('names', '')
        session['user_last_names'] = user_info.get('last_names', '')
        session['user_picture'] = user_info.get('picture', '')
        session['user_image_id'] = user_info.get('image_id')
        session['user_roles'] = user_info.get('roles', [])
        session['authenticated_at'] = datetime.utcnow().isoformat()
        session.permanent = True
        # Session is automatically marked as modified
        session.modified = True

    def get_session_user(self):
        """
        Get the authenticated user from the session.
        
        Returns:
            Dict with user info if session is valid, None otherwise
        """
        if 'user_email' not in session:
            return None
        
        return {
            'email': session.get('user_email'),
            'names': session.get('user_names'),
            'last_names': session.get('user_last_names'),
            'picture': session.get('user_picture'),
            'image_id': session.get('user_image_id'),
            'roles': session.get('user_roles', [])
        }

    def issue_access_token(self, user_email, image_id=None):
        """
        Issue a short-lived access token for an authenticated session.
        
        Args:
            user_email: Email of the authenticated user
            
        Returns:
            Tuple of (access_token, expires_in_seconds)
        """
        user = UserService.get_by_id(user_email)
        
        token_lifetime_seconds = int(current_app.config.get("SESSION_LIFETIME_SECONDS", 7200))

        access_token = create_access_token(
            identity=user_email,
            expires_delta=timedelta(seconds=token_lifetime_seconds),
            additional_claims={
                "names": user.names,
                "last_names": user.last_names,
                "picture": None,
                "image_id": image_id,
                "roles": self._extract_role_names(user),
            }
        )
        
        return access_token, token_lifetime_seconds

    def test_auth_callback(self):
        """
        Generate a test token with the DEFAULT_ADMIN_EMAIL.
        Used for testing purposes only.
        """
        admin_email = current_app.config.get("DEFAULT_ADMIN_EMAIL")
        access_token = create_access_token(
            identity=admin_email,
            additional_claims={
                "names": "Admin",
                "last_names": "User",
                "picture": ""
            }
        )
        return {
            "access_token": access_token
        }