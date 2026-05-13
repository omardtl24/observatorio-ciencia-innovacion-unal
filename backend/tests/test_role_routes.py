from types import SimpleNamespace

import pytest # type: ignore

from app.domain.exceptions import IllegalOperationError


def _unwrap(f):
    while hasattr(f, "__wrapped__"):
        f = f.__wrapped__
    return f


def test_create_role_success_and_assign_duplicate_error(monkeypatch, app):
    from app.api import role_routes

    monkeypatch.setattr("app.api.role_routes.assert_admin", lambda message: None)
    monkeypatch.setattr(
        "app.api.role_routes.RoleService.create",
        lambda **kwargs: SimpleNamespace(to_dict=lambda: {"id": 5, "name": "Editor", "description": "Can edit"}),
    )

    with app.test_request_context("/role", method="POST", json={"name": "Editor", "description": "Can edit"}):
        response, code = _unwrap(role_routes.create_role)()

    assert code == 201
    assert response.get_json()["name"] == "Editor"

    monkeypatch.setattr("app.api.role_routes.parse_role_assignment_payload", lambda: ("user@example.com", 7))
    monkeypatch.setattr(
        "app.api.role_routes.UserRoleRelation.get_user_by_email",
        lambda email: SimpleNamespace(roles=[SimpleNamespace(id=7)]),
    )
    monkeypatch.setattr("app.api.role_routes.RoleService.get_by_id", lambda role_id: SimpleNamespace(id=role_id))

    with pytest.raises(IllegalOperationError):
        with app.test_request_context("/role/assign", method="POST"):
            _unwrap(role_routes.assign_role_to_user)()


def test_delete_role_cascade_removes_relations(monkeypatch, app):
    from app.api import role_routes

    removed = []

    monkeypatch.setattr("app.api.role_routes.assert_admin", lambda message: None)
    monkeypatch.setattr("app.api.role_routes.RoleReportRelation.remove_all_b_for_a", lambda role_id: removed.append(("report", role_id)))
    monkeypatch.setattr("app.api.role_routes.RoleSimulatorRelation.remove_all_b_for_a", lambda role_id: removed.append(("simulator", role_id)))
    monkeypatch.setattr("app.api.role_routes.RoleVisorRelation.remove_all_b_for_a", lambda role_id: removed.append(("visor", role_id)))
    monkeypatch.setattr("app.api.role_routes.RoleDataSourceRelation.remove_all_b_for_a", lambda role_id: removed.append(("data_source", role_id)))
    monkeypatch.setattr("app.api.role_routes.DocumentPresentationRoleRelation.remove_all_a_for_b", lambda role_id: removed.append(("document", role_id)))
    monkeypatch.setattr("app.api.role_routes.UserRoleRelation.remove_all_a_for_b", lambda role_id: removed.append(("user", role_id)))
    monkeypatch.setattr("app.api.role_routes.RoleService.delete", lambda role_id: removed.append(("delete", role_id)))

    with app.test_request_context("/role/5?cascade=true", method="DELETE"):
        response, code = _unwrap(role_routes.delete_role)(5)

    assert code == 204
    assert removed == [
        ("report", 5),
        ("simulator", 5),
        ("visor", 5),
        ("data_source", 5),
        ("document", 5),
        ("user", 5),
        ("delete", 5),
    ]


def test_get_management_and_validate(monkeypatch, app):
    from app.api import role_routes

    role_routes.assert_admin = lambda msg: None
    monkeypatch.setattr('app.api.role_routes.RoleService.get_all_dict', lambda include=None: [])
    monkeypatch.setattr('app.api.role_routes.UserService.get_all', lambda: [])
    f = _unwrap(role_routes.get_role_management_data)
    with app.test_request_context('/fake'):
        resp, code = f()
        assert code == 200

    monkeypatch.setattr('app.api.role_routes.parse_resource_access_validation_params', lambda: (1, 'report'))
    monkeypatch.setattr('app.api.role_routes.AccessChecker.check_access', lambda u, i, t: True)
    monkeypatch.setattr('app.api.role_routes.get_jwt_identity', lambda: 'u@test')
    f2 = _unwrap(role_routes.validate_resource_access)
    with app.test_request_context('/fake'):
        resp, code = f2()
        assert code == 200
        assert resp.get_json()['has_access'] is True
