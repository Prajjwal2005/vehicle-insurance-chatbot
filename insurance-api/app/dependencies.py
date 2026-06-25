"""Shared FastAPI dependencies."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session

# Inject an async DB session into a route with: session: SessionDep
SessionDep = Annotated[AsyncSession, Depends(get_session)]
