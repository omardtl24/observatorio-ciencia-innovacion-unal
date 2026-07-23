"""Tests for Flask CLI commands registered in app/__init__.py."""

import os

import pytest # type: ignore

from app.domain.exceptions import NotFoundError
from app.services.file_service import FileService


@pytest.fixture(autouse=True)
def _isolated_file_storage_root(app, tmp_path):
    app.config["FILE_STORAGE_ROOT"] = str(tmp_path)
    yield


def _make_orphan(tmp_path, name="orphan.csv"):
    path = tmp_path / name
    path.write_bytes(b"content")
    return FileService.create(
        filename=name,
        storage_path=str(path),
        file_type="csv",
        size_bytes=7,
        checksum_sha256="irrelevant",
    )


class TestCleanupOrphanedFilesCommand:
    def test_default_has_no_grace_period(self, app, tmp_path):
        """The CLI is a manual trigger too: a just-created orphan is removed by default."""
        with app.app_context():
            orphan = _make_orphan(tmp_path)
            orphan_id = orphan.id
            storage_path = orphan.storage_path

        runner = app.test_cli_runner()
        result = runner.invoke(args=["cleanup-orphaned-files"])

        assert result.exit_code == 0
        with app.app_context():
            assert not os.path.exists(storage_path)
            with pytest.raises(NotFoundError):
                FileService.get_by_id(orphan_id)

    def test_can_opt_into_a_grace_period(self, app, tmp_path):
        with app.app_context():
            recent = _make_orphan(tmp_path, "fresh.csv")
            recent_id = recent.id

        runner = app.test_cli_runner()
        result = runner.invoke(args=["cleanup-orphaned-files", "--grace-period-seconds", "3600"])

        assert result.exit_code == 0
        with app.app_context():
            assert FileService.get_by_id(recent_id) is not None
