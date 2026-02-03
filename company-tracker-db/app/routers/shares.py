"""Product shares API endpoints."""

from fastapi import APIRouter, Header, HTTPException, Query

from app.config import get_settings
from app.database import DbSession
from app.repositories.shares import SharesRepository
from app.schemas.shares import (
    MarketShareReport,
    ShareCreate,
    ShareResponse,
    ShareUpsertResponse,
)

router = APIRouter(prefix="/api/shares", tags=["Shares"])
settings = get_settings()


@router.post(
    "",
    response_model=ShareUpsertResponse,
    summary="Upsert a product share",
    description="Create or update a product market share.",
)
async def upsert_share(
    share: ShareCreate,
    db: DbSession,
    x_user: str = Header(default=None, alias="X-User"),
) -> ShareUpsertResponse:
    """
    Upsert a product share record.

    Business key: company_id + country_code + product_class_3_id
    """
    repo = SharesRepository(db)
    created_by = x_user or settings.default_user

    record_id, is_new = await repo.upsert_share(
        company_id=share.company_id,
        country_code=share.country_code,
        product_class_3_id=share.product_class_3_id,
        share_percentage=share.share_percentage,
        created_by=created_by,
    )

    return ShareUpsertResponse(
        record_id=record_id,
        is_new=is_new,
        company_id=share.company_id,
        country_code=share.country_code,
        product_class_3_id=share.product_class_3_id,
    )


@router.get(
    "",
    response_model=list[ShareResponse],
    summary="List shares with filters",
)
async def list_shares(
    db: DbSession,
    company_id: int | None = Query(None, description="Filter by company"),
    country_code: str | None = Query(None, description="Filter by country"),
    product_class_3_id: int | None = Query(None, description="Filter by product"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
) -> list[ShareResponse]:
    """List current shares with optional filters."""
    repo = SharesRepository(db)
    shares = await repo.list_shares(
        company_id=company_id,
        country_code=country_code,
        product_class_3_id=product_class_3_id,
        limit=limit,
        offset=offset,
    )
    return [ShareResponse.model_validate(s) for s in shares]


@router.get(
    "/{company_id}/{country_code}/{product_class_3_id}",
    response_model=ShareResponse,
    summary="Get specific share",
)
async def get_share(
    company_id: int,
    country_code: str,
    product_class_3_id: int,
    db: DbSession,
) -> ShareResponse:
    """Get a specific share by business key."""
    repo = SharesRepository(db)
    share = await repo.get_share(company_id, country_code, product_class_3_id)

    if share is None:
        raise HTTPException(
            status_code=404,
            detail=f"Share not found for company {company_id}, {country_code}, product {product_class_3_id}",
        )

    return ShareResponse.model_validate(share)


# Company shares endpoint
companies_shares_router = APIRouter(
    prefix="/api/companies/{company_id}/shares",
    tags=["Companies", "Shares"],
)


@companies_shares_router.get(
    "",
    response_model=list[ShareResponse],
    summary="Get company's product shares",
)
async def get_company_shares(
    company_id: int,
    db: DbSession,
) -> list[ShareResponse]:
    """Get all current product shares for a company."""
    repo = SharesRepository(db)
    shares = await repo.get_company_shares(company_id)
    return [ShareResponse.model_validate(s) for s in shares]


# Market share report endpoint
reports_router = APIRouter(prefix="/api/reports", tags=["Reports"])


@reports_router.get(
    "/market-share",
    response_model=list[MarketShareReport],
    summary="Aggregated market share report",
)
async def get_market_share_report(
    db: DbSession,
    country_code: str | None = Query(None, description="Filter by country"),
    product_class_3_id: int | None = Query(None, description="Filter by product"),
) -> list[MarketShareReport]:
    """
    Get aggregated market share report.

    Shows total share by company/country with product count.
    """
    repo = SharesRepository(db)
    report = await repo.get_market_share_report(
        country_code=country_code,
        product_class_3_id=product_class_3_id,
    )
    return [MarketShareReport.model_validate(r) for r in report]
