"""Routes for the claim flow."""

from fastapi import APIRouter, Depends, status

from app import services
from app.dependencies import SessionDep, get_current_user
from app.schemas import ClaimCreate, ClaimRead, ClaimStatusRead, ClaimVerifyResult

router = APIRouter(
    prefix="/claims",
    tags=["claims"],
    dependencies=[Depends(get_current_user)],
)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_claim(payload: ClaimCreate, session: SessionDep) -> ClaimRead:
    """Open a draft claim from a policy number and accident details."""
    claim = await services.create_draft_claim(session, payload)
    return ClaimRead.model_validate(claim)


@router.post("/{claim_id}/verify")
async def verify_claim(claim_id: int, session: SessionDep) -> ClaimVerifyResult:
    """Check that the draft claim's policy number is valid."""
    claim, valid = await services.verify_claim(session, claim_id)
    message = "Policy number is valid." if valid else "Policy number was not found."
    return ClaimVerifyResult(
        valid=valid, policy_number=claim.policy_number, message=message
    )


@router.post("/{claim_id}/confirm")
async def confirm_claim(claim_id: int, session: SessionDep) -> ClaimRead:
    """Submit the claim and generate its claim number."""
    claim = await services.confirm_claim(session, claim_id)
    return ClaimRead.model_validate(claim)


@router.get("/{claim_number}")
async def read_claim_status(
    claim_number: str, session: SessionDep
) -> ClaimStatusRead:
    """Return a claim's status by its claim number."""
    claim = await services.get_claim_status(session, claim_number)
    return ClaimStatusRead.model_validate(claim)
