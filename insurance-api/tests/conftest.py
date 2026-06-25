"""Shared pytest fixtures: an isolated in-memory DB and an async test client.

Tests never touch the dev database. Each test gets a fresh in-memory SQLite,
created via StaticPool so the single connection (and its schema + data) is shared
across every request the test makes.
"""

import httpx
import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.database import Base, get_session
from app.main import app
from app.seed import _new_catalogue


@pytest.fixture
def application_payload() -> dict:
    """A valid full-coverage application body, reused across tests."""
    return {
        "customer": {"name": "Test User", "phone": "+971 50 1234567",
                     "email": "test@example.com", "address": "Dubai"},
        "vehicle": {"make": "Toyota", "model": "Corolla", "year": 2020,
                    "mileage": 30000, "vin": "1HGCM82633A004352"},
        "coverage_type": "full",
        "addon_rent_a_car": True,
    }


@pytest.fixture
async def db_engine():
    engine = create_async_engine(
        "sqlite+aiosqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture
def session_factory(db_engine):
    return async_sessionmaker(db_engine, expire_on_commit=False)


@pytest.fixture
async def client(session_factory):
    async def override_get_session():
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test", headers={"X-API-Key": "demo-secret-key"}) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
async def seed_catalogue(session_factory) -> list[str]:
    async with session_factory() as session:
        products = _new_catalogue()
        session.add_all(products)
        await session.commit()
    return [p.name for p in products]


@pytest.fixture
async def submitted_policy_number(client, seed_catalogue, application_payload) -> str:
    """Run the apply flow end to end and return the generated policy number."""
    r = await client.post("/applications", json=application_payload)
    app_id = r.json()["id"]
    r = await client.get(f"/applications/{app_id}/policies")
    product_id = r.json()[0]["id"]
    await client.patch(f"/applications/{app_id}", json={"selected_product_id": product_id})
    r = await client.post(f"/applications/{app_id}/confirm")
    return r.json()["policy_number"]
