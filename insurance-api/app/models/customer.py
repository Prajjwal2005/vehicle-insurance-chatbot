"""Customer model: the person applying for insurance."""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

from app.database import Base
from app.models.common import TimestampMixin

if TYPE_CHECKING:
    from app.models.vehicle import Vehicle
    from app.models.application import Application


class Customer(TimestampMixin, Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    phone: Mapped[str] = mapped_column(String(40))
    email: Mapped[str] = mapped_column(String(160))
    address: Mapped[str] = mapped_column(String(300))

    # A customer can own several vehicles and lodge several applications.
    vehicles: Mapped[list["Vehicle"]] = relationship(
        back_populates="customer", cascade="all, delete-orphan"
    )
    applications: Mapped[list["Application"]] = relationship(
        back_populates="customer", cascade="all, delete-orphan"
    )
