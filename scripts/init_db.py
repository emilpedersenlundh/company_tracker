#!/usr/bin/env python3
"""Database initialization script."""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import inspect, text

from app.config import get_settings
from app.database import Base, engine
import app.models  # noqa: F401 — register all models with Base.metadata


async def init_database() -> None:
    """Initialize the database with all tables."""
    settings = get_settings()
    print(f"Initializing database: {settings.database_url}")

    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)

        # Verify tables exist
        tables = await conn.run_sync(
            lambda sync_conn: inspect(sync_conn).get_table_names()
        )
        print(f"Tables ready: {tables}")


if __name__ == "__main__":
    asyncio.run(init_database())
