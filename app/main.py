"""FastAPI application initialization."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import configure_logging, get_settings
from app.routers.companies import router as companies_router
from app.routers.metrics import companies_metrics_router, router as metrics_router
from app.routers.products import router as products_router
from app.routers.shares import (
    companies_shares_router,
    reports_router,
    router as shares_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler for startup/shutdown."""
    settings = get_settings()
    configure_logging(settings)
    yield


settings = get_settings()

app = FastAPI(
    title="Company Tracker API",
    description="""
    Temporal data management API for tracking companies, metrics, products, and market shares.

    ## Features

    - **Append-only temporal pattern**: All changes are tracked with full history
    - **Point-in-time queries**: Query data as it was at any moment in time
    - **Audit trail**: All changes include created_by tracking
    - **No data deletion**: Data is never deleted, only superseded

    ## Upsert Logic

    When you POST/PUT data:
    1. If no current record exists, a new record is created
    2. If current record exists and data changed, the old record is closed and a new one created
    3. If current record exists and data is unchanged, no operation is performed

    The response indicates whether a new record was created (`is_new: true`) or not.
    """,
    version="0.1.0",
    lifespan=lifespan,
    debug=settings.debug,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.is_development else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(companies_router)
app.include_router(companies_metrics_router)
app.include_router(companies_shares_router)
app.include_router(metrics_router)
app.include_router(products_router)
app.include_router(shares_router)
app.include_router(reports_router)


@app.get("/health", tags=["Health"])
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/", tags=["Root"])
async def root() -> dict[str, str]:
    """Root endpoint with API info."""
    return {
        "name": "Company Tracker API",
        "version": "0.1.0",
        "docs": "/docs",
        "openapi": "/openapi.json",
    }
