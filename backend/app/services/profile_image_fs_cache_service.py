import glob
import hashlib
import mimetypes
import os
import tempfile
import threading
import time
from pathlib import Path

import requests


class ProfileImageFsCacheService:
    @staticmethod
    def build_image_id(user_id: str) -> str:
        normalized = (user_id or "").strip().lower()
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

    @staticmethod
    def _cache_root() -> str:
        from flask import current_app # type: ignore

        root = current_app.config.get("PROFILE_IMAGE_CACHE_DIR")
        os.makedirs(root, exist_ok=True)
        return root

    @classmethod
    def _cache_subdir(cls, image_id: str) -> str:
        root = cls._cache_root()
        subdir = os.path.join(root, image_id[:2], image_id[2:4])
        os.makedirs(subdir, exist_ok=True)
        return subdir

    @classmethod
    def _image_glob(cls, image_id: str) -> str:
        return os.path.join(cls._cache_subdir(image_id), f"{image_id}.*")

    @classmethod
    def _find_image_path(cls, image_id: str):
        candidates = [
            path
            for path in glob.glob(cls._image_glob(image_id))
            if not path.endswith(".lock")
        ]
        return candidates[0] if candidates else None

    @classmethod
    def _lock_path(cls, image_id: str) -> str:
        return os.path.join(cls._cache_subdir(image_id), f"{image_id}.lock")

    @classmethod
    def _acquire_file_lock(cls, image_id: str, wait_timeout_seconds: int = 10):
        lock_path = cls._lock_path(image_id)
        deadline = time.time() + wait_timeout_seconds

        while time.time() < deadline:
            try:
                fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.close(fd)
                return lock_path
            except FileExistsError:
                time.sleep(0.05)

        raise TimeoutError("Could not acquire profile image cache lock")

    @staticmethod
    def _release_file_lock(lock_path: str):
        try:
            os.remove(lock_path)
        except FileNotFoundError:
            pass

    @staticmethod
    def _extension_from_content_type(content_type: str) -> str:
        guessed = mimetypes.guess_extension(content_type) or ".img"
        if guessed == ".jpe":
            return ".jpg"
        return guessed

    @classmethod
    def cache_profile_image_at_login(cls, user_id: str, image_url: str):
        if not image_url:
            return None

        image_id = cls.build_image_id(user_id)
        lock_path = cls._acquire_file_lock(image_id)

        try:
            response = requests.get(image_url, timeout=12)
            response.raise_for_status()

            content_type = (response.headers.get("Content-Type") or "application/octet-stream").split(";")[0].strip().lower()
            if not content_type.startswith("image/"):
                raise ValueError("External profile URL did not return image content")

            subdir = cls._cache_subdir(image_id)
            extension = cls._extension_from_content_type(content_type)
            final_path = os.path.join(subdir, f"{image_id}{extension}")

            with tempfile.NamedTemporaryFile(delete=False, dir=subdir) as temp_file:
                temp_file.write(response.content)
                temp_path = temp_file.name

            for existing in glob.glob(os.path.join(subdir, f"{image_id}.*")):
                if existing != final_path and not existing.endswith(".lock"):
                    try:
                        os.remove(existing)
                    except FileNotFoundError:
                        pass

            os.replace(temp_path, final_path)
            os.utime(final_path, None)
            return image_id
        finally:
            cls._release_file_lock(lock_path)

    @classmethod
    def resolve_image_path(cls, image_id: str):
        return cls._find_image_path(image_id)

    @staticmethod
    def touch_image(path: str):
        os.utime(path, None)

    @staticmethod
    def guess_content_type(path: str) -> str:
        content_type, _ = mimetypes.guess_type(path)
        return content_type or "application/octet-stream"

    @classmethod
    def cleanup_expired_images(cls, ttl_seconds: int = 86400):
        root = Path(cls._cache_root())
        if not root.exists():
            return 0

        now = time.time()
        removed = 0

        for file_path in root.rglob("*"):
            if not file_path.is_file():
                continue
            if file_path.name.endswith(".lock"):
                continue

            try:
                age_seconds = now - file_path.stat().st_mtime
                if age_seconds > ttl_seconds:
                    file_path.unlink(missing_ok=True)
                    removed += 1
            except FileNotFoundError:
                continue
            except Exception:
                continue

        return removed


def start_profile_image_cleanup_daemon(app):
    interval_seconds = int(app.config.get("PROFILE_IMAGE_CLEANUP_INTERVAL_SECONDS", 900))
    ttl_seconds = int(app.config.get("PROFILE_IMAGE_CACHE_TTL_SECONDS", 86400))

    def _run_forever():
        while True:
            try:
                with app.app_context():
                    ProfileImageFsCacheService.cleanup_expired_images(ttl_seconds=ttl_seconds)
            except Exception as exc:
                app.logger.warning(f"Profile image cleanup iteration failed: {str(exc)}")
            time.sleep(interval_seconds)

    thread = threading.Thread(target=_run_forever, daemon=True)
    thread.start()
