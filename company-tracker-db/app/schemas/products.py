"""Pydantic schemas for product hierarchy endpoints."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ProductBase(BaseModel):
    """Base schema with common product fields."""

    class_level_1: str | None = Field(None, max_length=100, description="Top-level classification")
    class_level_2: str | None = Field(None, max_length=100, description="Mid-level classification")
    class_level_3: str | None = Field(None, max_length=100, description="Bottom-level classification")


class ProductCreate(ProductBase):
    """Schema for creating/upserting a product hierarchy."""

    product_class_3_id: int = Field(..., gt=0, description="Unique product class 3 identifier")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "product_class_3_id": 101,
                "class_level_1": "Medical Devices",
                "class_level_2": "Diagnostic Equipment",
                "class_level_3": "Blood Glucose Monitors",
            }
        }
    )


class ProductResponse(ProductBase):
    """Schema for product response (current state)."""

    product_class_3_id: int
    valid_from: datetime

    model_config = ConfigDict(from_attributes=True)


class ProductHistoryResponse(ProductBase):
    """Schema for product history response (includes temporal fields)."""

    record_id: int
    product_class_3_id: int
    valid_from: datetime
    valid_to: datetime | None
    is_current: bool
    created_by: str | None

    model_config = ConfigDict(from_attributes=True)


class ProductUpsertResponse(BaseModel):
    """Schema for upsert operation response."""

    record_id: int = Field(..., description="The record ID")
    is_new: bool = Field(..., description="True if a new record was created")
    product_class_3_id: int

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "record_id": 1,
                "is_new": True,
                "product_class_3_id": 101,
            }
        }
    )
