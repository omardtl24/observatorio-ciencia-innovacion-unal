import pytest # type: ignore

def _unwrap(f):
    while hasattr(f, "__wrapped__"):
        f = f.__wrapped__
    return f


def test_update_refresh_token(monkeypatch, app):
    from app.api import permission_routes

    permission_routes.assert_admin = lambda msg: None
    permission_routes.get_jwt_identity = lambda: 'u@test'

    class DummyPerm:
        def updateRefreshToken(self, v):
            self.updated = True
        def isRefreshTokenValid(self):
            return True

    monkeypatch.setattr('app.api.permission_routes.PermissionService', lambda app: DummyPerm())

    class VD:
        def model_dump(self):
            return {'refresh_token': 'x'}

    f = _unwrap(permission_routes.update_refresh_token)
    with app.test_request_context('/fake', method='POST'):
        from flask import request
        request.validated_data = VD()
        resp, code = f()
        assert code == 200
