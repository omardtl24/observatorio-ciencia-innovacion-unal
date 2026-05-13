import pytest # type: ignore

from app.domain.exceptions import UnauthorizedError


def _unwrap(f):
    while hasattr(f, "__wrapped__"):
        f = f.__wrapped__
    return f


def test_check_simulator_and_visor(monkeypatch, app):
    from app.api import access_routes

    monkeypatch.setattr('app.api.access_routes.get_jwt_identity', lambda: 'u@test')
    monkeypatch.setattr('app.api.access_routes.AccessChecker.check_access', lambda u, i, t: False)

    f_sim = _unwrap(access_routes.check_simulator_access)
    with pytest.raises(UnauthorizedError):
        with app.test_request_context('/fake'):
            f_sim(1)

    monkeypatch.setattr('app.api.access_routes.AccessChecker.check_access', lambda u, i, t: True)
    f_vis = _unwrap(access_routes.check_visor_access)
    with app.test_request_context('/fake'):
        resp, code = f_vis(1)
        assert code == 200
