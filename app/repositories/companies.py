"""Company repository with upsert logic."""

from decimal import Decimal
from typing import Any

from sqlalchemy import select

from app.models.companies import CompanyHistory
from app.repositories.base import BaseRepository


class CompanyRepository(BaseRepository[CompanyHistory]):
    """Repository for company history data."""

    model = CompanyHistory

    def _get_business_key_filter(self, company_id: int, **kwargs: Any) -> Any:
        """Filter by company_id business key."""
        return CompanyHistory.company_id == company_id

    def _extract_business_data(self, record: CompanyHistory) -> dict[str, Any]:
        """Extract business data for comparison."""
        return {
            "company_name": record.company_name,
            "percentage_a": record.percentage_a,
            "percentage_b": record.percentage_b,
            "percentage_c": record.percentage_c,
        }

    def _create_new_record(
        self,
        business_keys: dict[str, Any],
        data: dict[str, Any],
        created_by: str,
    ) -> CompanyHistory:
        """Create a new company history record."""
        return CompanyHistory(
            company_id=business_keys["company_id"],
            company_name=data["company_name"],
            percentage_a=data.get("percentage_a"),
            percentage_b=data.get("percentage_b"),
            percentage_c=data.get("percentage_c"),
            created_by=created_by,
        )

    async def upsert_company(
        self,
        company_id: int,
        company_name: str,
        percentage_a: Decimal | None = None,
        percentage_b: Decimal | None = None,
        percentage_c: Decimal | None = None,
        created_by: str = "system",
    ) -> tuple[int, bool]:
        """
        Upsert a company record.

        Args:
            company_id: The unique company identifier
            company_name: Company name
            percentage_a: Optional percentage A
            percentage_b: Optional percentage B
            percentage_c: Optional percentage C
            created_by: User performing the operation

        Returns:
            Tuple of (record_id, is_new)
        """
        return await self.upsert(
            business_keys={"company_id": company_id},
            data={
                "company_name": company_name,
                "percentage_a": percentage_a,
                "percentage_b": percentage_b,
                "percentage_c": percentage_c,
            },
            created_by=created_by,
        )

    async def get_company(self, company_id: int) -> CompanyHistory | None:
        """Get current company by company_id."""
        return await self.get_current(company_id=company_id)

    async def get_company_history(self, company_id: int) -> list[CompanyHistory]:
        """Get full history for a company."""
        return await self.get_history(company_id=company_id)

    async def search_companies(
        self,
        name_contains: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[CompanyHistory]:
        """Search current companies with optional name filter."""
        stmt = select(CompanyHistory).where(
            CompanyHistory.is_current == True  # noqa: E712
        )

        if name_contains:
            stmt = stmt.where(CompanyHistory.company_name.like(f"%{name_contains}%"))

        stmt = stmt.order_by(CompanyHistory.company_name).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
