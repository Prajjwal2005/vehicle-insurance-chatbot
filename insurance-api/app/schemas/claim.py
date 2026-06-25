"""Claim request/response schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import ClaimStatus
from app.schemas.common import ORMModel


class ClaimCreate(BaseModel):
    """Payload to open a draft claim (policy number + accident details)."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "policy_number": "POL-2026-00001",
                    "accident_location": "Sheikh Zayed Road",
                    "accident_time": "2026-06-20T15:30:00",
                    "accident_description": "Rear-ended at a traffic light.",
                }
            ]
        }
    )

    policy_number: str = Field(min_length=1, max_length=40)
    accident_location: str = Field(min_length=1, max_length=200)
    accident_time: datetime
    accident_description: str = Field(min_length=1)


class ClaimRead(ORMModel):
    id: int
    policy_number: str
    accident_location: str
    accident_time: datetime
    accident_description: str
    status: ClaimStatus
    claim_number: str | None


class ClaimVerifyResult(BaseModel):
    """Result of validating a draft claim's policy number."""

    valid: bool
    policy_number: str
    message: str


class ClaimStatusRead(ORMModel):
    """Compact status view returned by the status-check endpoint."""

    claim_number: str | None
    status: ClaimStatus
