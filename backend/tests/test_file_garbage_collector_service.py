"""Tests for FileGarbageCollectorService."""

import os
import time
from datetime import datetime, timedelta

import pytest # type: ignore

from app.domain.exceptions import NotFoundError
from app.models.documents_presentation import DocumentPresentation
from app.services.data_source_service import DataSourceService
from app.services.file_garbage_collector_service import FileGarbageCollectorService
from app.services.file_service import FileService
from app.services.report_service import ReportService
from app.services.simulator_service import SimulatorService


@pytest.fixture(autouse=True)
def _isolated_file_storage_root(app, tmp_path):
    # collect() now also scans FILE_STORAGE_ROOT for untracked disk files; pin
    # it to this test's own tmp_path so a value leaked from another test file
    # (app.config is mutated on a session-scoped app) can never sneak in.
    app.config["FILE_STORAGE_ROOT"] = str(tmp_path)
    yield


def _make_file(tmp_path, name="file.csv", content=b"content", age_seconds=None):
    path = tmp_path / name
    path.write_bytes(content)
    file_record = FileService.create(
        filename=name,
        storage_path=str(path),
        file_type=name.rsplit(".", 1)[-1],
        size_bytes=len(content),
        checksum_sha256="irrelevant-for-these-tests",
    )
    if age_seconds is not None:
        file_record.update(uploaded_at=datetime.utcnow() - timedelta(seconds=age_seconds))
    return file_record


class TestFindOrphanedFiles:
    def test_finds_unlinked_file_past_grace_period(self, app, tmp_path):
        with app.app_context():
            orphan = _make_file(tmp_path, "orphan.csv", age_seconds=90000)

            found = FileGarbageCollectorService.find_orphaned_files(grace_period_seconds=86400)

            assert [f.id for f in found] == [orphan.id]

    def test_recent_file_is_protected_by_grace_period(self, app, tmp_path):
        with app.app_context():
            _make_file(tmp_path, "fresh.csv")  # uploaded_at defaults to now

            found = FileGarbageCollectorService.find_orphaned_files(grace_period_seconds=86400)

            assert found == []

    def test_file_linked_via_report_is_not_orphaned(self, app, tmp_path):
        with app.app_context():
            file_record = _make_file(tmp_path, "report.pdf", age_seconds=90000)
            ReportService.create(title="R", document_file_id=file_record.id, updated_at=datetime.utcnow().date())

            found = FileGarbageCollectorService.find_orphaned_files(grace_period_seconds=86400)

            assert found == []

    def test_file_linked_via_simulator_specs_is_not_orphaned(self, app, tmp_path):
        with app.app_context():
            file_record = _make_file(tmp_path, "specs.txt", age_seconds=90000)
            SimulatorService.create(title="S", specs_file_id=file_record.id, from_file=False, simulator_url="http://x")

            found = FileGarbageCollectorService.find_orphaned_files(grace_period_seconds=86400)

            assert found == []

    def test_file_linked_via_documents_presentation_is_not_orphaned(self, app, tmp_path):
        with app.app_context():
            file_record = _make_file(tmp_path, "doc.pdf", age_seconds=90000)
            DocumentPresentation.create(title="D", file_id=file_record.id)

            found = FileGarbageCollectorService.find_orphaned_files(grace_period_seconds=86400)

            assert found == []

    def test_file_linked_via_data_source_history_is_not_orphaned(self, app, tmp_path):
        with app.app_context():
            file_record = _make_file(tmp_path, "data.csv", age_seconds=90000)
            # DataSourceService.create immediately promotes file_id to a new
            # symlink entity, so the original upload is referenced only via
            # data_source_files (the historic-versions table) - exactly the
            # reference path this test needs to exercise.
            DataSourceService.create(name="DS", description="d", file_id=file_record.id)

            found = FileGarbageCollectorService.find_orphaned_files(grace_period_seconds=86400)

            assert file_record.id not in [f.id for f in found]

    def test_data_source_current_symlink_file_is_not_orphaned(self, app, tmp_path):
        with app.app_context():
            file_record = _make_file(tmp_path, "data2.csv", age_seconds=90000)
            data_source = DataSourceService.create(name="DS2", description="d", file_id=file_record.id)
            symlink_file = DataSourceService.get_by_id(data_source.id).file
            symlink_file.update(uploaded_at=datetime.utcnow() - timedelta(seconds=90000))

            found = FileGarbageCollectorService.find_orphaned_files(grace_period_seconds=86400)

            assert symlink_file.id not in [f.id for f in found]


