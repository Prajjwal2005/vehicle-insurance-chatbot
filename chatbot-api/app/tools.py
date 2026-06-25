"""LangChain tools that expose the insurance API to the agent.

Each tool wraps an InsuranceClient call, returns a compact JSON string for the
model to relay conversationally, and converts HTTP errors into friendly text.
"""

import json

import httpx
from langchain_core.tools import tool

from app.insurance_client import InsuranceClient

client = InsuranceClient()


def _error(exc: Exception) -> str:
    """Turn any failure into a small JSON message the agent can relay kindly."""
    if isinstance(exc, httpx.HTTPStatusError):
        try:
            detail = exc.response.json().get("detail")
        except Exception:
            detail = None
        return json.dumps({"error": detail or exc.response.text or str(exc)})
    return json.dumps({"error": f"Could not reach the insurance system: {exc}"})


@tool
async def create_application(
    customer_name: str,
    customer_phone: str,
    customer_email: str,
    customer_address: str,
    vehicle_make: str,
    vehicle_model: str,
    vehicle_year: int,
    vehicle_mileage: int,
    vehicle_vin: str,
    coverage_type: str,
    addon_rent_a_car: bool = False,
) -> str:
    """Open a draft insurance application once ALL customer and vehicle details
    are collected. coverage_type must be "full" or "third_party"."""
    payload = {
        "customer": {
            "name": customer_name, "phone": customer_phone,
            "email": customer_email, "address": customer_address,
        },
        "vehicle": {
            "make": vehicle_make, "model": vehicle_model, "year": vehicle_year,
            "mileage": vehicle_mileage, "vin": vehicle_vin,
        },
        "coverage_type": coverage_type,
        "addon_rent_a_car": addon_rent_a_car,
    }
    try:
        r = await client.create_application(payload)
        return json.dumps({"application_id": r["id"], "status": r["status"]})
    except Exception as exc:
        return _error(exc)


@tool
async def list_policies(application_id: int) -> str:
    """List the plans applicable to a draft application, with prices and
    features, so the customer can choose one."""
    try:
        policies = await client.list_policies(application_id)
        return json.dumps([
            {"id": p["id"], "name": p["name"], "price": p["base_price"],
             "features": p["features"]}
            for p in policies
        ])
    except Exception as exc:
        return _error(exc)


@tool
async def select_policy(application_id: int, product_id: int) -> str:
    """Select a plan (product_id) for a draft application."""
    try:
        r = await client.select_policy(application_id, product_id)
        chosen = r.get("selected_product") or {}
        return json.dumps({"application_id": r["id"], "selected_plan": chosen.get("name")})
    except Exception as exc:
        return _error(exc)


@tool
async def confirm_application(application_id: int) -> str:
    """Submit a draft application and get its policy number. Only call this AFTER
    the customer has explicitly confirmed."""
    try:
        r = await client.confirm_application(application_id)
        return json.dumps({"policy_number": r["policy_number"], "status": r["status"]})
    except Exception as exc:
        return _error(exc)


@tool
async def create_claim(
    policy_number: str,
    accident_location: str,
    accident_time: str,
    accident_description: str,
) -> str:
    """Open a draft insurance claim. accident_time should be an ISO 8601 datetime
    (e.g. 2026-06-20T15:30:00)."""
    payload = {
        "policy_number": policy_number,
        "accident_location": accident_location,
        "accident_time": accident_time,
        "accident_description": accident_description,
    }
    try:
        r = await client.create_claim(payload)
        return json.dumps({"claim_id": r["id"], "status": r["status"]})
    except Exception as exc:
        return _error(exc)


@tool
async def verify_claim(claim_id: int) -> str:
    """Check that a draft claim's policy number is valid before confirming."""
    try:
        r = await client.verify_claim(claim_id)
        return json.dumps({"valid": r["valid"], "message": r["message"]})
    except Exception as exc:
        return _error(exc)


@tool
async def confirm_claim(claim_id: int) -> str:
    """Submit a draft claim and get its claim number. Only call this AFTER the
    customer has explicitly confirmed."""
    try:
        r = await client.confirm_claim(claim_id)
        return json.dumps({"claim_number": r["claim_number"], "status": r["status"]})
    except Exception as exc:
        return _error(exc)


@tool
async def check_claim_status(claim_number: str) -> str:
    """Look up the status of a claim by its claim number."""
    try:
        r = await client.get_claim_status(claim_number)
        return json.dumps({"claim_number": r["claim_number"], "status": r["status"]})
    except Exception as exc:
        return _error(exc)


TOOLS = [
    create_application, list_policies, select_policy, confirm_application,
    create_claim, verify_claim, confirm_claim, check_claim_status,
]