"""Business logic for the claim flow."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Application, Claim
from app.models.enums import ApplicationStatus, ClaimStatus
from app.schemas import ClaimCreate
from app.services.exceptions import ConflictError, NotFoundError
from app.services.numbering import generate_claim_number


async def _get_claim(session: AsyncSession, claim_id: int) -> Claim:
    claim = await session.get(Claim, claim_id)
    if claim is None:
        raise NotFoundError(f"Claim {claim_id} not found")
    return claim


async def _policy_number_is_valid(session: AsyncSession, policy_number: str) -> bool:
    """A policy number is valid only if it belongs to a submitted application."""
    stmt = select(Application.id).where(
        Application.policy_number == policy_number,
        Application.status == ApplicationStatus.SUBMITTED,
    )
    return (await session.execute(stmt)).first() is not None


async def create_draft_claim(session: AsyncSession, data: ClaimCreate) -> Claim:
    """Create a draft claim from the policy number and accident details."""
    claim = Claim(**data.model_dump())
    session.add(claim)
    await session.commit()
    await session.refresh(claim)
    return claim


async def verify_claim(session: AsyncSession, claim_id: int) -> tuple[Claim, bool]:
    """Check that the draft claim's policy number is valid."""
    claim = await _get_claim(session, claim_id)
    valid = await _policy_number_is_valid(session, claim.policy_number)
    return claim, valid


async def confirm_claim(session: AsyncSession, claim_id: int) -> Claim:
    """Submit a draft claim (after validating its policy number) and number it."""
    claim = await _get_claim(session, claim_id)
    if claim.status != ClaimStatus.DRAFT:
        raise ConflictError("Claim is already submitted")
    if not await _policy_number_is_valid(session, claim.policy_number):
        raise ConflictError(f"Policy number {claim.policy_number} is not valid")
    claim.status = ClaimStatus.SUBMITTED
    claim.claim_number = generate_claim_number(claim.id)
    await session.commit()
    await session.refresh(claim)
    return claim


async def get_claim_status(session: AsyncSession, claim_number: str) -> Claim:
    """Look up a claim by its claim number."""
    stmt = select(Claim).where(Claim.claim_number == claim_number)
    claim = (await session.execute(stmt)).scalar_one_or_none()
    if claim is None:
        raise NotFoundError(f"Claim {claim_number} not found")
    return claim
