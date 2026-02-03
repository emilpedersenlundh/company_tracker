"""Metrics API endpoints."""

from fastapi import APIRouter, Header, HTTPException, Query

from app.config import get_settings
from app.database import DbSession
from app.repositories.metrics import MetricsRepository
from app.schemas.metrics import (
    MetricCreate,
    MetricResponse,
    MetricUpsertResponse,
)

router = APIRouter(prefix="/api/metrics", tags=["Metrics"])
settings = get_settings()


@router.post(
    "",
    response_model=MetricUpsertResponse,
    summary="Upsert a metric",
    description="Create or update company metrics for a country/year.",
)
async def upsert_metric(
    metric: MetricCreate,
    db: DbSession,
    x_user: str = Header(default=None, alias="X-User"),
) -> MetricUpsertResponse:
    """
    Upsert a company metric record.

    Business key: company_id + country_code + year
    """
    repo = MetricsRepository(db)
    created_by = x_user or settings.default_user

    record_id, is_new = await repo.upsert_metric(
        company_id=metric.company_id,
        country_code=metric.country_code,
        year=metric.year,
        revenue=metric.revenue,
        gross_profit=metric.gross_profit,
        headcount=metric.headcount,
        created_by=created_by,
    )

    return MetricUpsertResponse(
        record_id=record_id,
        is_new=is_new,
        company_id=metric.company_id,
        country_code=metric.country_code,
        year=metric.year,
    )


@router.get(
    "",
    response_model=list[MetricResponse],
    summary="List metrics with filters",
)
async def list_metrics(
    db: DbSession,
    company_id: int | None = Query(None, description="Filter by company"),
    country_code: str | None = Query(None, description="Filter by country"),
    year: int | None = Query(None, description="Filter by year"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
) -> list[MetricResponse]:
    """List current metrics with optional filters."""
    repo = MetricsRepository(db)
    metrics = await repo.list_metrics(
        company_id=company_id,
        country_code=country_code,
        year=year,
        limit=limit,
        offset=offset,
    )
    return [MetricResponse.model_validate(m) for m in metrics]


@router.get(
    "/{company_id}/{country_code}/{year}",
    response_model=MetricResponse,
    summary="Get specific metric",
)
async def get_metric(
    company_id: int,
    country_code: str,
    year: int,
    db: DbSession,
) -> MetricResponse:
    """Get a specific metric by business key."""
    repo = MetricsRepository(db)
    metric = await repo.get_metric(company_id, country_code, year)

    if metric is None:
        raise HTTPException(
            status_code=404,
            detail=f"Metric not found for company {company_id}, {country_code}, {year}",
        )

    return MetricResponse.model_validate(metric)


# Also mount on companies router for convenience
companies_metrics_router = APIRouter(
    prefix="/api/companies/{company_id}/metrics",
    tags=["Companies", "Metrics"],
)


@companies_metrics_router.get(
    "",
    response_model=list[MetricResponse],
    summary="Get company metrics",
)
async def get_company_metrics(
    company_id: int,
    db: DbSession,
) -> list[MetricResponse]:
    """Get all metrics for a specific company."""
    repo = MetricsRepository(db)
    metrics = await repo.get_company_metrics(company_id)
    return [MetricResponse.model_validate(m) for m in metrics]
