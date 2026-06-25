"""ORM models.

Importing this package imports every model, which registers all tables on
``Base.metadata`` — required before ``create_all`` / migrations can see them.
"""

from app.models.application import Application
from app.models.claim import Claim
from app.models.customer import Customer
from app.models.policy_product import PolicyProduct
from app.models.vehicle import Vehicle

__all__ = [
    "Application",
    "Claim",
    "Customer",
    "PolicyProduct",
    "Vehicle",
]
