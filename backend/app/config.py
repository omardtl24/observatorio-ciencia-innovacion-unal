import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # DB CONFIG
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT", 5432)
    DB_NAME = os.getenv("DB_NAME")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")

    # PostgreSQL URI
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ---- AUTH0 ----
    AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
    AUTH0_CLIENT_ID = os.getenv("AUTH0_CLIENT_ID")
    AUTH0_CLIENT_SECRET = os.getenv("AUTH0_CLIENT_SECRET")
    AUTH0_CALLBACK_URL = os.getenv("AUTH0_CALLBACK_URL")

    # ---- SECURITY ----
    RESTRICTED_EMAIL_DOMAIN = os.getenv("RESTRICTED_EMAIL_DOMAIN")
    FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY")
    FRONTEND_URL = os.getenv("FRONTEND_URL")