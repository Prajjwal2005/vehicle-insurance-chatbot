"""Vehicle request/response schemas."""

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class VehicleCreate(BaseModel):
    """Vehicle details collected when starting an application."""

    make: str = Field(min_length=1, max_length=60)
    model: str = Field(min_length=1, max_length=60)
    year: int = Field(ge=1900, le=2100)
    mileage: int = Field(ge=0)
    vin: str = Field(min_length=11, max_length=17)


class VehicleRead(ORMModel):
    id: int
    make: str
    model: str
    year: int
    mileage: int
    vin: str
