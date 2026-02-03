"""Pydantic schemas for metrics endpoints."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class MetricBase(BaseModel):
    """Base schema with common metric fields."""

    revenue: Decimal | None = Field(None, ge=0, description="Revenue amount")
    gross_profit: Decimal | None = Field(None, description="Gross profit amount")
    headcount: int | None = Field(None, ge=0, description="Number of employees")


class MetricCreate(MetricBase):
    """Schema for creating/upserting a metric."""

    company_id: int = Field(..., gt=0, description="Company identifier")
    country_code: str = Field(
        ..., min_length=2, max_length=3, description="Country code (ISO 3166-1 alpha-2/3)"
    )
    year: int = Field(..., ge=1900, le=2100, description="Year for the metric")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "company_id": 1,
                "country_code": "DK",
                "year": 2024,
                "revenue": 150000000.00,
                "gross_profit": 85000000.00,
                "headcount": 5200,
            }
        }
    )


class MetricResponse(MetricBase):
    """Schema for metric response (current state)."""

    company_id: int
    country_code: str
    year: int
    valid_from: datetime

    model_config = ConfigDict(from_attributes=True)


class MetricHistoryResponse(MetricBase):
    """Schema for metric history response (includes temporal fields)."""

    record_id: int
    company_id: int
    country_code: str
    year: int
    valid_from: datetime
    valid_to: datetime | None
    is_current: bool
    created_by: str | None

    model_config = ConfigDict(from_attributes=True)


class MetricUpsertResponse(BaseModel):
    """Schema for upsert operation response."""

    record_id: int = Field(..., description="The record ID")
    is_new: bool = Field(..., description="True if a new record was created")
    company_id: int
    country_code: str
    year: int

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "record_id": 1,
                "is_new": True,
                "company_id": 1,
                "country_code": "DK",
                "year": 2024,
            }
        }
    )
