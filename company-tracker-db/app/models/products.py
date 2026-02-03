"""Product hierarchy history SQLAlchemy model."""

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Index, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ProductHierarchyHistory(Base):
    """
    Append-only history table for product hierarchy.

    Tracks a 3-level product classification hierarchy. Each product is
    identified by its class_3_id and belongs to a class_2 and class_1.
    """

    __tablename__ = "product_hierarchy_history"

    # Primary key
    record_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )

    # Business key
    product_class_3_id: Mapped[int] = mapped_column(Integer, nullable=False)

    # Business data - hierarchical classification
    class_level_1: Mapped[Optional[str]] = mapped_column(String(100))
    class_level_2: Mapped[Optional[str]] = mapped_column(String(100))
    class_level_3: Mapped[Optional[str]] = mapped_column(String(100))

    # Temporal tracking
    valid_from: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.current_timestamp()
    )
    valid_to: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    is_current: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default="true"
    )

    # Audit
    created_by: Mapped[Optional[str]] = mapped_column(String(100))

    __table_args__ = (
        # Partial index for fast current-state queries
        Index(
            "idx_product_current",
            "product_class_3_id",
            postgresql_where=(is_current == True),  # noqa: E712
        ),
        # Index for temporal queries
        Index(
            "idx_product_temporal",
            "product_class_3_id",
            valid_from.desc(),
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<ProductHierarchyHistory(record_id={self.record_id}, "
            f"product_class_3_id={self.product_class_3_id}, "
            f"class_3='{self.class_level_3}', is_current={self.is_current})>"
        )

    def to_dict(self) -> dict:
        """Convert to dictionary for comparison."""
        return {
            "class_level_1": self.class_level_1,
            "class_level_2": self.class_level_2,
            "class_level_3": self.class_level_3,
        }
