"""Generation of human-readable, unique policy and claim numbers.

The id-based scheme guarantees uniqueness (the id is unique) and stays readable.
A production system might prefer opaque/random identifiers so as not to leak
sequential counts — called out here as a deliberate simplification.
"""

from datetime import datetime, timezone


def _year() -> int:
    return datetime.now(timezone.utc).year


def generate_policy_number(application_id: int) -> str:
    return f"POL-{_year()}-{application_id:05d}"


def generate_claim_number(claim_id: int) -> str:
    return f"CLM-{_year()}-{claim_id:05d}"
