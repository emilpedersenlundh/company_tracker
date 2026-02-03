"""Company country metrics repository with upsert logic."""

from decimal import Decimal
from typing import Any

from sqlalchemy import and_, select

from app.models.metrics import CompanyCountryMetricsHistory
from app.repositories.base import BaseRepository


class MetricsRepository(BaseRepository[CompanyCountryMetricsHistory]):
    """Repository for company country metrics history data."""

    model = CompanyCountryMetricsHistory

    def _get_business_key_filter(
        self, company_id: int, country_code: str, year: int, **kwargs: Any
    ) -> Any:
        """Filter by composite business key."""
        return and_(
            CompanyCountryMetricsHistory.company_id == company_id,
            CompanyCountryMetricsHistory.country_code == country_code,
            CompanyCountryMetricsHistory.year == year,
        )

    def _extract_business_data(
        self, record: CompanyCountryMetricsHistory
    ) -> dict[str, Any]:
        """Extract business data for comparison."""
        return {
            "revenue": record.revenue,
            "gross_profit": record.gross_profit,
            "headcount": record.headcount,
        }

    def _create_new_record(
        self,
        business_keys: dict[str, Any],
        data: dict[str, Any],
        created_by: str,
    ) -> CompanyCountryMetricsHistory:
        """Create a new metrics history record."""
        return CompanyCountryMetricsHistory(
            company_id=business_keys["company_id"],
            country_code=business_keys["country_code"],
            year=business_keys["year"],
            revenue=data.get("revenue"),
            gross_profit=data.get("gross_profit"),
            headcount=data.get("headcount"),
            created_by=created_by,
        )

    async def upsert_metric(
        self,
        company_id: int,
        country_code: str,
        year: int,
        revenue: Decimal | None = None,
        gross_profit: Decimal | None = None,
        headcount: int | None = None,
        created_by: str = "system",
    ) -> tuple[int, bool]:
        """
        Upsert a company metric record.

        Args:
            company_id: The company identifier
            country_code: 3-letter country code
            year: The year for this metric
            revenue: Revenue amount
            gross_profit: Gross profit amount
            headcount: Number of employees
            created_by: User performing the operation

        Returns:
            Tuple of (record_id, is_new)
        """
        return await self.upsert(
            business_keys={
                "company_id": company_id,
                "country_code": country_code,
                "year": year,
            },
            data={
                "revenue": revenue,
                "gross_profit": gross_profit,
                "headcount": headcount,
            },
            created_by=created_by,
        )

    async def get_metric(
        self, company_id: int, country_code: str, year: int
    ) -> CompanyCountryMetricsHistory | None:
        """Get current metric by business key."""
        return await self.get_current(
            company_id=company_id, country_code=country_code, year=year
        )

    async def get_company_metrics(
        self, company_id: int
    ) -> list[CompanyCountryMetricsHistory]:
        """Get all current metrics for a company."""
        stmt = (
            select(CompanyCountryMetricsHistory)
            .where(
                and_(
                    CompanyCountryMetricsHistory.company_id == company_id,
                    CompanyCountryMetricsHistory.is_current == True,  # noqa: E712
                )
            )
            .order_by(
                CompanyCountryMetricsHistory.year.desc(),
                CompanyCountryMetricsHistory.country_code,
            )
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_metrics(
        self,
        company_id: int | None = None,
        country_code: str | None = None,
        year: int | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[CompanyCountryMetricsHistory]:
        """List current metrics with optional filters."""
        stmt = select(CompanyCountryMetricsHistory).where(
            CompanyCountryMetricsHistory.is_current == True  # noqa: E712
        )

        if company_id is not None:
            stmt = stmt.where(CompanyCountryMetricsHistory.company_id == company_id)
        if country_code is not None:
            stmt = stmt.where(CompanyCountryMetricsHistory.country_code == country_code)
        if year is not None:
            stmt = stmt.where(CompanyCountryMetricsHistory.year == year)

        stmt = (
            stmt.order_by(
                CompanyCountryMetricsHistory.company_id,
                CompanyCountryMetricsHistory.year.desc(),
            )
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
