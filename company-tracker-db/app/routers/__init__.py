"""FastAPI routers for API endpoints."""

from app.routers.companies import router as companies_router
from app.routers.metrics import router as metrics_router
from app.routers.products import router as products_router
from app.routers.shares import router as shares_router

__all__ = [
    "companies_router",
    "metrics_router",
    "products_router",
    "shares_router",
]
