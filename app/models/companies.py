"""Company history SQLAlchemy model."""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import Boolean, DateTime, Index, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class CompanyHistory(Base):
    """
    Append-only history table for companies.

    Each company can have multiple records over time. Only the record with
    is_current=True represents the current state. When data changes, the
    current record is closed (is_current=False, valid_to=now) and a new
    record is inserted.
    """

    __tablename__ = "companies_history"

    # Primary key - unique per record version
    record_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )

    # Business key - identifies the company across versions
    company_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)

    # Business data
    company_name: Mapped[str] = mapped_column(String(255), nullable=False)
    percentage_a: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 4))
    percentage_b: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 4))
    percentage_c: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 4))

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
            "idx_companies_current",
            "company_id",
            postgresql_where=(is_current == True),  # noqa: E712
        ),
        # Index for temporal queries
        Index("idx_companies_temporal", "company_id", valid_from.desc(), "valid_to"),
    )

    def __repr__(self) -> str:
        return (
            f"<CompanyHistory(record_id={self.record_id}, "
            f"company_id={self.company_id}, name='{self.company_name}', "
            f"is_current={self.is_current})>"
        )

    def to_dict(self) -> dict:
        """Convert to dictionary for comparison."""
        return {
            "company_name": self.company_name,
            "percentage_a": self.percentage_a,
            "percentage_b": self.percentage_b,
            "percentage_c": self.percentage_c,
        }
