"""Environment configuration.

Every setting the app needs is read (and validated) here, once, at import
time, so a missing variable fails fast with a clear message instead of
surfacing as a confusing error deep inside SQLAlchemy or PyJWT.
"""

import os

from dotenv import load_dotenv

load_dotenv()


def _require(name: str) -> str:
    value = os.getenv(name)

    if not value:
        raise RuntimeError(
            f"{name} is not set. Copy .env.example to .env and fill it in."
        )

    return value


DATABASE_URL = _require("DATABASE_URL")

SECRET_KEY = _require("SECRET_KEY")

ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
    if origin.strip()
]
