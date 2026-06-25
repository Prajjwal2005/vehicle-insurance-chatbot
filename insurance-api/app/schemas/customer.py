"""Customer request/response schemas."""

from pydantic import BaseModel, EmailStr, Field

from app.schemas.common import ORMModel


class CustomerCreate(BaseModel):
    """Customer details collected when starting an application."""

    name: str = Field(min_length=1, max_length=120)
    phone: str = Field(min_length=7, max_length=20, pattern=r"^[0-9 +()-]+$")
    email: EmailStr
    address: str = Field(min_length=1, max_length=300)


class CustomerRead(ORMModel):
    id: int
    name: str
    phone: str
    email: str
    address: str
