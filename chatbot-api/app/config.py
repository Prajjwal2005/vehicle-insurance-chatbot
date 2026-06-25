"""Application settings for the chatbot service."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration loaded from environment variables / .env.

    google_api_key defaults to empty so a missing key fails loudly at the
    connectivity check rather than silently.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Insurance Chatbot API"
    google_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash-lite"
    insurance_api_url: str = "http://127.0.0.1:8001"


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance (read .env only once)."""
    return Settings()