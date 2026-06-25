"""Routes for the apply-for-insurance flow."""

from fastapi import APIRouter, Depends, status

from app import services
from app.dependencies import SessionDep, get_current_user
from app.schemas import (
    ApplicationCreate,
    ApplicationRead,
    PolicyProductRead,
    PolicySelect,
)


router = APIRouter(
    prefix="/applications",
    tags=["applications"],
    dependencies=[Depends(get_current_user)],
)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_application(
    payload: ApplicationCreate, session: SessionDep
) -> ApplicationRead:
    """Open a draft application from customer + vehicle + coverage details."""
    application = await services.create_draft_application(session, payload)
    return ApplicationRead.model_validate(application)


@router.get("/{application_id}")
async def read_application(application_id: int, session: SessionDep) -> ApplicationRead:
    """Fetch a single application."""
    application = await services.get_application(session, application_id)
    return ApplicationRead.model_validate(application)


@router.get("/{application_id}/policies")
async def list_application_policies(
    application_id: int, session: SessionDep
) -> list[PolicyProductRead]:
    """List the plans applicable to this application's coverage type."""
    products = await services.list_applicable_policies(session, application_id)
    return [PolicyProductRead.model_validate(p) for p in products]


@router.patch("/{application_id}")
async def select_application_policy(
    application_id: int, payload: PolicySelect, session: SessionDep
) -> ApplicationRead:
    """Choose a plan for a draft application."""
    application = await services.select_policy(
        session, application_id, payload.selected_product_id
    )
    return ApplicationRead.model_validate(application)


@router.post("/{application_id}/confirm")
async def confirm_application(
    application_id: int, session: SessionDep
) -> ApplicationRead:
    """Submit the application and generate its policy number."""
    application = await services.confirm_application(session, application_id)
    return ApplicationRead.model_validate(application)
