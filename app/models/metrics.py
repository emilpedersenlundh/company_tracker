"""Company country metrics history SQLAlchemy model."""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import Boolean, DateTime, Index, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class CompanyCountryMetricsHistory(Base):
    """
    Append-only history table for company metrics by country and year.

    Tracks financial metrics (revenue, gross profit) and headcount for
    companies operating in different countries over different years.
    """

    __tablename__ = "company_country_metrics_history"

    # Primary key
    record_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )

    # Composite business key
    company_id: Mapped[int] = mapped_column(Integer, nullable=False)
    country_code: Mapped[str] = mapped_column(String(3), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)

    # Business data
    revenue: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2))
    gross_profit: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2))
    headcount: Mapped[Optional[int]] = mapped_column(Integer)

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
            "idx_metrics_current",
            "company_id",
            "country_code",
            "year",
            postgresql_where=(is_current == True),  # noqa: E712
        ),
        # Index for temporal queries
        Index(
            "idx_metrics_temporal",
            "company_id",
            "country_code",
            "year",
            valid_from.desc(),
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<CompanyCountryMetricsHistory(record_id={self.record_id}, "
            f"company_id={self.company_id}, country={self.country_code}, "
            f"year={self.year}, is_current={self.is_current})>"
        )

    def to_dict(self) -> dict:
        """Convert to dictionary for comparison."""
        return {
            "revenue": self.revenue,
            "gross_profit": self.gross_profit,
            "headcount": self.headcount,
        }
