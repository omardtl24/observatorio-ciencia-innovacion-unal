"""Unit tests for the current-version symlink management in DataSourceService."""

import os

import pytest # type: ignore

from app.domain.exceptions import NotFoundError
from app.services.data_source_service import DataSourceService
from app.services.file_service import FileService


def _make_real_file(tmp_path, name, content):
    """Create a real file on disk and register it as a File entity, mimicking an upload."""
    path = tmp_path / name
    path.write_bytes(content)
    return FileService.create(
        filename=name,
        storage_path=str(path),
        file_type=name.rsplit(".", 1)[-1],
        size_bytes=len(content),
        checksum_sha256="irrelevant-for-these-tests",
    )


@pytest.fixture
def file_v1(app, tmp_path):
    with app.app_context():
        yield _make_real_file(tmp_path, "v1.csv", b"version one content")


@pytest.fixture
def file_v2(app, tmp_path):
    with app.app_context():
        yield _make_real_file(tmp_path, "v2.csv", b"version two content, different")


class TestDataSourceCreateSymlink:
    def test_current_pointer_is_a_symlink_to_the_real_file(self, app, file_v1):
        with app.app_context():
            data_source = DataSourceService.create(name="Source", file_id=file_v1.id)

            current = FileService.get_by_id(data_source.file_id)

            assert data_source.file_id != file_v1.id
            assert os.path.islink(current.storage_path)
            assert os.readlink(current.storage_path) == file_v1.storage_path

    def test_symlinked_current_resolves_to_the_same_content_as_the_real_file(self, app, file_v1):
        with app.app_context():
            data_source = DataSourceService.create(name="Source", file_id=file_v1.id)
            current = FileService.get_by_id(data_source.file_id)

            with open(current.storage_path, "rb") as f:
                content = f.read()

            assert content == b"version one content"

    def test_current_symlink_copies_metadata_from_the_real_file(self, app, file_v1):
        with app.app_context():
            data_source = DataSourceService.create(name="Source", file_id=file_v1.id)
            current = FileService.get_by_id(data_source.file_id)

            assert current.filename == file_v1.filename
            assert current.file_type == file_v1.file_type
            assert current.size_bytes == file_v1.size_bytes
            assert current.checksum_sha256 == file_v1.checksum_sha256

    def test_initial_file_is_recorded_in_history_as_the_real_file(self, app, file_v1):
        with app.app_context():
            data_source = DataSourceService.create(name="Source", file_id=file_v1.id)

            history = DataSourceService.get_file_history(data_source.id)

            assert len(history) == 1
            assert history[0].file_id == file_v1.id

    def test_get_current_file_resolves_through_the_symlink(self, app, file_v1):
        with app.app_context():
            data_source = DataSourceService.create(name="Source", file_id=file_v1.id)

            resolved = DataSourceService.get_current_file(data_source.id)

            assert resolved.id == file_v1.id


class TestDataSourcePublishNewVersion:
    def test_publishing_new_version_relinks_the_same_symlink_entity(self, app, file_v1, file_v2):
        with app.app_context():
            data_source = DataSourceService.create(name="Source", file_id=file_v1.id)
            symlink_id_before = data_source.file_id

            DataSourceService.update(data_source.id, file_id=file_v2.id)

            assert data_source.file_id == symlink_id_before

    def test_publishing_new_version_repoints_symlink_target(self, app, file_v1, file_v2):
        with app.app_context():
            data_source = DataSourceService.create(name="Source", file_id=file_v1.id)

            DataSourceService.publish_file_version(data_source.id, file_v2.id)
            current = FileService.get_by_id(data_source.file_id)

            assert os.readlink(current.storage_path) == file_v2.storage_path
            with open(current.storage_path, "rb") as f:
                assert f.read() == b"version two content, different"

    def test_publishing_new_version_keeps_previous_real_file_untouched(self, app, file_v1, file_v2):
        with app.app_context():
            data_source = DataSourceService.create(name="Source", file_id=file_v1.id)
            DataSourceService.publish_file_version(data_source.id, file_v2.id)

            untouched = FileService.get_by_id(file_v1.id)
            assert os.path.exists(untouched.storage_path)
            assert not os.path.islink(untouched.storage_path)
            with open(untouched.storage_path, "rb") as f:
                assert f.read() == b"version one content"

    def test_history_accumulates_every_published_real_file(self, app, file_v1, file_v2):
        with app.app_context():
            data_source = DataSourceService.create(name="Source", file_id=file_v1.id)
            DataSourceService.publish_file_version(data_source.id, file_v2.id)

            history = DataSourceService.get_file_history(data_source.id)
            history_file_ids = {entry.file_id for entry in history}

            assert history_file_ids == {file_v1.id, file_v2.id}

    def test_get_current_file_reflects_latest_publish(self, app, file_v1, file_v2):
        with app.app_context():
            data_source = DataSourceService.create(name="Source", file_id=file_v1.id)
            DataSourceService.publish_file_version(data_source.id, file_v2.id)

            resolved = DataSourceService.get_current_file(data_source.id)

            assert resolved.id == file_v2.id

    def test_republishing_same_file_is_idempotent(self, app, file_v1, file_v2):
        with app.app_context():
            data_source = DataSourceService.create(name="Source", file_id=file_v1.id)
            DataSourceService.publish_file_version(data_source.id, file_v2.id)
            DataSourceService.publish_file_version(data_source.id, file_v2.id)

            history = DataSourceService.get_file_history(data_source.id)

            assert len(history) == 2

    def test_publishing_a_file_that_was_already_historic_relinks_back(self, app, file_v1, file_v2):
        with app.app_context():
            data_source = DataSourceService.create(name="Source", file_id=file_v1.id)
            DataSourceService.publish_file_version(data_source.id, file_v2.id)
            DataSourceService.publish_file_version(data_source.id, file_v1.id)

            resolved = DataSourceService.get_current_file(data_source.id)
            history = DataSourceService.get_file_history(data_source.id)

            assert resolved.id == file_v1.id
            assert len(history) == 2


