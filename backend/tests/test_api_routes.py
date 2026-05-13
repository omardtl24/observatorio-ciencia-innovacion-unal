import types
import tempfile

import pytest # type: ignore

from app.domain.exceptions import UnauthorizedError, SchemaValidationError, IllegalOperationError


def test_access_routes_check_monkeypatched(app, monkeypatch):
    from app.api.access_routes import check_simulator_access, check_visor_access

    # ensure get_jwt_identity returns a user
    monkeypatch.setattr('app.api.access_routes.get_jwt_identity', lambda: 'u@test')

    # Access denied path
    monkeypatch.setattr('app.api.access_routes.AccessChecker.check_access', lambda u, i, t: False)
    with pytest.raises(UnauthorizedError):
        with app.test_request_context('/fake'):
            f = check_simulator_access
            while hasattr(f, "__wrapped__"):
                f = f.__wrapped__
            f(1)

    # Access allowed path
    monkeypatch.setattr('app.api.access_routes.AccessChecker.check_access', lambda u, i, t: True)
    with app.test_request_context('/fake'):
        f = check_visor_access
        while hasattr(f, "__wrapped__"):
            f = f.__wrapped__
        resp, code = f(1)
        assert code == 200


def test_auth_routes_session_and_mock(app, monkeypatch):
    from app.api.auth_routes import get_session, test_mock_callback
    from app.services.auth_service import AuthService

    # get_session when no session => 401
    monkeypatch.setattr('app.api.auth_routes.AuthService.get_session_user', lambda self: None)
    with app.test_request_context('/fake', method='POST'):
        f = get_session
        while hasattr(f, "__wrapped__"):
            f = f.__wrapped__
        resp, code = f()
        assert code == 401

    # test_mock_callback returns token from AuthService.test_auth_callback
    monkeypatch.setattr('app.api.auth_routes.AuthService.test_auth_callback', lambda self: 'tok')
    with app.test_request_context('/fake'):
        f = test_mock_callback
        while hasattr(f, "__wrapped__"):
            f = f.__wrapped__
        resp, code = f()
        assert resp == 'tok'
        assert code == 200


def test_data_source_get_all_returns_empty(app, monkeypatch):
    from app.api.data_source_routes import get_data_sources
    monkeypatch.setattr('app.api.data_source_routes.DataSourceService.get_all', lambda: [])
    with app.test_request_context('/fake'):
        f = get_data_sources
        while hasattr(f, "__wrapped__"):
            f = f.__wrapped__
        resp, code = f()
        assert code == 200
        assert resp.get_json() == []


def test_documents_presentations_get_all_and_unauthorized(app, monkeypatch):
    from app.api.documents_presentation_routes import get_documents_presentations, get_document_presentation_by_id
    monkeypatch.setattr('app.api.documents_presentation_routes.DocumentPresentationService.get_all', lambda: [])
    with app.test_request_context('/fake'):
        f = get_documents_presentations
        while hasattr(f, "__wrapped__"):
            f = f.__wrapped__
        resp, code = f()
        assert code == 200

    # unauthorized path for get by id
    monkeypatch.setattr('app.api.documents_presentation_routes.get_jwt_identity', lambda: 'u@test')
    monkeypatch.setattr('app.api.documents_presentation_routes.AccessChecker.check_access', lambda u, i, t: False)
    with pytest.raises(UnauthorizedError):
        with app.test_request_context('/fake'):
            f = get_document_presentation_by_id
            while hasattr(f, "__wrapped__"):
                f = f.__wrapped__
            f(1)


def test_file_routes_upload_and_download_errors(app):
    from app.api.file_routes import upload, download
    # bypass admin check which relies on JWT
    import app.api.file_routes as file_mod
    file_mod.assert_admin = lambda msg: None

    # upload: no file in request -> SchemaValidationError
    with pytest.raises(SchemaValidationError):
        with app.test_request_context('/fake', method='POST'):
            f = upload
            while hasattr(f, "__wrapped__"):
                f = f.__wrapped__
            f()

    # download: missing query params -> IllegalOperationError
    with pytest.raises(IllegalOperationError):
        with app.test_request_context('/fake'):
            f = download
            while hasattr(f, "__wrapped__"):
                f = f.__wrapped__
            f('f1')


