"""Company API endpoints."""

from datetime import datetime

from fastapi import APIRouter, Header, HTTPException, Query

from app.config import get_settings
from app.database import DbSession
from app.repositories.companies import CompanyRepository
from app.schemas.companies import (
    CompanyCreate,
    CompanyHistoryResponse,
    CompanyResponse,
    CompanyUpsertResponse,
)

router = APIRouter(prefix="/api/companies", tags=["Companies"])
settings = get_settings()


@router.post(
    "",
    response_model=CompanyUpsertResponse,
    summary="Upsert a company",
    description="Create a new company or update an existing one. Uses append-only pattern.",
)
async def upsert_company(
    company: CompanyCreate,
    db: DbSession,
    x_user: str = Header(default=None, alias="X-User"),
) -> CompanyUpsertResponse:
    """
    Upsert a company record.

    If the company exists and data has changed, closes the current record
    and creates a new one. If no change, returns the existing record.
    """
    repo = CompanyRepository(db)
    created_by = x_user or settings.default_user

    record_id, is_new = await repo.upsert_company(
        company_id=company.company_id,
        company_name=company.company_name,
        percentage_a=company.percentage_a,
        percentage_b=company.percentage_b,
        percentage_c=company.percentage_c,
        created_by=created_by,
    )

    return CompanyUpsertResponse(
        record_id=record_id,
        is_new=is_new,
        company_id=company.company_id,
    )


@router.get(
    "",
    response_model=list[CompanyResponse],
    summary="List all current companies",
)
async def list_companies(
    db: DbSession,
    name: str | None = Query(None, description="Filter by name (contains)"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
) -> list[CompanyResponse]:
    """List all current companies with optional name filter."""
    repo = CompanyRepository(db)
    companies = await repo.search_companies(
        name_contains=name, limit=limit, offset=offset
    )
    return [CompanyResponse.model_validate(c) for c in companies]


@router.get(
    "/{company_id}",
    response_model=CompanyResponse,
    summary="Get current company state",
)
async def get_company(
    company_id: int,
    db: DbSession,
) -> CompanyResponse:
    """Get the current state of a company by ID."""
    repo = CompanyRepository(db)
    company = await repo.get_company(company_id)

    if company is None:
        raise HTTPException(status_code=404, detail=f"Company {company_id} not found")

    return CompanyResponse.model_validate(company)


@router.get(
    "/{company_id}/history",
    response_model=list[CompanyHistoryResponse],
    summary="Get company history",
)
async def get_company_history(
    company_id: int,
    db: DbSession,
) -> list[CompanyHistoryResponse]:
    """Get full history of a company (all versions)."""
    repo = CompanyRepository(db)
    history = await repo.get_company_history(company_id)

    if not history:
        raise HTTPException(status_code=404, detail=f"Company {company_id} not found")

    return [CompanyHistoryResponse.model_validate(h) for h in history]


@router.get(
    "/{company_id}/at/{date}",
    response_model=CompanyHistoryResponse,
    summary="Get company at point in time",
)
async def get_company_at_point_in_time(
    company_id: int,
    date: datetime,
    db: DbSession,
) -> CompanyHistoryResponse:
    """Get the company state at a specific point in time."""
    repo = CompanyRepository(db)
    company = await repo.get_at_point_in_time(date, company_id=company_id)

    if company is None:
        raise HTTPException(
            status_code=404,
            detail=f"Company {company_id} not found at {date.isoformat()}",
        )

    return CompanyHistoryResponse.model_validate(company)
