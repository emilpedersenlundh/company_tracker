"""Pydantic schemas for request/response validation."""

from app.schemas.companies import (
    CompanyCreate,
    CompanyHistoryResponse,
    CompanyResponse,
    CompanyUpsertResponse,
)
from app.schemas.metrics import (
    MetricCreate,
    MetricHistoryResponse,
    MetricResponse,
    MetricUpsertResponse,
)
from app.schemas.products import (
    ProductCreate,
    ProductHistoryResponse,
    ProductResponse,
    ProductUpsertResponse,
)
from app.schemas.shares import (
    MarketShareReport,
    ShareCreate,
    ShareHistoryResponse,
    ShareResponse,
    ShareUpsertResponse,
)

__all__ = [
    # Companies
    "CompanyCreate",
    "CompanyResponse",
    "CompanyHistoryResponse",
    "CompanyUpsertResponse",
    # Metrics
    "MetricCreate",
    "MetricResponse",
    "MetricHistoryResponse",
    "MetricUpsertResponse",
    # Products
    "ProductCreate",
    "ProductResponse",
    "ProductHistoryResponse",
    "ProductUpsertResponse",
    # Shares
    "ShareCreate",
    "ShareResponse",
    "ShareHistoryResponse",
    "ShareUpsertResponse",
    "MarketShareReport",
]
