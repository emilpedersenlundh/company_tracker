"""Application configuration using Pydantic Settings."""

import logging
from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Ignore extra fields from .env (e.g., POSTGRES_* for docker-compose)
    )

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/company_tracker"
    database_url_sync: str = "postgresql://postgres:postgres@localhost:5432/company_tracker"

    # Application
    app_env: Literal["development", "staging", "production"] = "development"
    debug: bool = True
    log_level: str = "INFO"

    # Default user for audit tracking
    default_user: str = "system"

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.app_env == "development"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


def configure_logging(settings: Settings) -> None:
    """Configure application logging."""
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
