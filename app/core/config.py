from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    PROJECT_NAME: str = "Football Intelligence App"
    API_V1_PREFIX: str = "/api/v1"

    # Postgres/SQLAlchemy models in app/models and app/crud/base.py are kept for a future
    # migration but are not on the active request path right now (see DATA_DIR below).
    DATABASE_URL: str = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/football_intelligence"
    )

    # Active backend: flat CSV files under DATA_DIR, one per entity. Override via env var
    # to point at a Render persistent disk mount (e.g. /var/data) — the default path lives
    # inside the repo checkout, which most hosts (including Render's default ephemeral disk)
    # wipe on every deploy/restart.
    DATA_DIR: str = str(BASE_DIR / "data")

    CORS_ORIGINS: list[str] = ["*"]


settings = Settings()
