"""Policy product (catalogue) response schemas."""

from app.models.enums import CoverageType
from app.schemas.common import ORMModel


class PolicyProductRead(ORMModel):
    """A plan returned when listing the policies applicable to an application."""

    id: int
    name: str
    coverage_type: CoverageType
    base_price: float
    features: list[str]
    description: str
