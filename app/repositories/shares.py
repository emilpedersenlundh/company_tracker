"""Product shares repository with upsert logic."""

from decimal import Decimal
from typing import Any

from sqlalchemy import and_, func, select

from app.models.shares import ProductSharesHistory
from app.repositories.base import BaseRepository


class SharesRepository(BaseRepository[ProductSharesHistory]):
    """Repository for product shares history data."""

    model = ProductSharesHistory

    def _get_business_key_filter(
        self,
        company_id: int,
        country_code: str,
        product_class_3_id: int,
        **kwargs: Any,
    ) -> Any:
        """Filter by composite business key."""
        return and_(
            ProductSharesHistory.company_id == company_id,
            ProductSharesHistory.country_code == country_code,
            ProductSharesHistory.product_class_3_id == product_class_3_id,
        )

    def _extract_business_data(self, record: ProductSharesHistory) -> dict[str, Any]:
        """Extract business data for comparison."""
        return {
            "share_percentage": record.share_percentage,
        }

    def _create_new_record(
        self,
        business_keys: dict[str, Any],
        data: dict[str, Any],
        created_by: str,
    ) -> ProductSharesHistory:
        """Create a new product shares record."""
        return ProductSharesHistory(
            company_id=business_keys["company_id"],
            country_code=business_keys["country_code"],
            product_class_3_id=business_keys["product_class_3_id"],
            share_percentage=data.get("share_percentage"),
            created_by=created_by,
        )

    async def upsert_share(
        self,
        company_id: int,
        country_code: str,
        product_class_3_id: int,
        share_percentage: Decimal | None = None,
        created_by: str = "system",
    ) -> tuple[int, bool]:
        """
        Upsert a product share record.

        Args:
            company_id: The company identifier
            country_code: 3-letter country code
            product_class_3_id: Product class identifier
            share_percentage: Market share percentage
            created_by: User performing the operation

        Returns:
            Tuple of (record_id, is_new)
        """
        return await self.upsert(
            business_keys={
                "company_id": company_id,
                "country_code": country_code,
                "product_class_3_id": product_class_3_id,
            },
            data={
                "share_percentage": share_percentage,
            },
            created_by=created_by,
        )

    async def get_share(
        self,
        company_id: int,
        country_code: str,
        product_class_3_id: int,
    ) -> ProductSharesHistory | None:
        """Get current share by business key."""
        return await self.get_current(
            company_id=company_id,
            country_code=country_code,
            product_class_3_id=product_class_3_id,
        )

    async def get_company_shares(
        self, company_id: int
    ) -> list[ProductSharesHistory]:
        """Get all current shares for a company."""
        stmt = (
            select(ProductSharesHistory)
            .where(
                and_(
                    ProductSharesHistory.company_id == company_id,
                    ProductSharesHistory.is_current == True,  # noqa: E712
                )
            )
            .order_by(
                ProductSharesHistory.country_code,
                ProductSharesHistory.product_class_3_id,
            )
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_shares(
        self,
        company_id: int | None = None,
        country_code: str | None = None,
        product_class_3_id: int | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[ProductSharesHistory]:
        """List current shares with optional filters."""
        stmt = select(ProductSharesHistory).where(
            ProductSharesHistory.is_current == True  # noqa: E712
        )

        if company_id is not None:
            stmt = stmt.where(ProductSharesHistory.company_id == company_id)
        if country_code is not None:
            stmt = stmt.where(ProductSharesHistory.country_code == country_code)
        if product_class_3_id is not None:
            stmt = stmt.where(
                ProductSharesHistory.product_class_3_id == product_class_3_id
            )

        stmt = (
            stmt.order_by(
                ProductSharesHistory.company_id,
                ProductSharesHistory.country_code,
            )
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_market_share_report(
        self,
        country_code: str | None = None,
        product_class_3_id: int | None = None,
    ) -> list[dict[str, Any]]:
        """
        Get aggregated market share report.

        Returns total share by company for given filters.
        """
        stmt = (
            select(
                ProductSharesHistory.company_id,
                ProductSharesHistory.country_code,
                func.sum(ProductSharesHistory.share_percentage).label("total_share"),
                func.count(ProductSharesHistory.product_class_3_id).label(
                    "product_count"
                ),
            )
            .where(ProductSharesHistory.is_current == True)  # noqa: E712
            .group_by(
                ProductSharesHistory.company_id,
                ProductSharesHistory.country_code,
            )
        )

        if country_code is not None:
            stmt = stmt.where(ProductSharesHistory.country_code == country_code)
        if product_class_3_id is not None:
            stmt = stmt.where(
                ProductSharesHistory.product_class_3_id == product_class_3_id
            )

        stmt = stmt.order_by(func.sum(ProductSharesHistory.share_percentage).desc())

        result = await self.session.execute(stmt)
        return [
            {
                "company_id": row.company_id,
                "country_code": row.country_code,
                "total_share": float(row.total_share) if row.total_share else 0.0,
                "product_count": row.product_count,
            }
            for row in result.all()
        ]
