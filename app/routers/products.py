"""Product hierarchy API endpoints."""

from datetime import datetime

from fastapi import APIRouter, Header, HTTPException, Query

from app.config import get_settings
from app.database import DbSession
from app.repositories.products import ProductRepository
from app.schemas.products import (
    ProductCreate,
    ProductHistoryResponse,
    ProductResponse,
    ProductUpsertResponse,
)

router = APIRouter(prefix="/api/products", tags=["Products"])
settings = get_settings()


@router.post(
    "",
    response_model=ProductUpsertResponse,
    summary="Upsert a product hierarchy",
    description="Create or update a product classification hierarchy.",
)
async def upsert_product(
    product: ProductCreate,
    db: DbSession,
    x_user: str = Header(default=None, alias="X-User"),
) -> ProductUpsertResponse:
    """
    Upsert a product hierarchy record.

    Business key: product_class_3_id
    """
    repo = ProductRepository(db)
    created_by = x_user or settings.default_user

    record_id, is_new = await repo.upsert_product(
        product_class_3_id=product.product_class_3_id,
        class_level_1=product.class_level_1,
        class_level_2=product.class_level_2,
        class_level_3=product.class_level_3,
        created_by=created_by,
    )

    return ProductUpsertResponse(
        record_id=record_id,
        is_new=is_new,
        product_class_3_id=product.product_class_3_id,
    )


@router.get(
    "",
    response_model=list[ProductResponse],
    summary="List current products",
)
async def list_products(
    db: DbSession,
    class_level_1: str | None = Query(None, description="Filter by level 1"),
    class_level_2: str | None = Query(None, description="Filter by level 2"),
    name: str | None = Query(None, description="Filter by name (level 3 contains)"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
) -> list[ProductResponse]:
    """List current products with optional filters."""
    repo = ProductRepository(db)
    products = await repo.search_products(
        class_level_1=class_level_1,
        class_level_2=class_level_2,
        name_contains=name,
        limit=limit,
        offset=offset,
    )
    return [ProductResponse.model_validate(p) for p in products]


@router.get(
    "/{product_class_3_id}",
    response_model=ProductResponse,
    summary="Get product by ID",
)
async def get_product(
    product_class_3_id: int,
    db: DbSession,
) -> ProductResponse:
    """Get the current state of a product by ID."""
    repo = ProductRepository(db)
    product = await repo.get_product(product_class_3_id)

    if product is None:
        raise HTTPException(
            status_code=404, detail=f"Product {product_class_3_id} not found"
        )

    return ProductResponse.model_validate(product)


@router.get(
    "/{product_class_3_id}/history",
    response_model=list[ProductHistoryResponse],
    summary="Get product history",
)
async def get_product_history(
    product_class_3_id: int,
    db: DbSession,
) -> list[ProductHistoryResponse]:
    """Get full history of a product (all versions)."""
    repo = ProductRepository(db)
    history = await repo.get_product_history(product_class_3_id)

    if not history:
        raise HTTPException(
            status_code=404, detail=f"Product {product_class_3_id} not found"
        )

    return [ProductHistoryResponse.model_validate(h) for h in history]


@router.get(
    "/{product_class_3_id}/at/{date}",
    response_model=ProductHistoryResponse,
    summary="Get product at point in time",
)
async def get_product_at_point_in_time(
    product_class_3_id: int,
    date: datetime,
    db: DbSession,
) -> ProductHistoryResponse:
    """Get the product state at a specific point in time."""
    repo = ProductRepository(db)
    product = await repo.get_at_point_in_time(date, product_class_3_id=product_class_3_id)

    if product is None:
        raise HTTPException(
            status_code=404,
            detail=f"Product {product_class_3_id} not found at {date.isoformat()}",
        )

    return ProductHistoryResponse.model_validate(product)
