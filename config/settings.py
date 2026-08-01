"""Application configuration loaded from environment variables."""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Validated runtime configuration for SafePkgAI."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "SafePkgAI"
    environment: Literal["development", "production", "test"] = "development"
    database_path: Path = Path("safepkgai.db")

    request_timeout_seconds: float = Field(default=15.0, gt=0, le=60)
    # Limit archive size before extraction to reduce resource-exhaustion risk.
    max_archive_size_bytes: int = Field(
        default=50 * 1024 * 1024,
        gt=0,
        le=200 * 1024 * 1024,
    )

    openai_api_key: str | None = None
    openai_model: str = "gpt-5.6-terra"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"


@lru_cache
def get_settings() -> Settings:
    """Create and cache the application settings once per process."""

    return Settings()


settings = get_settings()