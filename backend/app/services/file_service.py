import os
import hashlib
from werkzeug.utils import secure_filename
from flask import current_app

from app.services.base_service import BaseService
from app.services.exceptions import IllegalOperationError
from app.models.file import File
from app.models.base import db


class FileService(BaseService):
    model = File

    @classmethod
    def save_uploaded_file(cls, flask_file):
        if flask_file is None or flask_file.filename == "":
            raise IllegalOperationError("No file provided")

        filename = secure_filename(flask_file.filename)

        # ✅ Load from config
        file_storage_path = current_app.config.get("FILE_STORAGE_PATH")
        if not file_storage_path:
            raise IllegalOperationError(
                "FILE_STORAGE_PATH not configured in .env or config"
            )

        os.makedirs(file_storage_path, exist_ok=True)
        file_path = os.path.join(file_storage_path, filename)

        try:
            flask_file.save(file_path)
        except Exception as e:
            raise IllegalOperationError(f"Could not save file to disk: {e}")

        size_bytes = os.path.getsize(file_path)
        checksum = cls._calculate_sha256(file_path)
        ext = os.path.splitext(filename)[1].lower().replace(".", "")
        file_type = ext if ext else "unknown"

        try:
            new_file = File.create(
                filename=filename,
                storage_path=file_path,
                file_type=file_type,
                size_bytes=size_bytes,
                checksum_sha256=checksum
            )
            return new_file

        except Exception as e:
            db.session.rollback()
            os.remove(file_path)
            raise IllegalOperationError(f"DB error while saving file metadata: {e}")


    @staticmethod
    def _calculate_sha256(file_path):
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
