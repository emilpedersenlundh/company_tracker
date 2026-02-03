"""Pytest fixtures and test database setup."""

import asyncio
from collections.abc import AsyncGenerator, Generator
from typing import Any

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app

# Use in-memory SQLite for tests (with async support)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def test_engine() -> AsyncGenerator[Any, None]:
    """Create test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )

    # Enable foreign keys for SQLite
    @event.listens_for(engine.sync_engine, "connect")
    def set_sqlite_pragma(dbapi_connection: Any, connection_record: Any) -> None:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def test_session(
    test_engine: Any,
) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session."""
    async_session_factory = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

    async with async_session_factory() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def client(test_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create test HTTP client with database override."""

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        try:
            yield test_session
            await test_session.commit()
        except Exception:
            await test_session.rollback()
            raise

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def sample_company() -> dict[str, Any]:
    """Sample company data for tests."""
    return {
        "company_id": 1,
        "company_name": "Novo Nordisk",
        "percentage_a": "0.2500",
        "percentage_b": "0.3500",
        "percentage_c": "0.4000",
    }


@pytest.fixture
def sample_metric() -> dict[str, Any]:
    """Sample metric data for tests."""
    return {
        "company_id": 1,
        "country_code": "DK",
        "year": 2024,
        "revenue": "150000000.00",
        "gross_profit": "85000000.00",
        "headcount": 5200,
    }


@pytest.fixture
def sample_product() -> dict[str, Any]:
    """Sample product data for tests."""
    return {
        "product_class_3_id": 101,
        "class_level_1": "Medical Devices",
        "class_level_2": "Diagnostic Equipment",
        "class_level_3": "Blood Glucose Monitors",
    }


@pytest.fixture
def sample_share() -> dict[str, Any]:
    """Sample share data for tests."""
    return {
        "company_id": 1,
        "country_code": "DK",
        "product_class_3_id": 101,
        "share_percentage": "0.3250",
    }
