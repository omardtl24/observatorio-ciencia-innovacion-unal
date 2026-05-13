from types import SimpleNamespace

import pytest # type: ignore

from app.domain.exceptions import IllegalOperationError, UnauthorizedError


def _unwrap(f):
    while hasattr(f, "__wrapped__"):
        f = f.__wrapped__
    return f


def test_create_get_and_delete_data_source(monkeypatch, app):
    from app.api import data_source_routes

    class DummyValidatedData:
        def model_dump(self):
            return {"name": "Data source", "description": "Test source"}

    class DummyDataSource:
        id = 10

        def to_dict(self, include=None, exclude=None):
            return {"id": 10, "name": "Data source", "description": "Test source", "updated_at": None}

    created = []
    granted = []
    removed = []

    monkeypatch.setattr("app.api.data_source_routes.assert_admin", lambda message: None)
    monkeypatch.setattr(
        "app.api.data_source_routes.DataSourceService.create",
        lambda **kwargs: SimpleNamespace(id=10),
    )
    monkeypatch.setattr("app.api.data_source_routes.DataSourceService.get_by_id", lambda data_source_id: DummyDataSource())
    monkeypatch.setattr("app.api.data_source_routes.AccessChecker.grant_admin_access", lambda resource_id, resource_type: granted.append((resource_id, resource_type)))

    with app.test_request_context("/data-source", method="POST"):
        from flask import request # type: ignore

        request.validated_data = DummyValidatedData()
        response, code = _unwrap(data_source_routes.create_data_source)()

    assert code == 201
    assert response.get_json()["name"] == "Data source"
    assert granted == [(10, "data_source")]

    monkeypatch.setattr("app.api.data_source_routes.AccessChecker.check_access", lambda user_email, resource_id, resource_type: True)
    monkeypatch.setattr("app.api.data_source_routes.get_jwt_identity", lambda: "u@test")

    with app.test_request_context("/data-source/10"):
        response, code = _unwrap(data_source_routes.get_data_source_by_id)(10)

    assert code == 200
    assert response.get_json()["id"] == 10

    monkeypatch.setattr("app.api.data_source_routes.ReportDataSourceRelation.remove_all_b_for_a", lambda resource_id: removed.append(("report", resource_id)))
    monkeypatch.setattr("app.api.data_source_routes.VisorDataSourceRelation.remove_all_b_for_a", lambda resource_id: removed.append(("visor", resource_id)))
    monkeypatch.setattr("app.api.data_source_routes.SimulatorDataSourceRelation.remove_all_b_for_a", lambda resource_id: removed.append(("simulator", resource_id)))
    monkeypatch.setattr("app.api.data_source_routes.RoleDataSourceRelation.remove_all_b_for_a", lambda resource_id: removed.append(("role", resource_id)))
    monkeypatch.setattr("app.api.data_source_routes.DataSourceService.delete", lambda resource_id: created.append(resource_id))

    with app.test_request_context("/data-source/10?cascade=true", method="DELETE"):
        response, code = _unwrap(data_source_routes.delete_data_source)(10)

    assert code == 204
    assert created == [10]
    assert removed == [
        ("report", 10),
        ("visor", 10),
        ("simulator", 10),
        ("role", 10),
    ]


def test_get_data_source_by_id_unauthorized(monkeypatch, app):
    from app.api import data_source_routes

    monkeypatch.setattr('app.api.data_source_routes.get_jwt_identity', lambda: 'u@test')
    monkeypatch.setattr('app.api.data_source_routes.AccessChecker.check_access', lambda u, i, t: False)

    with pytest.raises(UnauthorizedError):
        with app.test_request_context('/fake'):
            _unwrap(data_source_routes.get_data_source_by_id)(1)
