"""Shared model helpers: a timestamp mixin and a portable enum column type."""

from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import DateTime, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column


def db_enum(enum_cls: type[Enum]) -> SAEnum:
    """A SQLAlchemy Enum column that stores the enum *values* (lowercase strings).

    Portable across SQLite and PostgreSQL, and keeps stored data readable -
    e.g. "third_party" rather than the member name "THIRD_PARTY".
    """
    return SAEnum(enum_cls, values_callable=lambda e: [m.value for m in e])


class TimestampMixin:
    """Adds a UTC ``created_at`` timestamp, set when the row is inserted."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )