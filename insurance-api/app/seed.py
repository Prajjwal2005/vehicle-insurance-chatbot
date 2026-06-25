"""Seed the database with a policy catalogue and demo data.

Run once after the tables exist:

    python -m app.seed

Idempotent: re-running will not duplicate rows.
"""

import asyncio

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import SessionLocal, init_db
from app.models import Application, Customer, PolicyProduct, Vehicle
from app.models.enums import ApplicationStatus, CoverageType
from app.services.numbering import generate_policy_number


def _new_catalogue() -> list[PolicyProduct]:
    """Fresh PolicyProduct rows for the catalogue (new objects each call)."""
    return [
        PolicyProduct(
            name="Third Party Basic",
            coverage_type=CoverageType.THIRD_PARTY,
            base_price=400.0,
            features=["Third-party liability cover", "24/7 claims hotline"],
            description="The legal minimum cover for third-party damage.",
        ),
        PolicyProduct(
            name="Full Coverage Standard",
            coverage_type=CoverageType.FULL,
            base_price=1200.0,
            features=["Accident damage", "Theft & fire",
                      "Third-party liability", "24/7 claims hotline"],
            description="Comprehensive cover for most drivers.",
        ),
        PolicyProduct(
            name="Full Coverage Plus",
            coverage_type=CoverageType.FULL,
            base_price=1800.0,
            features=["Everything in Standard", "Zero-depreciation cover",
                      "Roadside assistance", "Personal accident cover"],
            description="Top-tier cover with optional extras.",
        ),
    ]


async def seed_policy_products(session: AsyncSession) -> list[PolicyProduct]:
    """Insert the catalogue once; on later runs, return the existing rows."""
    count = (await session.execute(select(func.count(PolicyProduct.id)))).scalar_one()
    if count:
        print(f"Catalogue already has {count} products - skipping.")
        return list((await session.execute(select(PolicyProduct))).scalars().all())
    products = _new_catalogue()
    session.add_all(products)
    await session.commit()
    print(f"Inserted {len(products)} policy products.")
    return products


async def seed_demo_application(
    session: AsyncSession, products: list[PolicyProduct]
) -> None:
    """Create one pre-submitted application so a valid policy number exists."""
    submitted = (
        await session.execute(
            select(func.count(Application.id)).where(
                Application.status == ApplicationStatus.SUBMITTED
            )
        )
    ).scalar_one()
    if submitted:
        print(f"{submitted} submitted application(s) exist - skipping demo data.")
        return

    full_standard = next(p for p in products if p.name == "Full Coverage Standard")
    customer = Customer(
        name="Demo Customer", phone="+971 50 0000001",
        email="demo@example.com", address="Downtown Dubai",
    )
    vehicle = Vehicle(
        customer=customer, make="Honda", model="Civic",
        year=2021, mileage=25000, vin="2HGFB2F50CH123456",
    )
    application = Application(
        customer=customer, vehicle=vehicle, coverage_type=CoverageType.FULL,
        addon_rent_a_car=False, selected_product=full_standard,
        status=ApplicationStatus.SUBMITTED,
    )
    session.add(application)
    await session.flush()  # assign application.id before numbering
    application.policy_number = generate_policy_number(application.id)
    await session.commit()
    print(f"Created demo application - policy number: {application.policy_number}")


async def main() -> None:
    await init_db()
    async with SessionLocal() as session:
        products = await seed_policy_products(session)
        await seed_demo_application(session, products)
    print("Seeding complete.")


if __name__ == "__main__":
    asyncio.run(main())
