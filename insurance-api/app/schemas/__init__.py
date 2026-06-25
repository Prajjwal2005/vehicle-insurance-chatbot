"""Pydantic request/response schemas (the API's external contract)."""

from app.schemas.application import (
    ApplicationCreate,
    ApplicationRead,
    PolicySelect,
)
from app.schemas.claim import (
    ClaimCreate,
    ClaimRead,
    ClaimStatusRead,
    ClaimVerifyResult,
)
from app.schemas.customer import CustomerCreate, CustomerRead
from app.schemas.policy import PolicyProductRead
from app.schemas.vehicle import VehicleCreate, VehicleRead

__all__ = [
    "ApplicationCreate",
    "ApplicationRead",
    "PolicySelect",
    "ClaimCreate",
    "ClaimRead",
    "ClaimStatusRead",
    "ClaimVerifyResult",
    "CustomerCreate",
    "CustomerRead",
    "PolicyProductRead",
    "VehicleCreate",
    "VehicleRead",
]