class TestCollect:
    def test_collect_removes_orphaned_file_from_db_and_disk(self, app, tmp_path):
        with app.app_context():
            orphan = _make_file(tmp_path, "gone.csv", age_seconds=90000)
            storage_path = orphan.storage_path
            orphan_id = orphan.id

            result = FileGarbageCollectorService.collect(grace_period_seconds=86400)

            assert result["orphaned_file_records"] == 1
            assert result["removed"] == 1
            assert not os.path.exists(storage_path)
            with pytest.raises(NotFoundError):
                FileService.get_by_id(orphan_id)

    def test_collect_leaves_linked_files_untouched(self, app, tmp_path):
        with app.app_context():
            file_record = _make_file(tmp_path, "kept.csv", age_seconds=90000)
            ReportService.create(title="R", document_file_id=file_record.id, updated_at=datetime.utcnow().date())

            result = FileGarbageCollectorService.collect(grace_period_seconds=86400)

            assert result["orphaned_file_records"] == 0
            assert os.path.exists(file_record.storage_path)
            assert FileService.get_by_id(file_record.id) is not None

    def test_collect_leaves_recent_unlinked_files_untouched(self, app, tmp_path):
        with app.app_context():
            file_record = _make_file(tmp_path, "too_new.csv")

            result = FileGarbageCollectorService.collect(grace_period_seconds=86400)

            assert result["orphaned_file_records"] == 0
            assert os.path.exists(file_record.storage_path)

    def test_collect_removes_symlinked_orphan_without_following_it(self, app, tmp_path):
        with app.app_context():
            real = _make_file(tmp_path, "real.csv")
            symlink_path = tmp_path / "orphan_link.csv"
            os.symlink(real.storage_path, symlink_path)

            orphan_symlink = FileService.create(
                filename="orphan_link.csv",
                storage_path=str(symlink_path),
                file_type="csv",
                size_bytes=real.size_bytes,
                checksum_sha256=real.checksum_sha256,
            )
            orphan_symlink.update(uploaded_at=datetime.utcnow() - timedelta(seconds=90000))

            result = FileGarbageCollectorService.collect(grace_period_seconds=86400)

            assert result["orphaned_file_records"] == 1
            assert not os.path.lexists(symlink_path)
            # the real target file must survive - only the symlink was removed
            assert os.path.exists(real.storage_path)


class TestFindUntrackedDiskFiles:
    def test_finds_file_with_no_file_record(self, app, tmp_path):
        app.config["FILE_STORAGE_ROOT"] = str(tmp_path)
        with app.app_context():
            stray = tmp_path / "stray.pdf"
            stray.write_bytes(b"stray content")
            old_time = time.time() - 90000
            os.utime(stray, (old_time, old_time))

            found = FileGarbageCollectorService.find_untracked_disk_files(grace_period_seconds=86400)

            assert found == [str(stray)]

    def test_ignores_files_backed_by_a_file_record(self, app, tmp_path):
        app.config["FILE_STORAGE_ROOT"] = str(tmp_path)
        with app.app_context():
            tracked = _make_file(tmp_path, "tracked.csv", age_seconds=90000)

            found = FileGarbageCollectorService.find_untracked_disk_files(grace_period_seconds=86400)

            assert str(tracked.storage_path) not in found

    def test_recent_stray_file_is_protected_by_grace_period(self, app, tmp_path):
        app.config["FILE_STORAGE_ROOT"] = str(tmp_path)
        with app.app_context():
            stray = tmp_path / "fresh_stray.pdf"
            stray.write_bytes(b"fresh")

            found = FileGarbageCollectorService.find_untracked_disk_files(grace_period_seconds=86400)

            assert found == []

    def test_does_not_recurse_into_subfolders(self, app, tmp_path):
        app.config["FILE_STORAGE_ROOT"] = str(tmp_path)
        with app.app_context():
            subdir = tmp_path / "shiny-apps"
            subdir.mkdir()
            nested_stray = subdir / "nested.pdf"
            nested_stray.write_bytes(b"nested")
            old_time = time.time() - 90000
            os.utime(nested_stray, (old_time, old_time))

            found = FileGarbageCollectorService.find_untracked_disk_files(grace_period_seconds=86400)

            assert found == []

    def test_finds_dangling_symlink_with_no_file_record(self, app, tmp_path):
        app.config["FILE_STORAGE_ROOT"] = str(tmp_path)
        with app.app_context():
            dangling_link = tmp_path / "dangling.csv"
            os.symlink(str(tmp_path / "does_not_exist.csv"), dangling_link)
            old_time = time.time() - 90000
            os.utime(dangling_link, (old_time, old_time), follow_symlinks=False)

            found = FileGarbageCollectorService.find_untracked_disk_files(grace_period_seconds=86400)

            assert found == [str(dangling_link)]


class TestCollectUntrackedDiskFiles:
    def test_collect_removes_stray_file_and_reports_it(self, app, tmp_path):
        app.config["FILE_STORAGE_ROOT"] = str(tmp_path)
        with app.app_context():
            stray = tmp_path / "stray.pdf"
            stray.write_bytes(b"stray content")
            old_time = time.time() - 90000
            os.utime(stray, (old_time, old_time))

            result = FileGarbageCollectorService.collect(grace_period_seconds=86400)

            assert result["untracked_disk_files"] == 1
            assert result["removed"] == 1
            assert not os.path.exists(stray)

    def test_collect_keeps_tracked_files_and_subfolders(self, app, tmp_path):
        app.config["FILE_STORAGE_ROOT"] = str(tmp_path)
        with app.app_context():
            # Linked to a report so phase 1 (orphaned File records) leaves it
            # alone too - this test is specifically about phase 2 not
            # mistaking a tracked, linked file for untracked disk cruft.
            tracked = _make_file(tmp_path, "tracked.csv", age_seconds=90000)
            ReportService.create(title="R", document_file_id=tracked.id, updated_at=datetime.utcnow().date())
            subdir = tmp_path / "profile_images_cache"
            subdir.mkdir()

            result = FileGarbageCollectorService.collect(grace_period_seconds=86400)

            assert result["untracked_disk_files"] == 0
            assert os.path.exists(tracked.storage_path)
            assert os.path.isdir(subdir)
