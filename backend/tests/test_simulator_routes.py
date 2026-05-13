from io import BytesIO
from types import SimpleNamespace

import pytest # type: ignore

from app.domain.exceptions import SchemaValidationError


def _unwrap(f):
    while hasattr(f, "__wrapped__"):
        f = f.__wrapped__
    return f


def test_create_simulator_success(monkeypatch, app):
    from app.api import simulator_routes

    class DummySimulator:
        id = 20
        roles = [SimpleNamespace(name="Administrador"), SimpleNamespace(name="Investigador")]

        def to_dict(self, include=None, exclude=None):
            return {
                "id": 20,
                "title": "Simulator",
                "description": "Test simulator",
                "simulator_url": "http://example.com/sim.zip",
                "specs_file_id": None,
                "updated_at": None,
            }

    updated = []
    granted = []
    added = []

    monkeypatch.setattr("app.api.simulator_routes.assert_admin", lambda message: None)
    monkeypatch.setattr("app.api.simulator_routes._get_simulator_payload", lambda schema_class: {"title": "Simulator", "description": "Test simulator", "role_ids": [1, 2]})
    monkeypatch.setattr("app.api.simulator_routes.RoleService.get_by_name", lambda name: SimpleNamespace(id=1, name=name))
    monkeypatch.setattr("app.api.simulator_routes.RoleService.get_by_id", lambda role_id: SimpleNamespace(id=role_id))
    monkeypatch.setattr("app.api.simulator_routes.SimulatorService.create", lambda **kwargs: SimpleNamespace(id=20))
    monkeypatch.setattr("app.api.simulator_routes.build_resource_url", lambda uploaded_file, resource_id, resource_type: "http://example.com/sim.zip")
    monkeypatch.setattr("app.api.simulator_routes.SimulatorService.update", lambda simulator_id, **kwargs: updated.append((simulator_id, kwargs)))
    monkeypatch.setattr("app.api.simulator_routes.SimulatorService.get_by_id", lambda simulator_id: DummySimulator())
    monkeypatch.setattr("app.api.simulator_routes.AccessChecker.grant_admin_access", lambda resource_id, resource_type: granted.append((resource_id, resource_type)))
    monkeypatch.setattr("app.api.simulator_routes.RoleSimulatorRelation.add", lambda role_id, simulator_id: added.append((role_id, simulator_id)))

    with app.test_request_context(
        "/simulator",
        method="POST",
        data={"r_program": (BytesIO(b"zip"), "sim.zip")},
        content_type="multipart/form-data",
    ):
        response, code = _unwrap(simulator_routes.create_simulator)()

    assert code == 201
    assert response.get_json()["title"] == "Simulator"
    assert granted == [(20, "simulator")]
    assert added == [(2, 20)]
    assert updated == [(20, {"simulator_url": "http://example.com/sim.zip"})]


def test_update_simulator_roles_rejects_invalid_payload(monkeypatch, app):
    from app.api import simulator_routes

    monkeypatch.setattr("app.api.simulator_routes.assert_admin", lambda message: None)

    with app.test_request_context("/simulator/1/roles", method="PATCH", json={"role_ids": "oops"}):
        with pytest.raises(SchemaValidationError):
            _unwrap(simulator_routes.update_simulator_roles)(1)


def test_delete_simulator_cascade_removes_relations(monkeypatch, app):
    from app.api import simulator_routes

    removed = []

    monkeypatch.setattr("app.api.simulator_routes.assert_admin", lambda message: None)
    monkeypatch.setattr("app.api.simulator_routes.SimulatorDataSourceRelation.remove_all_b_for_a", lambda simulator_id: removed.append(("data_source", simulator_id)))
    monkeypatch.setattr("app.api.simulator_routes.RoleSimulatorRelation.remove_all_a_for_b", lambda simulator_id: removed.append(("role", simulator_id)))
    monkeypatch.setattr("app.api.simulator_routes.delete_resource_file", lambda resource_id, resource_type: removed.append(("file", resource_id, resource_type)))
    monkeypatch.setattr("app.api.simulator_routes.SimulatorService.delete", lambda simulator_id: removed.append(("delete", simulator_id)))

    with app.test_request_context("/simulator/1?cascade=true", method="DELETE"):
        response, code = _unwrap(simulator_routes.delete_simulator)(1)

    assert code == 204
    assert removed == [("data_source", 1), ("role", 1), ("file", 1, "simulator"), ("delete", 1)]


def test_get_simulators_and_validate_access(monkeypatch, app):
    from app.api import simulator_routes

    monkeypatch.setattr('app.api.simulator_routes.SimulatorService.get_all', lambda: [])
    f = _unwrap(simulator_routes.get_simulators)
    with app.test_request_context('/fake'):
        resp, code = f()
        assert code == 200

    monkeypatch.setattr('app.api.simulator_routes.get_jwt_identity', lambda: 'u@test')
    monkeypatch.setattr('app.api.simulator_routes.AccessChecker.check_access', lambda u, i, t: False)
    f2 = _unwrap(simulator_routes.validate_simulator_access)
    with pytest.raises(Exception):
        with app.test_request_context('/fake'):
            f2(1)

    f3 = _unwrap(simulator_routes.get_simulator_by_id)
    with pytest.raises(Exception):
        with app.test_request_context('/fake'):
            f3(1)
