import os
from dotenv import load_dotenv # type: ignore

load_dotenv()
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    # DB CONFIG
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT", 5432)
    DB_NAME = os.getenv("DB_NAME")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")

    # ---- POSTGRESQL URI --------
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ---- AUTH0 ----
    AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
    AUTH0_CLIENT_ID = os.getenv("AUTH0_CLIENT_ID")
    AUTH0_CLIENT_SECRET = os.getenv("AUTH0_CLIENT_SECRET")
    AUTH0_CALLBACK_URL = os.getenv("AUTH0_CALLBACK_URL")

    # ---- LOOKER STUDIO / OAUTH ----
    CLIENT_ID = os.getenv("CLIENT_ID")
    CLIENT_SECRET = os.getenv("CLIENT_SECRET")
    REDIRECT_URI = os.getenv("REDIRECT_URI")
    REFRESH_TOKEN = os.getenv("REFRESH_TOKEN")

    # ---- FILE STORAGE ----
    _FILE_STORAGE_ROOT_ENV = os.getenv("FILE_STORAGE_ROOT", "files")
    FILE_STORAGE_ROOT = (
        _FILE_STORAGE_ROOT_ENV
        if os.path.isabs(_FILE_STORAGE_ROOT_ENV)
        else os.path.join(BASE_DIR, _FILE_STORAGE_ROOT_ENV)
    )
    RESOURCES_SHARED_FOLDER = os.path.join(FILE_STORAGE_ROOT, "shiny-apps")
    RESOURCES_BASE_URL = os.getenv("RESOURCES_BASE_URL", "")
    PROFILE_IMAGE_CACHE_DIR = os.path.join(FILE_STORAGE_ROOT, "profile_images_cache")
    PROFILE_IMAGE_CACHE_TTL_SECONDS = int(os.getenv("PROFILE_IMAGE_CACHE_TTL_SECONDS", "86400"))
    PROFILE_IMAGE_CLEANUP_INTERVAL_SECONDS = int(os.getenv("PROFILE_IMAGE_CLEANUP_INTERVAL_SECONDS", "900"))

    # Grace period before an unlinked file is considered orphaned (protects files
    # mid-upload-flow, not yet attached to their owning entity) and how often the
    # background job checks for them.
    ORPHANED_FILES_GRACE_PERIOD_SECONDS = int(os.getenv("ORPHANED_FILES_GRACE_PERIOD_SECONDS", "86400"))
    ORPHANED_FILES_CLEANUP_INTERVAL_SECONDS = int(os.getenv("ORPHANED_FILES_CLEANUP_INTERVAL_SECONDS", "3600"))

    # ---- SECURITY ----
    RESTRICTED_EMAIL_DOMAIN = os.getenv("RESTRICTED_EMAIL_DOMAIN")
    FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY")
    FRONTEND_URL = os.getenv("FRONTEND_URL")
    DEFAULT_ADMIN_EMAIL = os.getenv("DEFAULT_ADMIN_EMAIL")
    TEST = os.getenv("TEST", "false").lower() == "true"
    OAUTH_STATE_TTL_SECONDS = int(os.getenv("OAUTH_STATE_TTL_SECONDS", "300"))
    SESSION_LIFETIME_SECONDS = int(os.getenv("SESSION_LIFETIME_SECONDS", "7200"))

    # --- PROD ----
    POPULATE = os.getenv("POPULATE", "false").lower() == "true"

    SHINY_CONTAINER_NAME = os.getenv("SHINY_CONTAINER_NAME", "app_shiny_dev")


class TestingConfig(Config):
    """Configuration for testing."""
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    TEST = True
    POPULATE = False
    JWT_SECRET_KEY = "test-secret-key"
    PROFILE_IMAGE_CACHE_TTL_SECONDS = 60
    PROFILE_IMAGE_CLEANUP_INTERVAL_SECONDS = 60
    ORPHANED_FILES_GRACE_PERIOD_SECONDS = 60
    ORPHANED_FILES_CLEANUP_INTERVAL_SECONDS = 60
    OAUTH_STATE_TTL_SECONDS = 300
    SESSION_LIFETIME_SECONDS = 7200