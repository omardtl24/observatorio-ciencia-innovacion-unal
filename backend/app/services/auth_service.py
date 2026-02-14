from flask import current_app
from authlib.integrations.flask_client import OAuth
from app.models import db
from flask_jwt_extended import create_access_token
from app.services.user_service import UserService
from app.domain.exceptions import ForbiddenError, IllegalOperationError, NotFoundError

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

    def process_callback_for_redirect(self):
        """
        Process the Auth0 callback and always redirect to frontend with
        either user info or error message as query params.
        """
        query_params = {}
        token = self.auth0.authorize_access_token()
        user_info = token.get('userinfo') or self.auth0.parse_id_token(token)

        if not user_info:
            raise NotFoundError("No se pudo obtener el perfil del usuario desde Auth0")

        email = user_info.get("email")
        if not email:
            raise NotFoundError("El proveedor de identidad no proporcionó un correo electrónico")

        required_domain = current_app.config.get("RESTRICTED_EMAIL_DOMAIN")
        if not email.endswith(f"@{required_domain}"):
            raise ForbiddenError(f"Solo se permiten cuentas con dominio @{required_domain}")


        try:
            user = UserService.create(
                email=email,
                names=user_info.get("given_name", ""),
                last_names=user_info.get("family_name", "")
            )
        except IllegalOperationError:
            user = UserService.get_by_id(email)

        user = UserService.update(email, last_login_at=db.func.now())
        access_token = create_access_token(identity=email)

        # Success query params
        query_params = {
            "access_token": access_token,
            "email": email,
            "names": user.names,
            "last_names": user.last_names,
            "picture": user_info.get("picture")
        }
        
        current_app.logger.info(f"Auth callback successful for user: {email}")
        return query_params