class TestDataSourcePublishSelfReferenceGuard:
    """Publishing the data source's own current file_id must not corrupt the symlink.

    This mirrors what a naive "resend the current file_id if nothing changed"
    frontend flow would send, since `data_source.file_id` is the symlink's id,
    not the real file's id.
    """

    def test_republishing_the_current_symlink_id_resolves_to_its_real_target(self, app, file_v1):
        with app.app_context():
            data_source = DataSourceService.create(name="Source", file_id=file_v1.id)
            symlink_id = data_source.file_id

            DataSourceService.publish_file_version(data_source.id, symlink_id)

            current = FileService.get_by_id(data_source.file_id)
            assert data_source.file_id == symlink_id
            assert os.path.islink(current.storage_path)
            assert os.readlink(current.storage_path) == file_v1.storage_path

    def test_republishing_the_current_symlink_id_does_not_duplicate_history(self, app, file_v1):
        with app.app_context():
            data_source = DataSourceService.create(name="Source", file_id=file_v1.id)

            DataSourceService.publish_file_version(data_source.id, data_source.file_id)

            history = DataSourceService.get_file_history(data_source.id)
            assert len(history) == 1
            assert history[0].file_id == file_v1.id


def _unwrap(f):
    while hasattr(f, "__wrapped__"):
        f = f.__wrapped__
    return f


class TestDataSourceFileHistoryRoute:
    def test_route_payload_includes_filename_and_current_flag(self, app, monkeypatch, file_v1, file_v2):
        from app.api import data_source_routes

        with app.app_context():
            data_source = DataSourceService.create(name="Source", file_id=file_v1.id)
            DataSourceService.publish_file_version(data_source.id, file_v2.id)
            data_source_id = data_source.id

        monkeypatch.setattr("app.api.data_source_routes.get_jwt_identity", lambda: "admin@test.com")
        monkeypatch.setattr("app.api.data_source_routes.AccessChecker.check_access", lambda user_email, resource_id, resource_type: True)

        with app.test_request_context(f"/data-source/{data_source_id}/files"):
            response, code = _unwrap(data_source_routes.get_data_source_file_history)(data_source_id)

        assert code == 200
        payload = response.get_json()
        assert len(payload) == 2

        by_file_id = {entry["file_id"]: entry for entry in payload}
        assert by_file_id[file_v1.id]["filename"] == "v1.csv"
        assert by_file_id[file_v2.id]["filename"] == "v2.csv"
        assert by_file_id[file_v1.id]["is_current"] is False
        assert by_file_id[file_v2.id]["is_current"] is True


class TestDataSourceDeleteSymlinkCleanup:
    def test_delete_removes_the_symlink_entity(self, app, file_v1):
        with app.app_context():
            data_source = DataSourceService.create(name="Source", file_id=file_v1.id)
            symlink_id = data_source.file_id

            DataSourceService.delete(data_source.id)

            with pytest.raises(NotFoundError):
                FileService.get_by_id(symlink_id)

    def test_delete_removes_the_symlink_from_disk(self, app, file_v1):
        with app.app_context():
            data_source = DataSourceService.create(name="Source", file_id=file_v1.id)
            symlink_path = FileService.get_by_id(data_source.file_id).storage_path

            DataSourceService.delete(data_source.id)

            assert not os.path.lexists(symlink_path)

    def test_delete_keeps_the_real_historic_file_intact(self, app, file_v1):
        with app.app_context():
            data_source = DataSourceService.create(name="Source", file_id=file_v1.id)

            DataSourceService.delete(data_source.id)

            preserved = FileService.get_by_id(file_v1.id)
            assert os.path.exists(preserved.storage_path)
            with open(preserved.storage_path, "rb") as f:
                assert f.read() == b"version one content"
