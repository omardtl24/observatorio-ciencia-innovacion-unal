from io import BytesIO
from types import SimpleNamespace

import pytest # type: ignore

from app.domain.exceptions import IllegalOperationError, UnauthorizedError


def _unwrap(f):
    while hasattr(f, "__wrapped__"):
        f = f.__wrapped__
    return f


def test_upload_success_and_download_success(monkeypatch, app, tmp_path):
    from app.api import file_routes

    class DummyFileRecord:
        def to_dict(self, include=None, exclude=None):
            return {"id": 1, "filename": "sample.txt", "file_type": "txt", "size_bytes": 5}

    monkeypatch.setattr("app.api.file_routes.assert_admin", lambda message: None)
    monkeypatch.setattr("app.api.file_routes.FileService.create", lambda **kwargs: DummyFileRecord())
    app.config["FILE_STORAGE_ROOT"] = str(tmp_path)

    with app.test_request_context(
        "/file/upload",
        method="POST",
        data={"file": (BytesIO(b"hello"), "sample.txt")},
        content_type="multipart/form-data",
    ):
        response, code = _unwrap(file_routes.upload)()

    assert code == 201
    assert response.get_json()["filename"] == "sample.txt"

    file_path = tmp_path / "sample.txt"
    file_path.write_bytes(b"hello")

    monkeypatch.setattr("app.api.file_routes.get_jwt_identity", lambda: "user@example.com")
    monkeypatch.setattr("app.api.file_routes.AccessChecker.check_access", lambda user_email, resource_id, resource_origin: True)
    monkeypatch.setattr(
        "app.api.file_routes.FileService.get_by_id",
        lambda file_id: SimpleNamespace(storage_path=str(file_path), checksum_sha256="checksum"),
    )
    monkeypatch.setattr("app.api.file_routes.validate_sha256", lambda file_path_value, checksum: True)

    with app.test_request_context("/file/download/1?resource=report&id=1&display=true"):
        response = _unwrap(file_routes.download)("1")

    assert response.status_code == 200
    response.direct_passthrough = False
    assert response.get_data() == b"hello"


def test_download_missing_params_and_forbidden(monkeypatch, app):
    from app.api import file_routes

    monkeypatch.setattr("app.api.file_routes.assert_admin", lambda message: None)

    with pytest.raises(IllegalOperationError):
        with app.test_request_context("/file/download/1"):
            _unwrap(file_routes.download)("1")

    monkeypatch.setattr("app.api.file_routes.get_jwt_identity", lambda: "user@example.com")
    monkeypatch.setattr("app.api.file_routes.AccessChecker.check_access", lambda user_email, resource_id, resource_origin: False)

    with pytest.raises(UnauthorizedError):
        with app.test_request_context("/file/download/1?resource=report&id=1&display=true"):
            _unwrap(file_routes.download)("1")
