"""PolicyProduct model: a plan in the catalogue that customers choose from.

These rows are seeded once (see seed.py); they are the products listed back to
the customer after a draft application is created.
"""

from sqlalchemy import JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.common import db_enum
from app.models.enums import CoverageType


class PolicyProduct(Base):
    __tablename__ = "policy_products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    coverage_type: Mapped[CoverageType] = mapped_column(db_enum(CoverageType))
    base_price: Mapped[float]
    # A list of human-readable feature strings, e.g. ["Roadside assistance", ...].
    features: Mapped[list[str]] = mapped_column(JSON, default=list)
    description: Mapped[str] = mapped_column(String(300), default="")
