"""Shared schema base classes."""

from pydantic import BaseModel, ConfigDict


class ORMModel(BaseModel):
    """Base for response schemas that are read directly from ORM objects.

    ``from_attributes=True`` lets Pydantic build a response model from a
    SQLAlchemy row (reading attributes) rather than only from a dict.
    """

    model_config = ConfigDict(from_attributes=True)
