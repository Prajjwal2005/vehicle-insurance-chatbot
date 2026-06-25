"""Vehicle model: the car being insured, owned by a customer."""

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.common import TimestampMixin

if TYPE_CHECKING:
    from app.models.application import Application
    from app.models.customer import Customer


class Vehicle(TimestampMixin, Base):
    __tablename__ = "vehicles"

    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"))
    make: Mapped[str] = mapped_column(String(60))
    model: Mapped[str] = mapped_column(String(60))
    year: Mapped[int]
    mileage: Mapped[int]
    vin: Mapped[str] = mapped_column(String(40))

    customer: Mapped["Customer"] = relationship(back_populates="vehicles")
    applications: Mapped[list["Application"]] = relationship(
        back_populates="vehicle"
    )
