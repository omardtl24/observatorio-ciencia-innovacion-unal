import os
import threading
import time
from datetime import datetime, timedelta

from flask import current_app # type: ignore

from app.models.base import db
from app.models.data_source import DataSource
from app.models.data_source_file import DataSourceFile
from app.models.documents_presentation import DocumentPresentation
from app.models.file import File
from app.models.report import Report
from app.models.simulator import Simulator
from app.services.file_service import FileService


class FileGarbageCollectorService:
    """Finds and removes files that aren't backed by anything anymore.

    Two independent kinds of orphan are handled:

    1. Orphaned File records: rows in the `files` table no longer referenced by
       any report, simulator, document/presentation, or data source (its current
       pointer, or any of its historic versions). These are cleaned up together
       with their on-disk content.
    2. Untracked files on disk: entries directly under FILE_STORAGE_ROOT (not
       recursing into subfolders like profile_images_cache/ or shiny-apps/,
       which are managed by their own separate lifecycles) that have no File
       record pointing at them at all - e.g. left behind by a crash between
       writing the file and committing its record.

    In both cases, entries younger than the grace period are never touched, so
    anything still mid-upload (a File row not yet linked to its owning entity,
    or a file on disk not yet backed by its File row) is never swept up.
    """

    @staticmethod
    def _referenced_file_ids():
        ids = set()

        for (value,) in db.session.query(Simulator.specs_file_id).filter(Simulator.specs_file_id.isnot(None)):
            ids.add(value)
        for (value,) in db.session.query(Report.document_file_id).filter(Report.document_file_id.isnot(None)):
            ids.add(value)
        for (value,) in db.session.query(DocumentPresentation.file_id).filter(DocumentPresentation.file_id.isnot(None)):
            ids.add(value)
        for (value,) in db.session.query(DataSource.file_id).filter(DataSource.file_id.isnot(None)):
            ids.add(value)
        for (value,) in db.session.query(DataSourceFile.file_id):
            ids.add(value)

        return ids

    @classmethod
    def find_orphaned_files(cls, grace_period_seconds=86400):
        """Return File records not referenced by any entity, older than the grace period."""
        cutoff = datetime.utcnow() - timedelta(seconds=grace_period_seconds)
        referenced_ids = cls._referenced_file_ids()

        candidates = File.query.filter(File.uploaded_at < cutoff).all()
        return [file for file in candidates if file.id not in referenced_ids]

    @classmethod
    def find_untracked_disk_files(cls, grace_period_seconds=86400):
        """Return absolute paths directly under FILE_STORAGE_ROOT with no matching File record.

        Only looks at the top level of FILE_STORAGE_ROOT - subfolders (the
        profile image cache, shiny app deployments, ...) are out of scope here.
        """
        storage_root = current_app.config.get("FILE_STORAGE_ROOT")
        if not storage_root or not os.path.isdir(storage_root):
            return []

        tracked_paths = {path for (path,) in db.session.query(File.storage_path)}
        cutoff = time.time() - grace_period_seconds
        untracked = []

        for name in os.listdir(storage_root):
            full_path = os.path.join(storage_root, name)

            if os.path.isdir(full_path):
                continue
            if full_path in tracked_paths:
                continue

            try:
                age_reference = os.lstat(full_path).st_mtime
            except OSError:
                continue

            if age_reference < cutoff:
                untracked.append(full_path)

        return untracked

    @classmethod
    def collect(cls, grace_period_seconds=86400, logger=None):
        """Run the full cleanup: orphaned File records, then untracked disk files.

        Returns:
            dict: {"orphaned_file_records": int, "untracked_disk_files": int, "removed": int (total)}
        """
        orphaned_file_records = cls._collect_orphaned_file_records(
            grace_period_seconds=grace_period_seconds, logger=logger
        )
        untracked_disk_files = cls._collect_untracked_disk_files(
            grace_period_seconds=grace_period_seconds, logger=logger
        )

        return {
            "orphaned_file_records": orphaned_file_records,
            "untracked_disk_files": untracked_disk_files,
            "removed": orphaned_file_records + untracked_disk_files,
        }

    @classmethod
    def _collect_orphaned_file_records(cls, grace_period_seconds=86400, logger=None):
        """Delete orphaned File records (DB record and on-disk content).

        Each file is handled independently: a failure on one (e.g. a race where
        it got linked to something after the query ran, or the DB still refuses
        the delete via a foreign key we didn't account for) is logged and
        skipped rather than aborting the whole run.
        """
        orphaned = cls.find_orphaned_files(grace_period_seconds=grace_period_seconds)
        removed = 0

        for file_record in orphaned:
            file_id = file_record.id
            storage_path = file_record.storage_path

            try:
                FileService.delete(file_id)
            except Exception as exc:
                if logger:
                    logger.warning(f"Skipped orphaned file {file_id} ({storage_path}): {str(exc)}")
                continue

            try:
                if os.path.lexists(storage_path):
                    os.remove(storage_path)
            except OSError as exc:
                if logger:
                    logger.warning(
                        f"Deleted DB record for file {file_id} but could not remove {storage_path}: {str(exc)}"
                    )

            removed += 1

        return removed

    @classmethod
    def _collect_untracked_disk_files(cls, grace_period_seconds=86400, logger=None):
        """Delete files on disk that have no File record at all."""
        untracked = cls.find_untracked_disk_files(grace_period_seconds=grace_period_seconds)
        removed = 0

        for path in untracked:
            try:
                os.remove(path)
                removed += 1
            except OSError as exc:
                if logger:
                    logger.warning(f"Could not remove untracked file {path}: {str(exc)}")

        return removed


def start_orphaned_files_cleanup_daemon(app):
    interval_seconds = int(app.config.get("ORPHANED_FILES_CLEANUP_INTERVAL_SECONDS", 3600))
    grace_period_seconds = int(app.config.get("ORPHANED_FILES_GRACE_PERIOD_SECONDS", 86400))

    def _run_forever():
        while True:
            try:
                with app.app_context():
                    result = FileGarbageCollectorService.collect(
                        grace_period_seconds=grace_period_seconds, logger=app.logger
                    )
                    if result["removed"]:
                        app.logger.info(
                            f"Orphaned files cleanup removed {result['orphaned_file_records']} orphaned "
                            f"record(s) and {result['untracked_disk_files']} untracked file(s)"
                        )
            except Exception as exc:
                app.logger.warning(f"Orphaned files cleanup iteration failed: {str(exc)}")
            time.sleep(interval_seconds)

    thread = threading.Thread(target=_run_forever, daemon=True)
    thread.start()
