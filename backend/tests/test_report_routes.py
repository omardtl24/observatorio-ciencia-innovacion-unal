from types import SimpleNamespace

import pytest # type: ignore

from app.domain.exceptions import SchemaValidationError, UnauthorizedError


def _unwrap(f):
    while hasattr(f, "__wrapped__"):
        f = f.__wrapped__
    return f


def test_create_report_success(monkeypatch, app):
    from app.api import report_routes

    class DummyValidatedData:
        def dict(self, exclude_unset=False):
            return {
                "title": "Quarterly report",
                "description": "Summary",
                "document_file_id": 7,
                "updated_at": None,
                "role_ids": [1, 2],
            }

    class DummyReport:
        id = 50

        def to_dict(self, include=None, exclude=None):
            return {
                "id": 50,
                "title": "Quarterly report",
                "description": "Summary",
                "document_file_id": 7,
                "updated_at": None,
            }

        roles = [SimpleNamespace(name="Administrador"), SimpleNamespace(name="Investigador")]

    role_calls = []

    monkeypatch.setattr("app.api.report_routes.assert_admin", lambda message: None)
    monkeypatch.setattr("app.api.report_routes.RoleService.get_by_name", lambda name: SimpleNamespace(id=1, name=name))
    monkeypatch.setattr("app.api.report_routes.RoleService.get_by_id", lambda role_id: SimpleNamespace(id=role_id))
    monkeypatch.setattr("app.api.report_routes.ReportService.create", lambda self, **kwargs: SimpleNamespace(id=50))
    monkeypatch.setattr("app.api.report_routes.ReportService.get_by_id", lambda self, report_id: DummyReport())
    monkeypatch.setattr("app.api.report_routes.AccessChecker.grant_admin_access", lambda resource_id, resource_type: role_calls.append((resource_id, resource_type)))
    monkeypatch.setattr("app.api.report_routes.RoleReportRelation.add", lambda role_id, report_id: role_calls.append((role_id, report_id)))

    with app.test_request_context("/report", method="POST"):
        from flask import request # type: ignore

        request.validated_data = DummyValidatedData()
        response, code = _unwrap(report_routes.create_report)()

    assert code == 201
    assert response.get_json()["title"] == "Quarterly report"
    assert role_calls == [(50, "report"), (2, 50)]


def test_update_report_rejects_empty_payload(monkeypatch, app):
    from app.api import report_routes

    class EmptyValidatedData:
        def dict(self, exclude_unset=False):
            return {}

    monkeypatch.setattr("app.api.report_routes.assert_admin", lambda message: None)

    with app.test_request_context("/report/1", method="PATCH"):
        from flask import request # type: ignore

        request.validated_data = EmptyValidatedData()
        with pytest.raises(SchemaValidationError):
            _unwrap(report_routes.update_report)(1)


def test_delete_report_cascade_removes_relations(monkeypatch, app):
    from app.api import report_routes

    removed = []

    monkeypatch.setattr("app.api.report_routes.assert_admin", lambda message: None)
    monkeypatch.setattr("app.api.report_routes.ReportDataSourceRelation.remove_all_b_for_a", lambda report_id: removed.append(("data_source", report_id)))
    monkeypatch.setattr("app.api.report_routes.RoleReportRelation.remove_all_a_for_b", lambda report_id: removed.append(("role", report_id)))
    monkeypatch.setattr("app.api.report_routes.ReportService.delete", lambda report_id: removed.append(("delete", report_id)))

    with app.test_request_context("/report/1?cascade=true", method="DELETE"):
        response, code = _unwrap(report_routes.delete_report)(1)

    assert code == 204
    assert removed == [("data_source", 1), ("role", 1), ("delete", 1)]


def test_get_reports_and_get_by_id_unauthorized(monkeypatch, app):
    from app.api import report_routes

    monkeypatch.setattr('app.api.report_routes.ReportService.get_all', lambda: [])
    f = _unwrap(report_routes.get_reports)
    with app.test_request_context('/fake'):
        resp, code = f()
        assert code == 200

    monkeypatch.setattr('app.api.report_routes.get_jwt_identity', lambda: 'u@test')
    monkeypatch.setattr('app.api.report_routes.AccessChecker.check_access', lambda u, i, t: False)
    f2 = _unwrap(report_routes.get_report_by_id)
    with pytest.raises(UnauthorizedError):
        with app.test_request_context('/fake'):
            f2(1)
