"""Tests for the HTTP-triggerable orphaned-files garbage collector routes."""

import os
import time
from datetime import datetime, timedelta

import pytest # type: ignore

from app.domain.exceptions import IllegalOperationError
from app.services.file_service import FileService


def _unwrap(f):
    while hasattr(f, "__wrapped__"):
        f = f.__wrapped__
    return f


@pytest.fixture(autouse=True)
def _isolated_file_storage_root(app, tmp_path):
    # The routes now also scan FILE_STORAGE_ROOT for untracked disk files;
    # pin it to this test's own tmp_path for deterministic results.
    app.config["FILE_STORAGE_ROOT"] = str(tmp_path)
    yield


def _make_orphan(tmp_path, name="orphan.csv", age_seconds=90000):
    path = tmp_path / name
    path.write_bytes(b"content")
    file_record = FileService.create(
        filename=name,
        storage_path=str(path),
        file_type="csv",
        size_bytes=7,
        checksum_sha256="irrelevant",
    )
    file_record.update(uploaded_at=datetime.utcnow() - timedelta(seconds=age_seconds))
    return file_record


class TestPreviewOrphanedFilesRoute:
    def test_requires_admin(self, monkeypatch, app):
        from app.api import file_routes

        monkeypatch.setattr(
            "app.api.file_routes.assert_admin",
            lambda message: (_ for _ in ()).throw(IllegalOperationError(message)),
        )

        with pytest.raises(IllegalOperationError):
            with app.test_request_context("/file/orphaned"):
                _unwrap(file_routes.preview_orphaned_files)()

    def test_lists_orphaned_files_without_deleting(self, monkeypatch, app, tmp_path):
        from app.api import file_routes

        monkeypatch.setattr("app.api.file_routes.assert_admin", lambda message: None)

        with app.app_context():
            orphan = _make_orphan(tmp_path)

            with app.test_request_context("/file/orphaned?grace_period_seconds=86400"):
                response, code = _unwrap(file_routes.preview_orphaned_files)()

            assert code == 200
            payload = response.get_json()
            records = payload["orphaned_file_records"]
            assert len(records) == 1
            assert records[0]["id"] == orphan.id
            assert records[0]["filename"] == "orphan.csv"
            assert records[0]["uploaded_at"] is not None
            assert payload["untracked_disk_files"] == []

            # dry run: the file must still exist
            assert FileService.get_by_id(orphan.id) is not None

    def test_grace_period_query_param_excludes_recent_files(self, monkeypatch, app, tmp_path):
        from app.api import file_routes

        monkeypatch.setattr("app.api.file_routes.assert_admin", lambda message: None)

        with app.app_context():
            _make_orphan(tmp_path, "fresh.csv", age_seconds=10)

            with app.test_request_context("/file/orphaned?grace_period_seconds=86400"):
                response, code = _unwrap(file_routes.preview_orphaned_files)()

            assert code == 200
            payload = response.get_json()
            assert payload["orphaned_file_records"] == []
            assert payload["untracked_disk_files"] == []

    def test_lists_untracked_disk_files(self, monkeypatch, app, tmp_path):
        from app.api import file_routes

        monkeypatch.setattr("app.api.file_routes.assert_admin", lambda message: None)

        with app.app_context():
            stray = tmp_path / "stray.pdf"
            stray.write_bytes(b"stray content")
            old_time = time.time() - 90000
            os.utime(stray, (old_time, old_time))

            with app.test_request_context("/file/orphaned?grace_period_seconds=86400"):
                response, code = _unwrap(file_routes.preview_orphaned_files)()

            assert code == 200
            payload = response.get_json()
            assert payload["orphaned_file_records"] == []
            assert len(payload["untracked_disk_files"]) == 1
            assert payload["untracked_disk_files"][0]["path"] == str(stray)

            # dry run: the file must still exist
            assert os.path.exists(stray)

    def test_default_has_no_grace_period(self, monkeypatch, app, tmp_path):
        """Manual trigger route: with no query param, even a just-created orphan shows up."""
        from app.api import file_routes

        monkeypatch.setattr("app.api.file_routes.assert_admin", lambda message: None)

        with app.app_context():
            orphan = _make_orphan(tmp_path, "just_now.csv", age_seconds=0)

            with app.test_request_context("/file/orphaned"):
                response, code = _unwrap(file_routes.preview_orphaned_files)()

            assert code == 200
            payload = response.get_json()
            assert [r["id"] for r in payload["orphaned_file_records"]] == [orphan.id]


