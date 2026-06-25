"""Shared FastAPI dependencies."""

from typing import Annotated

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session

# Inject an async DB session into a route with: session: SessionDep
SessionDep = Annotated[AsyncSession, Depends(get_session)]

# Mock Authentication
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

def get_current_user(api_key: str = Security(api_key_header)) -> dict:
    if api_key == "demo-secret-key":
        return {"user_id": 1, "username": "demo_user"}
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing API Key",
    )

CurrentUserDep = Annotated[dict, Depends(get_current_user)]
