"""Validated runtime configuration for PackageMind AI."""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration loaded from environment variables and local defaults."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "PackageMind AI"
    environment: Literal["development", "production", "test"] = "development"
    database_path: Path = Path("packagemind.db")

    request_timeout_seconds: float = Field(default=15.0, gt=0, le=60)

    gemini_api_key: str | None = None
    gemini_model: str = "gemini-3.6-flash"
    ai_summary_max_output_tokens: int = Field(default=900, ge=200, le=2_000)

    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"


@lru_cache
def get_settings() -> Settings:
    """Create and cache application settings for the current process."""

    return Settings()


settings = get_settings()
