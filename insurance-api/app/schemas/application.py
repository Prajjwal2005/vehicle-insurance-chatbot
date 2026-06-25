"""Application request/response schemas."""

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import ApplicationStatus, CoverageType
from app.schemas.common import ORMModel
from app.schemas.customer import CustomerCreate, CustomerRead
from app.schemas.policy import PolicyProductRead
from app.schemas.vehicle import VehicleCreate, VehicleRead


class ApplicationCreate(BaseModel):
    """Payload to open a draft application (step i of the apply flow)."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "customer": {
                        "name": "Jane Doe",
                        "phone": "+971 50 1234567",
                        "email": "jane@example.com",
                        "address": "Dubai Marina",
                    },
                    "vehicle": {
                        "make": "Toyota",
                        "model": "Corolla",
                        "year": 2020,
                        "mileage": 30000,
                        "vin": "1HGCM82633A004352",
                    },
                    "coverage_type": "full",
                    "addon_rent_a_car": True,
                }
            ]
        }
    )

    customer: CustomerCreate
    vehicle: VehicleCreate
    coverage_type: CoverageType
    addon_rent_a_car: bool = False


class PolicySelect(BaseModel):
    """Payload to choose a plan for a draft application (step iii)."""

    model_config = ConfigDict(
        json_schema_extra={"examples": [{"selected_product_id": 2}]}
    )

    selected_product_id: int = Field(gt=0)


class ApplicationRead(ORMModel):
    """Full application view, with related objects nested in."""

    id: int
    status: ApplicationStatus
    coverage_type: CoverageType
    addon_rent_a_car: bool
    selected_product_id: int | None
    policy_number: str | None
    customer: CustomerRead
    vehicle: VehicleRead
    selected_product: PolicyProductRead | None
