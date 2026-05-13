from types import SimpleNamespace

import pytest # type: ignore

from app.domain.exceptions import UnauthorizedError


def _unwrap(f):
    while hasattr(f, "__wrapped__"):
        f = f.__wrapped__
    return f


def test_login_redirect_uses_auth_service(monkeypatch, app):
    from app.api import auth_routes

    class DummyAuth0:
        def authorize_redirect(self, **kwargs):
            return kwargs

    class DummyAuthService:
        def __init__(self, app):
            self.auth0 = DummyAuth0()

        def generate_oauth_state(self):
            return "state-123", "nonce-456"

    monkeypatch.setattr("app.api.auth_routes.AuthService", DummyAuthService)

    with app.test_request_context("/auth/login"):
        response = _unwrap(auth_routes.login)()

    assert response["redirect_uri"] == app.config.get("AUTH0_CALLBACK_URL")
    assert response["state"] == "state-123"
    assert response["nonce"] == "nonce-456"
    assert response["prompt"] == "login"
    assert response["connection"] == "google-oauth2"


def test_callback_success_and_domain_error(monkeypatch, app):
    from app.api import auth_routes

    created_sessions = []

    class DummyUser:
        roles = [SimpleNamespace(name="Administrador"), SimpleNamespace(name="Investigador")]

    class SuccessfulAuthService:
        def __init__(self, app):
            self.auth0 = SimpleNamespace()

        def validate_oauth_state(self, state):
            assert state == "state-1"
            return {"nonce": "nonce-1"}

        def process_callback_for_redirect(self, authorization_code, nonce):
            assert authorization_code == "code-1"
            assert nonce == "nonce-1"
            return {"email": "user@example.com", "picture": "https://example.com/picture.jpg"}

        def create_session(self, user_info):
            created_sessions.append(user_info)

    monkeypatch.setattr("app.api.auth_routes.AuthService", SuccessfulAuthService)
    monkeypatch.setattr(
        "app.api.auth_routes.ProfileImageFsCacheService.cache_profile_image_at_login",
        lambda **kwargs: "image-1",
    )
    monkeypatch.setattr("app.api.auth_routes.UserService.get_by_id", lambda user_id: DummyUser())

    with app.test_request_context("/auth/callback?state=state-1&code=code-1"):
        response, status = _unwrap(auth_routes.callback)()

    assert status == 200
    assert created_sessions
    assert created_sessions[0]["email"] == "user@example.com"
    assert created_sessions[0]["image_id"] == "image-1"
    assert created_sessions[0]["roles"] == ["Administrador", "Investigador"]
    assert "Autenticacion completada" in response.get_data(as_text=True)

    class FailingAuthService:
        def __init__(self, app):
            self.auth0 = SimpleNamespace()

        def validate_oauth_state(self, state):
            return {"nonce": "nonce-1"}

        def process_callback_for_redirect(self, authorization_code, nonce):
            raise UnauthorizedError("No se pudo completar el inicio de sesión")

    monkeypatch.setattr("app.api.auth_routes.AuthService", FailingAuthService)

    with app.test_request_context("/auth/callback?state=state-1&code=code-1"):
        response, status = _unwrap(auth_routes.callback)()

    assert status == 401
    assert "Error de autenticacion" in response.get_data(as_text=True)


def test_get_session_success(monkeypatch, app):
    from app.api import auth_routes

    class DummyAuthService:
        def __init__(self, app):
            self.auth0 = SimpleNamespace()

        def get_session_user(self):
            return {"email": "user@example.com", "image_id": "image-1"}

        def issue_access_token(self, email, image_id=None):
            assert email == "user@example.com"
            assert image_id == "image-1"
            return "access-token", 900

    monkeypatch.setattr("app.api.auth_routes.AuthService", DummyAuthService)

    with app.test_request_context("/auth/session", method="POST"):
        response, status = _unwrap(auth_routes.get_session)()

    assert status == 200
    assert response.get_json() == {"access_token": "access-token", "expires_in": 900}


def test_get_session_and_test_mock(monkeypatch, app):
    from app.api import auth_routes

    # no session -> 401
    monkeypatch.setattr('app.api.auth_routes.AuthService.get_session_user', lambda self: None)
    f = _unwrap(auth_routes.get_session)
    with app.test_request_context('/fake', method='POST'):
        resp, code = f()
        assert code == 401

    # test mock callback
    monkeypatch.setattr('app.api.auth_routes.AuthService.test_auth_callback', lambda self: 'tok')
    f2 = _unwrap(auth_routes.test_mock_callback)
    with app.test_request_context('/fake'):
        resp, code = f2()
        assert resp == 'tok'
        assert code == 200
