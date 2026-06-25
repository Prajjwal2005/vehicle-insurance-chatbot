"""Claim model: a claim filed against a valid policy number."""

from datetime import datetime

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.common import TimestampMixin, db_enum
from app.models.enums import ClaimStatus


class Claim(TimestampMixin, Base):
    __tablename__ = "claims"

    id: Mapped[int] = mapped_column(primary_key=True)
    # Loose coupling by design: a claim stores the policy number it relates to,
    # and the service layer validates that the number exists. This keeps the
    # claim flow independent of the applications table structure.
    policy_number: Mapped[str] = mapped_column(String(40), index=True)

    accident_location: Mapped[str] = mapped_column(String(200))
    accident_time: Mapped[datetime]
    accident_description: Mapped[str] = mapped_column(Text)

    status: Mapped[ClaimStatus] = mapped_column(
        db_enum(ClaimStatus), default=ClaimStatus.DRAFT
    )
    claim_number: Mapped[str | None] = mapped_column(
        String(40), unique=True, nullable=True
    )
