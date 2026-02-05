"""Application configuration using Pydantic Settings."""

import logging
from functools import lru_cache
from typing import Literal

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

SQLITE_URL = "sqlite+aiosqlite:///company_tracker.db"
SQLITE_URL_SYNC = "sqlite:///company_tracker.db"
POSTGRES_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/company_tracker"
POSTGRES_URL_SYNC = "postgresql://postgres:postgres@localhost:5432/company_tracker"


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Ignore extra fields from .env (e.g., POSTGRES_* for docker-compose)
    )

    # Database (resolved automatically from app_env if not set explicitly)
    database_url: str | None = None
    database_url_sync: str | None = None

    # Application
    app_env: Literal["development", "staging", "production"] = "development"
    debug: bool = True
    log_level: str = "INFO"

    # Default user for audit tracking
    default_user: str = "system"

    @model_validator(mode="after")
    def _resolve_database_urls(self) -> "Settings":
        """Set database URLs based on app_env when not explicitly provided."""
        if self.app_env == "production":
            if self.database_url is None:
                self.database_url = POSTGRES_URL
            if self.database_url_sync is None:
                self.database_url_sync = POSTGRES_URL_SYNC
        else:
            if self.database_url is None:
                self.database_url = SQLITE_URL
            if self.database_url_sync is None:
                self.database_url_sync = SQLITE_URL_SYNC
        return self

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.app_env == "development"

    @property
    def is_sqlite(self) -> bool:
        """Check if using SQLite database."""
        return self.database_url.startswith("sqlite")


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
