#!/usr/bin/env python3
"""Database initialization script."""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text

from app.config import get_settings
from app.database import Base, engine


async def init_database() -> None:
    """Initialize the database with all tables."""
    settings = get_settings()
    print(f"Initializing database: {settings.database_url}")

    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
        print("Tables created successfully.")

        # Verify tables exist
        result = await conn.execute(
            text(
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_schema = 'public'"
            )
        )
        tables = [row[0] for row in result.fetchall()]
        print(f"Created tables: {tables}")


if __name__ == "__main__":
    asyncio.run(init_database())
