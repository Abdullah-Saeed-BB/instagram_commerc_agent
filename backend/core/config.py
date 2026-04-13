from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ── Database ───────────────────────────────
    DATABASE_URL: str

    # ── Meta / Instagram ───────────────────────
    META_VERIFY_TOKEN: str
    META_PAGE_ACCESS_TOKEN: str
    META_APP_SECRET: str
    INSTAGRAM_ACCOUNT_ID: str

    # ── App ────────────────────────────────────
    APP_ENV: str = "development"
    DEBUG: bool = True


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance (reads .env once)."""
    return Settings()
