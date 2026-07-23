import os
from uuid import uuid4

from flask import current_app # type: ignore

from app.domain.exceptions import IllegalOperationError
from app.models.base import db
from app.models.data_source import DataSource
from app.models.data_source_file import DataSourceFile
from app.models.file import File
from app.services.base_service import BaseService
from app.services.file_service import FileService

class DataSourceService(BaseService):
    model = DataSource

    @classmethod
    def create(cls, **data):
        """Create a data source, publishing its initial file as the current version."""
        target_file = cls._resolve_real_file(FileService.get_by_id(data["file_id"]))
        data_source = super().create(**data)
        cls._record_file_version(data_source.id, target_file.id)
        cls._republish_symlink(data_source, target_file)
        return data_source

    @classmethod
    def update(cls, resource_id, **data):
        """Update a data source, publishing a new file version when file_id is provided."""
        file_id = data.pop("file_id", None)
        data_source = super().update(resource_id, **data)

        if file_id is not None:
            data_source = cls.publish_file_version(resource_id, file_id)

        return data_source

    @classmethod
    def publish_file_version(cls, data_source_id, file_id):
        """Publish a file as the current version of a data source.

        The file itself is kept untouched as an exact copy and recorded in the
        data source's history. The data source's current pointer is a symlink
        that gets re-targeted at this file, so publishing never duplicates bytes.
        """
        data_source = cls.get_by_id(data_source_id)
        target_file = cls._resolve_real_file(FileService.get_by_id(file_id))

        try:
            cls._record_file_version(data_source_id, target_file.id)
            cls._republish_symlink(data_source, target_file)
            return data_source
        except Exception as e:
            db.session.rollback()
            raise IllegalOperationError(str(e))

    @classmethod
    def get_file_history(cls, data_source_id):
        """Get every exact file ever published under a data source, most recent first."""
        cls.get_by_id(data_source_id)
        return DataSourceFile.query.filter_by(data_source_id=data_source_id) \
            .order_by(DataSourceFile.published_at.desc()).all()

    @classmethod
    def get_current_file(cls, data_source_id):
        """Resolve the real (exact) file currently targeted by a data source's symlink."""
        data_source = cls.get_by_id(data_source_id)
        current = db.session.get(File, data_source.file_id)

        if current is None or not os.path.islink(current.storage_path):
            return current

        target_path = os.readlink(current.storage_path)
        return File.query.filter_by(storage_path=target_path).first()

    @classmethod
    def delete(cls, resource_id):
        """Delete a data source, cleaning up its current-version symlink.

        Historic (exact) files are never touched by this - only the symlink
        entity that represented the data source's current pointer is removed.
        """
        data_source = cls.get_by_id(resource_id)
        symlink_file = db.session.get(File, data_source.file_id)

        deleted = super().delete(resource_id)

        if symlink_file and os.path.islink(symlink_file.storage_path):
            symlink_path = symlink_file.storage_path
            FileService.delete(symlink_file.id)
            if os.path.islink(symlink_path):
                os.remove(symlink_path)

        return deleted

    @classmethod
    def _resolve_real_file(cls, file):
        """If `file` is itself a current-version symlink, resolve it to the real file it targets.

        Guards against callers accidentally re-publishing a data source's own
        current pointer (e.g. resubmitting `file_id` from a stale form), which
        would otherwise turn the symlink into a self-reference.
        """
        if not os.path.islink(file.storage_path):
            return file

        target_path = os.readlink(file.storage_path)
        return File.query.filter_by(storage_path=target_path).first() or file

    @classmethod
    def _record_file_version(cls, data_source_id, file_id):
        existing = DataSourceFile.query.filter_by(
            data_source_id=data_source_id, file_id=file_id
        ).first()
        if existing:
            return existing
        return DataSourceFile.create(data_source_id=data_source_id, file_id=file_id)

    @classmethod
    def _republish_symlink(cls, data_source, target_file):
        """(Re)point the data source's current-version symlink at target_file's exact content.

        Follows the same storage convention as the file upload logic (a file
        named `<uuid4()>.<file_type>` under FILE_STORAGE_ROOT) except the
        content written to disk is a symlink instead of the uploaded bytes.
        The first publish promotes `data_source.file_id` from the real file to
        this dedicated symlink entity; every following publish re-targets the
        same symlink in place instead of allocating a new one.
        """
        current = db.session.get(File, data_source.file_id)

        if current and os.path.islink(current.storage_path):
            if os.readlink(current.storage_path) == target_file.storage_path:
                return current

            os.remove(current.storage_path)
            os.symlink(target_file.storage_path, current.storage_path)
            current.update(
                filename=target_file.filename,
                file_type=target_file.file_type,
                size_bytes=target_file.size_bytes,
                checksum_sha256=target_file.checksum_sha256,
            )
            return current

        storage_root = current_app.config["FILE_STORAGE_ROOT"]
        os.makedirs(storage_root, exist_ok=True)

        symlink_name = f"{uuid4()}.{target_file.file_type}" if target_file.file_type else str(uuid4())
        symlink_path = os.path.join(storage_root, symlink_name)
        os.symlink(target_file.storage_path, symlink_path)

        symlink_file = FileService.create(
            filename=target_file.filename,
            storage_path=symlink_path,
            file_type=target_file.file_type,
            size_bytes=target_file.size_bytes,
            checksum_sha256=target_file.checksum_sha256,
        )

        data_source.file_id = symlink_file.id
        data_source.save()
        return symlink_file
