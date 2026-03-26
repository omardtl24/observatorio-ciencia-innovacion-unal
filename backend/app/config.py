import os
from dotenv import load_dotenv

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
    FILE_STORAGE_ROOT = os.path.join(
        BASE_DIR, os.getenv("FILE_STORAGE_ROOT")
    )
    PROFILE_IMAGE_CACHE_DIR = os.path.join(FILE_STORAGE_ROOT, "profile_images_cache")
    PROFILE_IMAGE_CACHE_TTL_SECONDS = int(os.getenv("PROFILE_IMAGE_CACHE_TTL_SECONDS", "86400"))
    PROFILE_IMAGE_CLEANUP_INTERVAL_SECONDS = int(os.getenv("PROFILE_IMAGE_CLEANUP_INTERVAL_SECONDS", "900"))

    # ---- SECURITY ----
    RESTRICTED_EMAIL_DOMAIN = os.getenv("RESTRICTED_EMAIL_DOMAIN")
    FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY")
    FRONTEND_URL = os.getenv("FRONTEND_URL")
    DEFAULT_ADMIN_EMAIL = os.getenv("DEFAULT_ADMIN_EMAIL")
    TEST = os.getenv("TEST", "false").lower() == "true"
    OAUTH_STATE_TTL_SECONDS = int(os.getenv("OAUTH_STATE_TTL_SECONDS", "300"))
    SESSION_LIFETIME_SECONDS = int(os.getenv("SESSION_LIFETIME_SECONDS", "7200"))


class TestingConfig(Config):
    """Configuration for testing."""
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    TEST = True
    JWT_SECRET_KEY = "test-secret-key"
    PROFILE_IMAGE_CACHE_TTL_SECONDS = 60
    PROFILE_IMAGE_CLEANUP_INTERVAL_SECONDS = 60
    OAUTH_STATE_TTL_SECONDS = 300
    SESSION_LIFETIME_SECONDS = 7200