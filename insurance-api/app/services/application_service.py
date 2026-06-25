"""Business logic for the application (apply-for-insurance) flow."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Application, Customer, PolicyProduct, Vehicle
from app.models.enums import ApplicationStatus
from app.schemas import ApplicationCreate
from app.services.exceptions import ConflictError, NotFoundError
from app.services.numbering import generate_policy_number


async def get_application(session: AsyncSession, application_id: int) -> Application:
    """Fetch an application with its related objects eagerly loaded.

    selectinload avoids async lazy-loading errors when the response schema
    reads application.customer / .vehicle / .selected_product.
    """
    stmt = (
        select(Application)
        .where(Application.id == application_id)
        .options(
            selectinload(Application.customer),
            selectinload(Application.vehicle),
            selectinload(Application.selected_product),
        )
    )
    application = (await session.execute(stmt)).scalar_one_or_none()
    if application is None:
        raise NotFoundError(f"Application {application_id} not found")
    return application


async def create_draft_application(
    session: AsyncSession, data: ApplicationCreate
) -> Application:
    """Create a customer, a vehicle and a draft application in one step."""
    customer = Customer(**data.customer.model_dump())
    vehicle = Vehicle(customer=customer, **data.vehicle.model_dump())
    application = Application(
        customer=customer,
        vehicle=vehicle,
        coverage_type=data.coverage_type,
        addon_rent_a_car=data.addon_rent_a_car,
    )
    session.add(application)  # cascades to the new customer and vehicle
    await session.commit()
    return await get_application(session, application.id)


async def list_applicable_policies(
    session: AsyncSession, application_id: int
) -> list[PolicyProduct]:
    """List catalogue plans matching the application's coverage type."""
    application = await get_application(session, application_id)
    stmt = select(PolicyProduct).where(
        PolicyProduct.coverage_type == application.coverage_type
    )
    return list((await session.execute(stmt)).scalars().all())


async def select_policy(
    session: AsyncSession, application_id: int, product_id: int
) -> Application:
    """Attach a chosen plan to a draft application."""
    application = await get_application(session, application_id)
    if application.status != ApplicationStatus.DRAFT:
        raise ConflictError("Cannot change the plan on a submitted application")
    product = await session.get(PolicyProduct, product_id)
    if product is None:
        raise NotFoundError(f"Policy product {product_id} not found")
    if product.coverage_type != application.coverage_type:
        raise ConflictError("Plan does not match the application's coverage type")
    # Assign the relationship object (not the raw FK): this keeps the ORM's
    # relationship state and the foreign-key column in sync. Setting only the FK
    # can leave an already-loaded relationship reading stale.
    application.selected_product = product
    await session.commit()
    return await get_application(session, application_id)


async def confirm_application(
    session: AsyncSession, application_id: int
) -> Application:
    """Submit a draft application and generate its policy number."""
    application = await get_application(session, application_id)
    if application.status == ApplicationStatus.SUBMITTED:
        raise ConflictError("Application is already submitted")
    if application.selected_product_id is None:
        raise ConflictError("Select a policy before confirming")
    application.status = ApplicationStatus.SUBMITTED
    application.policy_number = generate_policy_number(application.id)
    await session.commit()
    return await get_application(session, application_id)
