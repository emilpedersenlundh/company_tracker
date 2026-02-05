"""Product hierarchy repository with upsert logic."""

from typing import Any

from sqlalchemy import select

from app.models.products import ProductHierarchyHistory
from app.repositories.base import BaseRepository


class ProductRepository(BaseRepository[ProductHierarchyHistory]):
    """Repository for product hierarchy history data."""

    model = ProductHierarchyHistory

    def _get_business_key_filter(
        self, product_class_3_id: int, **kwargs: Any
    ) -> Any:
        """Filter by product_class_3_id business key."""
        return ProductHierarchyHistory.product_class_3_id == product_class_3_id

    def _extract_business_data(self, record: ProductHierarchyHistory) -> dict[str, Any]:
        """Extract business data for comparison."""
        return {
            "class_level_1": record.class_level_1,
            "class_level_2": record.class_level_2,
            "class_level_3": record.class_level_3,
        }

    def _create_new_record(
        self,
        business_keys: dict[str, Any],
        data: dict[str, Any],
        created_by: str,
    ) -> ProductHierarchyHistory:
        """Create a new product hierarchy record."""
        return ProductHierarchyHistory(
            product_class_3_id=business_keys["product_class_3_id"],
            class_level_1=data.get("class_level_1"),
            class_level_2=data.get("class_level_2"),
            class_level_3=data.get("class_level_3"),
            created_by=created_by,
        )

    async def upsert_product(
        self,
        product_class_3_id: int,
        class_level_1: str | None = None,
        class_level_2: str | None = None,
        class_level_3: str | None = None,
        created_by: str = "system",
    ) -> tuple[int, bool]:
        """
        Upsert a product hierarchy record.

        Args:
            product_class_3_id: The unique product class 3 identifier
            class_level_1: Top-level classification
            class_level_2: Mid-level classification
            class_level_3: Bottom-level classification
            created_by: User performing the operation

        Returns:
            Tuple of (record_id, is_new)
        """
        return await self.upsert(
            business_keys={"product_class_3_id": product_class_3_id},
            data={
                "class_level_1": class_level_1,
                "class_level_2": class_level_2,
                "class_level_3": class_level_3,
            },
            created_by=created_by,
        )

    async def get_product(
        self, product_class_3_id: int
    ) -> ProductHierarchyHistory | None:
        """Get current product by product_class_3_id."""
        return await self.get_current(product_class_3_id=product_class_3_id)

    async def get_product_history(
        self, product_class_3_id: int
    ) -> list[ProductHierarchyHistory]:
        """Get full history for a product."""
        return await self.get_history(product_class_3_id=product_class_3_id)

    async def search_products(
        self,
        class_level_1: str | None = None,
        class_level_2: str | None = None,
        name_contains: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[ProductHierarchyHistory]:
        """Search current products with optional filters."""
        stmt = select(ProductHierarchyHistory).where(
            ProductHierarchyHistory.is_current == True  # noqa: E712
        )

        if class_level_1:
            stmt = stmt.where(ProductHierarchyHistory.class_level_1 == class_level_1)
        if class_level_2:
            stmt = stmt.where(ProductHierarchyHistory.class_level_2 == class_level_2)
        if name_contains:
            stmt = stmt.where(
                ProductHierarchyHistory.class_level_3.like(f"%{name_contains}%")
            )

        stmt = (
            stmt.order_by(
                ProductHierarchyHistory.class_level_1,
                ProductHierarchyHistory.class_level_2,
                ProductHierarchyHistory.class_level_3,
            )
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
