import io
import os
import tempfile
import zipfile
from html import escape

import pytest # type: ignore

from app.api.utils.auth import build_auth_popup_html
from app.api.utils.validate_schema import validate_schema
from app.api.utils.parsers import (
    parse_role_assignment_payload,
    parse_resource_access_validation_params,
)
from app.api.utils.file_utils import compute_sha256, validate_sha256
from app.api.utils.serializers import (
    serialize_user,
    serialize_resource_with_roles,
    serialize_data_source,
)
from app.api.utils.resource_urls import build_resource_url, delete_resource_file
from app.domain.exceptions import IllegalOperationError, NotFoundError, SchemaValidationError


def test_build_auth_popup_html_payload_and_error():
    payload = {"status": "error", "message": "Ocurrió"}
    html = build_auth_popup_html("Título", "Subtitulo & prueba", payload, auto_close=False, error_message="detalle <bad>")
    assert 'postMessage' in html
    assert 'Título' in html
    assert escape('Subtitulo & prueba') in html
    assert escape('detalle <bad>') in html


def test_validate_schema_success_and_failure():
    from pydantic import BaseModel # type: ignore

    class M(BaseModel):
        a: int

    model = validate_schema({"a": 1}, M)
    assert model.a == 1

    with pytest.raises(SchemaValidationError) as excinfo:
        validate_schema({"a": "x"}, M)
    assert isinstance(excinfo.value.details, dict)


def test_parsers_role_assignment_and_resource_params(app):
    with app.test_request_context('/fake', method='POST', json={'user_email': 'u@e.co', 'role_id': 3}):
        user_email, role_id = parse_role_assignment_payload()
        assert user_email == 'u@e.co'
        assert role_id == 3

    with app.test_request_context('/fake?id=10&resourceType=simulator'):
        rid, rtype = parse_resource_access_validation_params()
        assert rid == 10
        assert rtype == 'simulator'

    with app.test_request_context('/fake'):
        with pytest.raises(SchemaValidationError):
            parse_resource_access_validation_params()


def test_file_utils_compute_and_validate(tmp_path):
    p = tmp_path / "f.bin"
    data = b"hello world"
    p.write_bytes(data)
    checksum = compute_sha256(str(p))
    assert len(checksum) == 64
    assert validate_sha256(str(p), checksum) is True
    assert validate_sha256(str(p), checksum[:-1] + '0') is False


def test_serializers_simple():
    class R:
        def __init__(self):
            self.id = 1
            self.title = 'T'
            self.description = 'D'
            self.visor_url = '/'
            self.updated_at = None
            self.roles = []
        def to_dict(self, include=None):
            return {"id": self.id, "title": self.title}

    class U:
        def __init__(self):
            self.email = 'a@b'
            self.names = 'N'
            self.last_names = 'L'
            self.roles = []

    r = R()
    u = U()
    assert serialize_resource_with_roles(r)["id"] == 1
    su = serialize_user(u)
    assert su["email"] == 'a@b'


def test_build_resource_url_bad_zip_raises(app):
    # Create an in-memory file-like object that simulates uploaded file
    class FileLike:
        def __init__(self, data: bytes):
            self._data = data
        def save(self, path):
            with open(path, 'wb') as f:
                f.write(self._data)

    # Build a zip without renv.lock
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w') as z:
        z.writestr('somefile.txt', 'ok')
    buf.seek(0)

    filelike = FileLike(buf.read())

    # Ensure config paths exist
    with app.app_context():
        app.config['RESOURCES_SHARED_FOLDER'] = tempfile.mkdtemp()
        app.config['RESOURCES_BASE_URL'] = '/resources/'
        with pytest.raises(IllegalOperationError):
            build_resource_url(filelike, 'x1', 'simulator')


def test_delete_resource_file_not_found(app, tmp_path):
    with app.app_context():
        app.config['RESOURCES_SHARED_FOLDER'] = str(tmp_path)
        with pytest.raises(NotFoundError):
            delete_resource_file('nope', 'simulator')
