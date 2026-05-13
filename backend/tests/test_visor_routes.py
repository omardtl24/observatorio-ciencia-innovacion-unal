from io import BytesIO
from types import SimpleNamespace

import pytest # type: ignore

from app.domain.exceptions import SchemaValidationError


def _unwrap(f):
    while hasattr(f, "__wrapped__"):
        f = f.__wrapped__
    return f


def test_create_visor_success(monkeypatch, app):
    from app.api import visor_routes

    class DummyVisor:
        id = 30
        roles = [SimpleNamespace(name="Administrador"), SimpleNamespace(name="Investigador")]

        def to_dict(self, include=None, exclude=None):
            return {
                "id": 30,
                "title": "Visor",
                "description": "Test visor",
                "visor_url": "http://example.com/visor.zip",
                "updated_at": None,
            }

    updated = []
    granted = []
    added = []

    monkeypatch.setattr("app.api.visor_routes.assert_admin", lambda message: None)
    monkeypatch.setattr("app.api.visor_routes._get_visor_payload", lambda schema_class: {"title": "Visor", "description": "Test visor", "role_ids": [1, 2]})
    monkeypatch.setattr("app.api.visor_routes.RoleService.get_by_name", lambda name: SimpleNamespace(id=1, name=name))
    monkeypatch.setattr("app.api.visor_routes.RoleService.get_by_id", lambda role_id: SimpleNamespace(id=role_id))
    monkeypatch.setattr("app.api.visor_routes.VisorService.create", lambda self, **kwargs: SimpleNamespace(id=30))
    monkeypatch.setattr("app.api.visor_routes.build_resource_url", lambda uploaded_file, resource_id, resource_type: "http://example.com/visor.zip")
    monkeypatch.setattr("app.api.visor_routes.VisorService.update", lambda self, visor_id, **kwargs: updated.append((visor_id, kwargs)))
    monkeypatch.setattr("app.api.visor_routes.VisorService.get_by_id", lambda self, visor_id: DummyVisor())
    monkeypatch.setattr("app.api.visor_routes.AccessChecker.grant_admin_access", lambda resource_id, resource_type: granted.append((resource_id, resource_type)))
    monkeypatch.setattr("app.api.visor_routes.RoleVisorRelation.add", lambda role_id, visor_id: added.append((role_id, visor_id)))

    with app.test_request_context(
        "/visor",
        method="POST",
        data={"r_program": (BytesIO(b"zip"), "visor.zip")},
        content_type="multipart/form-data",
    ):
        response, code = _unwrap(visor_routes.create_visor)()

    assert code == 201
    assert response.get_json()["title"] == "Visor"
    assert granted == [(30, "visor")]
    assert added == [(2, 30)]
    assert updated == [(30, {"visor_url": "http://example.com/visor.zip"})]


def test_update_visor_roles_rejects_invalid_payload(monkeypatch, app):
    from app.api import visor_routes

    monkeypatch.setattr("app.api.visor_routes.assert_admin", lambda message: None)

    with app.test_request_context("/visor/1/roles", method="PATCH", json={"role_ids": "oops"}):
        with pytest.raises(SchemaValidationError):
            _unwrap(visor_routes.update_visor_roles)(1)


def test_delete_visor_cascade_removes_relations(monkeypatch, app):
    from app.api import visor_routes

    removed = []

    monkeypatch.setattr("app.api.visor_routes.assert_admin", lambda message: None)
    monkeypatch.setattr("app.api.visor_routes.VisorDataSourceRelation.remove_all_b_for_a", lambda visor_id: removed.append(("data_source", visor_id)))
    monkeypatch.setattr("app.api.visor_routes.RoleVisorRelation.remove_all_a_for_b", lambda visor_id: removed.append(("role", visor_id)))
    monkeypatch.setattr("app.api.visor_routes.delete_resource_file", lambda resource_id, resource_type: removed.append(("file", resource_id, resource_type)))
    monkeypatch.setattr("app.api.visor_routes.VisorService.delete", lambda visor_id: removed.append(("delete", visor_id)))

    with app.test_request_context("/visor/1?cascade=true", method="DELETE"):
        response, code = _unwrap(visor_routes.delete_visor)(1)

    assert code == 204
    assert removed == [("data_source", 1), ("role", 1), ("file", 1, "visor"), ("delete", 1)]


def test_get_visor_and_unauthorized(monkeypatch, app):
    from app.api import visor_routes

    monkeypatch.setattr('app.api.visor_routes.VisorService.get_all', lambda: [])
    f = _unwrap(visor_routes.get_visor)
    with app.test_request_context('/fake'):
        resp, code = f()
        assert code == 200

    monkeypatch.setattr('app.api.visor_routes.get_jwt_identity', lambda: 'u@test')
    monkeypatch.setattr('app.api.visor_routes.AccessChecker.check_access', lambda u, i, t: False)
    f2 = _unwrap(visor_routes.validate_visor_access)
    with pytest.raises(Exception):
        with app.test_request_context('/fake'):
            f2(1)

    f3 = _unwrap(visor_routes.get_visor_by_id)
    with pytest.raises(Exception):
        with app.test_request_context('/fake'):
            f3(1)
