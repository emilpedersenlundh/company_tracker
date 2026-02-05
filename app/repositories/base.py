"""Base repository with common append-only upsert logic."""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Generic, TypeVar

from sqlalchemy import and_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(ABC, Generic[ModelType]):
    """
    Base repository implementing the append-only temporal pattern.

    The upsert logic:
    1. Query for the current record (is_current=True)
    2. Compare values to detect changes
    3. If changed: close old record (is_current=False, valid_to=now)
    4. Insert new record (is_current=True)
    5. Return the record_id
    """

    model: type[ModelType]

    def __init__(self, session: AsyncSession):
        """Initialize repository with database session."""
        self.session = session

    @abstractmethod
    def _get_business_key_filter(self, **kwargs: Any) -> Any:
        """Return SQLAlchemy filter for the business key columns."""
        pass

    @abstractmethod
    def _extract_business_data(self, record: ModelType) -> dict[str, Any]:
        """Extract business data fields for comparison."""
        pass

    @abstractmethod
    def _create_new_record(
        self, business_keys: dict[str, Any], data: dict[str, Any], created_by: str
    ) -> ModelType:
        """Create a new model instance with given data."""
        pass

    async def get_current(self, **business_keys: Any) -> ModelType | None:
        """Get the current version of a record by business key."""
        stmt = select(self.model).where(
            and_(
                self._get_business_key_filter(**business_keys),
                self.model.is_current == True,  # noqa: E712
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_record_id(self, record_id: int) -> ModelType | None:
        """Get a specific record version by its record_id."""
        stmt = select(self.model).where(self.model.record_id == record_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_history(self, **business_keys: Any) -> list[ModelType]:
        """Get all versions of a record, ordered by valid_from descending."""
        stmt = (
            select(self.model)
            .where(self._get_business_key_filter(**business_keys))
            .order_by(self.model.valid_from.desc(), self.model.record_id.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_at_point_in_time(
        self, point_in_time: datetime, **business_keys: Any
    ) -> ModelType | None:
        """Get the record version that was current at a specific point in time."""
        stmt = (
            select(self.model)
            .where(
                and_(
                    self._get_business_key_filter(**business_keys),
                    self.model.valid_from <= point_in_time,
                    (self.model.valid_to > point_in_time) | (self.model.valid_to.is_(None)),
                )
            )
            .order_by(self.model.valid_from.desc())
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_current(self, limit: int = 100, offset: int = 0) -> list[ModelType]:
        """List all current records with pagination."""
        stmt = (
            select(self.model)
            .where(self.model.is_current == True)  # noqa: E712
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def upsert(
        self,
        business_keys: dict[str, Any],
        data: dict[str, Any],
        created_by: str = "system",
    ) -> tuple[int, bool]:
        """
        Upsert a record using the append-only pattern.

        Args:
            business_keys: The business key fields that identify the entity
            data: The data fields to insert/update
            created_by: Username for audit tracking

        Returns:
            Tuple of (record_id, is_new) where is_new indicates if a new
            record was created (True) or no change was needed (False)
        """
        # Get current record
        current = await self.get_current(**business_keys)

        if current is not None:
            # Compare data to detect changes
            current_data = self._extract_business_data(current)

            # Normalize for comparison (handle Decimal, etc.)
            has_changes = self._compare_data(current_data, data)

            if not has_changes:
                # No change, return existing record_id
                return current.record_id, False

            # Close the current record
            now = datetime.utcnow()
            stmt = (
                update(self.model)
                .where(
                    and_(
                        self._get_business_key_filter(**business_keys),
                        self.model.is_current == True,  # noqa: E712
                    )
                )
                .values(is_current=False, valid_to=now)
            )
            await self.session.execute(stmt)

        # Insert new record with explicit valid_from for consistent timestamps
        # (SQLite's CURRENT_TIMESTAMP has only second-level precision)
        new_record = self._create_new_record(business_keys, data, created_by)
        new_record.valid_from = datetime.utcnow()
        self.session.add(new_record)
        await self.session.flush()  # Get the record_id

        return new_record.record_id, True

    def _compare_data(
        self, current_data: dict[str, Any], new_data: dict[str, Any]
    ) -> bool:
        """
        Compare current data with new data to detect changes.

        Uses IS DISTINCT FROM semantics (NULL-safe comparison).
        Returns True if there are changes, False otherwise.
        """
        for key, new_value in new_data.items():
            current_value = current_data.get(key)

            # NULL-safe comparison
            if current_value is None and new_value is None:
                continue
            if current_value is None or new_value is None:
                return True

            # Handle Decimal comparison
            if hasattr(current_value, "__float__") and hasattr(new_value, "__float__"):
                if float(current_value) != float(new_value):
                    return True
            elif current_value != new_value:
                return True

        return False
