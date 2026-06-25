"""Async SQLAlchemy engine, session factory, declarative base, and DB dependency."""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config import get_settings

settings = get_settings()

# echo=False keeps logs quiet; set True to see the SQL SQLAlchemy emits.
engine = create_async_engine(settings.database_url, echo=False)

# expire_on_commit=False lets us read attributes (e.g. a freshly generated
# policy number) after commit without a reload against a closed session.
SessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


class Base(DeclarativeBase):
    """Declarative base that every ORM model inherits from."""


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide a database session for the lifetime of one request.

    The service layer commits explicitly. This dependency rolls back on any
    unhandled exception and always closes the session when the request ends.
    """
    async with SessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


async def init_db() -> None:
    """Create all tables. A dev convenience — production would use Alembic."""
    # Imported here so every model is registered on Base.metadata first.
    from app import models  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
