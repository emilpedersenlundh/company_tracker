"""Pydantic schemas for company endpoints."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class CompanyBase(BaseModel):
    """Base schema with common company fields."""

    company_name: str = Field(..., max_length=255, description="Company name")
    percentage_a: Decimal | None = Field(
        None, ge=0, le=1, decimal_places=4, description="Percentage A (0-1)"
    )
    percentage_b: Decimal | None = Field(
        None, ge=0, le=1, decimal_places=4, description="Percentage B (0-1)"
    )
    percentage_c: Decimal | None = Field(
        None, ge=0, le=1, decimal_places=4, description="Percentage C (0-1)"
    )


class CompanyCreate(CompanyBase):
    """Schema for creating/upserting a company."""

    company_id: int = Field(..., gt=0, description="Unique company identifier")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "company_id": 1,
                "company_name": "Novo Nordisk",
                "percentage_a": 0.25,
                "percentage_b": 0.35,
                "percentage_c": 0.40,
            }
        }
    )


class CompanyResponse(CompanyBase):
    """Schema for company response (current state)."""

    company_id: int
    valid_from: datetime

    model_config = ConfigDict(from_attributes=True)


class CompanyHistoryResponse(CompanyBase):
    """Schema for company history response (includes temporal fields)."""

    record_id: int
    company_id: int
    valid_from: datetime
    valid_to: datetime | None
    is_current: bool
    created_by: str | None

    model_config = ConfigDict(from_attributes=True)


class CompanyUpsertResponse(BaseModel):
    """Schema for upsert operation response."""

    record_id: int = Field(..., description="The record ID of the created/existing record")
    is_new: bool = Field(..., description="True if a new record was created, False if unchanged")
    company_id: int = Field(..., description="The company ID")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "record_id": 1,
                "is_new": True,
                "company_id": 1,
            }
        }
    )
