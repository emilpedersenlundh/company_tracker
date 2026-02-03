"""Product shares history SQLAlchemy model."""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import Boolean, DateTime, Index, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ProductSharesHistory(Base):
    """
    Append-only history table for product market shares.

    Tracks what percentage of market share a company has for a specific
    product in a specific country.
    """

    __tablename__ = "product_shares_history"

    # Primary key
    record_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )

    # Composite business key
    company_id: Mapped[int] = mapped_column(Integer, nullable=False)
    country_code: Mapped[str] = mapped_column(String(3), nullable=False)
    product_class_3_id: Mapped[int] = mapped_column(Integer, nullable=False)

    # Business data
    share_percentage: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 4))

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
            "idx_shares_current",
            "company_id",
            "country_code",
            "product_class_3_id",
            postgresql_where=(is_current == True),  # noqa: E712
        ),
        # Index for temporal queries
        Index(
            "idx_shares_temporal",
            "company_id",
            "country_code",
            "product_class_3_id",
            valid_from.desc(),
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<ProductSharesHistory(record_id={self.record_id}, "
            f"company_id={self.company_id}, country={self.country_code}, "
            f"product={self.product_class_3_id}, share={self.share_percentage}, "
            f"is_current={self.is_current})>"
        )

    def to_dict(self) -> dict:
        """Convert to dictionary for comparison."""
        return {
            "share_percentage": self.share_percentage,
        }
