"""Application model: a customer's request to insure a vehicle.

Starts as a draft, then becomes 'submitted' on confirmation — at which point a
unique policy_number is generated. That policy number is what claims reference.
"""

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from typing import TYPE_CHECKING

from app.database import Base
from app.models.common import TimestampMixin, db_enum
from app.models.enums import ApplicationStatus, CoverageType

if TYPE_CHECKING:
    from app.models.customer import Customer
    from app.models.policy_product import PolicyProduct
    from app.models.vehicle import Vehicle


class Application(TimestampMixin, Base):
    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"))
    vehicle_id: Mapped[int] = mapped_column(ForeignKey("vehicles.id"))

    coverage_type: Mapped[CoverageType] = mapped_column(db_enum(CoverageType))
    addon_rent_a_car: Mapped[bool] = mapped_column(default=False)

    status: Mapped[ApplicationStatus] = mapped_column(
        db_enum(ApplicationStatus), default=ApplicationStatus.DRAFT
    )
    # Null until the customer selects a plan / confirms the application.
    selected_product_id: Mapped[int | None] = mapped_column(
        ForeignKey("policy_products.id"), nullable=True
    )
    policy_number: Mapped[str | None] = mapped_column(
        String(40), unique=True, nullable=True
    )

    customer: Mapped["Customer"] = relationship(back_populates="applications")
    vehicle: Mapped["Vehicle"] = relationship(back_populates="applications")
    selected_product: Mapped["PolicyProduct | None"] = relationship()