def test_permission_update_refresh_token(app, monkeypatch):
    from app.api.permission_routes import update_refresh_token
    # bypass admin check and jwt identity
    import app.api.permission_routes as perm_mod
    perm_mod.assert_admin = lambda msg: None
    perm_mod.get_jwt_identity = lambda: 'u@test'

    class DummyPerm:
        def __init__(self):
            self.updated = False
        def updateRefreshToken(self, v):
            self.updated = True
        def isRefreshTokenValid(self):
            return True

    monkeypatch.setattr('app.api.permission_routes.PermissionService', lambda app: DummyPerm())

    # create a fake validated_data on request
    class VD:
        def model_dump(self):
            return {'refresh_token': 'x'}

    with app.test_request_context('/fake', method='POST'):
        # attach the validated payload the schema validator would provide
        from flask import request # type: ignore
        request.validated_data = VD()
        f = update_refresh_token
        while hasattr(f, "__wrapped__"):
            f = f.__wrapped__
        resp, code = f()
        assert code == 200
        assert resp.get_json()['updated'] is True


def test_report_get_all_and_get_by_id_unauthorized(app, monkeypatch):
    from app.api.report_routes import get_reports, get_report_by_id
    monkeypatch.setattr('app.api.report_routes.ReportService.get_all', lambda: [])
    with app.test_request_context('/fake'):
        f = get_reports
        while hasattr(f, "__wrapped__"):
            f = f.__wrapped__
        resp, code = f()
        assert code == 200

    monkeypatch.setattr('app.api.report_routes.get_jwt_identity', lambda: 'u@test')
    monkeypatch.setattr('app.api.report_routes.AccessChecker.check_access', lambda u, i, t: False)
    with pytest.raises(UnauthorizedError):
        with app.test_request_context('/fake'):
            f = get_report_by_id
            while hasattr(f, "__wrapped__"):
                f = f.__wrapped__
            f(1)


def test_role_get_management_and_validate(app, monkeypatch):
    from app.api.role_routes import get_role_management_data, validate_resource_access
    # bypass admin check used in get_role_management_data
    import app.api.role_routes as role_mod
    role_mod.assert_admin = lambda msg: None
    monkeypatch.setattr('app.api.role_routes.RoleService.get_all_dict', lambda include=None: [])
    monkeypatch.setattr('app.api.role_routes.UserService.get_all', lambda: [])
    with app.test_request_context('/fake'):
        f = get_role_management_data
        while hasattr(f, "__wrapped__"):
            f = f.__wrapped__
        resp, code = f()
        assert code == 200

    # validate_resource_access uses parse_resource_access_validation_params
    monkeypatch.setattr('app.api.role_routes.parse_role_assignment_payload', lambda: ('u@test', 1))
    monkeypatch.setattr('app.api.role_routes.parse_resource_access_validation_params', lambda: (1, 'report'))
    monkeypatch.setattr('app.api.role_routes.AccessChecker.check_access', lambda u, i, t: True)
    monkeypatch.setattr('app.api.role_routes.get_jwt_identity', lambda: 'u@test')
    with app.test_request_context('/fake'):
        f = validate_resource_access
        while hasattr(f, "__wrapped__"):
            f = f.__wrapped__
        resp, code = f()
        assert code == 200
        assert resp.get_json()['has_access'] is True


def test_visor_get_all_and_access_unauthorized(app, monkeypatch):
    from app.api.visor_routes import get_visor, validate_visor_access, get_visor_by_id
    monkeypatch.setattr('app.api.visor_routes.VisorService.get_all', lambda: [])
    with app.test_request_context('/fake'):
        f = get_visor
        while hasattr(f, "__wrapped__"):
            f = f.__wrapped__
        resp, code = f()
        assert code == 200

    monkeypatch.setattr('app.api.visor_routes.get_jwt_identity', lambda: 'u@test')
    monkeypatch.setattr('app.api.visor_routes.AccessChecker.check_access', lambda u, i, t: False)
    with pytest.raises(UnauthorizedError):
        with app.test_request_context('/fake'):
            f = validate_visor_access
            while hasattr(f, "__wrapped__"):
                f = f.__wrapped__
            f(1)

    with pytest.raises(UnauthorizedError):
        with app.test_request_context('/fake'):
            f = get_visor_by_id
            while hasattr(f, "__wrapped__"):
                f = f.__wrapped__
            f(1)
