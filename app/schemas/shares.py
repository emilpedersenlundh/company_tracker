"""Pydantic schemas for product shares endpoints."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ShareBase(BaseModel):
    """Base schema with common share fields."""

    share_percentage: Decimal | None = Field(
        None, ge=0, le=1, decimal_places=4, description="Market share percentage (0-1)"
    )


class ShareCreate(ShareBase):
    """Schema for creating/upserting a product share."""

    company_id: int = Field(..., gt=0, description="Company identifier")
    country_code: str = Field(
        ..., min_length=2, max_length=3, description="Country code"
    )
    product_class_3_id: int = Field(..., gt=0, description="Product class identifier")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "company_id": 1,
                "country_code": "DK",
                "product_class_3_id": 101,
                "share_percentage": 0.3250,
            }
        }
    )


class ShareResponse(ShareBase):
    """Schema for share response (current state)."""

    company_id: int
    country_code: str
    product_class_3_id: int
    valid_from: datetime

    model_config = ConfigDict(from_attributes=True)


class ShareHistoryResponse(ShareBase):
    """Schema for share history response (includes temporal fields)."""

    record_id: int
    company_id: int
    country_code: str
    product_class_3_id: int
    valid_from: datetime
    valid_to: datetime | None
    is_current: bool
    created_by: str | None

    model_config = ConfigDict(from_attributes=True)


class ShareUpsertResponse(BaseModel):
    """Schema for upsert operation response."""

    record_id: int = Field(..., description="The record ID")
    is_new: bool = Field(..., description="True if a new record was created")
    company_id: int
    country_code: str
    product_class_3_id: int

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "record_id": 1,
                "is_new": True,
                "company_id": 1,
                "country_code": "DK",
                "product_class_3_id": 101,
            }
        }
    )


class MarketShareReport(BaseModel):
    """Schema for aggregated market share report."""

    company_id: int
    country_code: str
    total_share: float = Field(..., description="Total market share across products")
    product_count: int = Field(..., description="Number of products")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "company_id": 1,
                "country_code": "DK",
                "total_share": 0.65,
                "product_count": 5,
            }
        }
    )