class TestCollectOrphanedFilesRoute:
    def test_requires_admin(self, monkeypatch, app):
        from app.api import file_routes

        monkeypatch.setattr(
            "app.api.file_routes.assert_admin",
            lambda message: (_ for _ in ()).throw(IllegalOperationError(message)),
        )

        with pytest.raises(IllegalOperationError):
            with app.test_request_context("/file/gc", method="POST"):
                _unwrap(file_routes.collect_orphaned_files)()

    def test_deletes_orphaned_files_and_reports_count(self, monkeypatch, app, tmp_path):
        from app.api import file_routes

        monkeypatch.setattr("app.api.file_routes.assert_admin", lambda message: None)

        with app.app_context():
            orphan = _make_orphan(tmp_path)
            orphan_id = orphan.id
            storage_path = orphan.storage_path

            with app.test_request_context("/file/gc?grace_period_seconds=86400", method="POST"):
                response, code = _unwrap(file_routes.collect_orphaned_files)()

            assert code == 200
            assert response.get_json() == {
                "orphaned_file_records": 1,
                "untracked_disk_files": 0,
                "removed": 1,
            }

            assert not os.path.exists(storage_path)
            with pytest.raises(Exception):
                FileService.get_by_id(orphan_id)

    def test_does_not_delete_recent_files(self, monkeypatch, app, tmp_path):
        from app.api import file_routes

        monkeypatch.setattr("app.api.file_routes.assert_admin", lambda message: None)

        with app.app_context():
            recent = _make_orphan(tmp_path, "fresh.csv", age_seconds=10)

            with app.test_request_context("/file/gc?grace_period_seconds=86400", method="POST"):
                response, code = _unwrap(file_routes.collect_orphaned_files)()

            assert code == 200
            assert response.get_json() == {
                "orphaned_file_records": 0,
                "untracked_disk_files": 0,
                "removed": 0,
            }
            assert FileService.get_by_id(recent.id) is not None

    def test_default_has_no_grace_period(self, monkeypatch, app, tmp_path):
        """Manual trigger route: with no query param, even a just-created orphan is deleted."""
        from app.api import file_routes

        monkeypatch.setattr("app.api.file_routes.assert_admin", lambda message: None)

        with app.app_context():
            orphan = _make_orphan(tmp_path, "just_now.csv", age_seconds=0)
            orphan_id = orphan.id
            storage_path = orphan.storage_path

            with app.test_request_context("/file/gc", method="POST"):
                response, code = _unwrap(file_routes.collect_orphaned_files)()

            assert code == 200
            assert response.get_json()["orphaned_file_records"] == 1
            assert not os.path.exists(storage_path)
            with pytest.raises(Exception):
                FileService.get_by_id(orphan_id)

    def test_can_opt_into_a_grace_period_explicitly(self, monkeypatch, app, tmp_path):
        """A manual caller can still ask for a safety margin via the query param."""
        from app.api import file_routes

        monkeypatch.setattr("app.api.file_routes.assert_admin", lambda message: None)

        with app.app_context():
            recent = _make_orphan(tmp_path, "fresh.csv", age_seconds=10)

            with app.test_request_context("/file/gc?grace_period_seconds=3600", method="POST"):
                response, code = _unwrap(file_routes.collect_orphaned_files)()

            assert code == 200
            assert response.get_json()["orphaned_file_records"] == 0
            assert FileService.get_by_id(recent.id) is not None

    def test_deletes_untracked_disk_files(self, monkeypatch, app, tmp_path):
        from app.api import file_routes

        monkeypatch.setattr("app.api.file_routes.assert_admin", lambda message: None)

        with app.app_context():
            stray = tmp_path / "stray.pdf"
            stray.write_bytes(b"stray content")
            old_time = time.time() - 90000
            os.utime(stray, (old_time, old_time))

            with app.test_request_context("/file/gc?grace_period_seconds=86400", method="POST"):
                response, code = _unwrap(file_routes.collect_orphaned_files)()

            assert code == 200
            assert response.get_json() == {
                "orphaned_file_records": 0,
                "untracked_disk_files": 1,
                "removed": 1,
            }
            assert not os.path.exists(stray)
