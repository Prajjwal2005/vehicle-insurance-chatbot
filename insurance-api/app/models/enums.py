"""Fixed value sets used across the insurance domain.

Defined as ``(str, Enum)`` so members compare equal to their string value and
serialise cleanly to JSON. This stays compatible with Python 3.10 (whereas
``enum.StrEnum`` would require 3.11+).
"""

from enum import Enum


class CoverageType(str, Enum):
    """Level of cover a policy provides."""

    FULL = "full"
    THIRD_PARTY = "third_party"


class ApplicationStatus(str, Enum):
    """Lifecycle of an insurance application."""

    DRAFT = "draft"
    SUBMITTED = "submitted"


class ClaimStatus(str, Enum):
    """Lifecycle of an insurance claim."""

    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    DECLINED = "declined"
    COMPLETED = "completed"
