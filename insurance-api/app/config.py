"""Application settings, loaded from environment variables / .env."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration for the Insurance System API.

    Values come from environment variables (case-insensitive) or a local .env
    file. Field defaults make the app runnable with zero configuration.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Insurance System API"
    database_url: str = "sqlite+aiosqlite:///./insurance.db"


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance (read .env only once)."""
    return Settings()
