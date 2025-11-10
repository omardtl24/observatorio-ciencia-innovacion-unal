import os
from urllib.parse import urlencode
from flask import current_app, redirect
from authlib.integrations.flask_client import OAuth
from app.models import db
from app.models.user import User
from flask_jwt_extended import create_access_token


class AuthService:
    def __init__(self, app):
        self.oauth = OAuth(app)
        self.auth0 = self.oauth.register(
            'auth0',
            client_id=os.getenv("AUTH0_CLIENT_ID"),
            client_secret=os.getenv("AUTH0_CLIENT_SECRET"),
            client_kwargs={'scope': 'openid profile email'},
            server_metadata_url=f'https://{os.getenv("AUTH0_DOMAIN")}/.well-known/openid-configuration'
        )

    def process_callback_for_redirect(self):
        """
        Process the Auth0 callback and always redirect to frontend with
        either user info or error message as query params.
        """
        frontend_url = current_app.config.get("FRONTEND_URL")
        query_params = {}

        try:
            token = self.auth0.authorize_access_token()
            user_info = token.get('userinfo') or self.auth0.parse_id_token(token)

            if not user_info:
                raise ValueError("Cannot retrieve user profile from Auth0")

            email = user_info.get("email")
            if not email:
                raise ValueError("Email not provided by identity provider")

            required_domain = current_app.config.get("RESTRICTED_EMAIL_DOMAIN", "unal.edu.co")
            if not email.endswith(f"@{required_domain}"):
                raise ValueError(f"Only @{required_domain} accounts are allowed")

            # Load or create user
            user = User.query.get(email)
            if not user:
                user = User(
                    email=email,
                    names=user_info.get("given_name", ""),
                    last_names=user_info.get("family_name", "")
                )
                db.session.add(user)
                db.session.commit()

            user.update(last_login_at=db.func.now())

            access_token = create_access_token(identity=email)

            # Success query params
            query_params = {
                "access_token": access_token,
                "email": email,
                "names": user.names,
                "last_names": user.last_names
            }

        except Exception as e:
            # Instead of raising, propagate error to frontend
            current_app.logger.warning(f"Auth callback error: {e}")
            query_params = {"error": str(e)}

        # Build redirect URL
        redirect_url = f"{frontend_url}/auth/callback?{urlencode(query_params)}"
        return redirect_url



