"""Claim flow tests."""

ACCIDENT = {
    "accident_location": "Sheikh Zayed Road",
    "accident_time": "2026-06-20T15:30:00",
    "accident_description": "Rear-ended at a traffic light.",
}


async def test_claim_happy_path(client, submitted_policy_number):
    # Draft a claim against the valid policy number
    r = await client.post(
        "/claims", json={"policy_number": submitted_policy_number, **ACCIDENT}
    )
    assert r.status_code == 201
    claim_id = r.json()["id"]
    assert r.json()["status"] == "draft"

    # Verify -> valid
    r = await client.post(f"/claims/{claim_id}/verify")
    assert r.status_code == 200
    assert r.json()["valid"] is True

    # Confirm -> submitted + a claim number
    r = await client.post(f"/claims/{claim_id}/confirm")
    assert r.status_code == 200
    claim_number = r.json()["claim_number"]
    assert claim_number.startswith("CLM-")

    # Status lookup by claim number
    r = await client.get(f"/claims/{claim_number}")
    assert r.status_code == 200
    assert r.json()["status"] == "submitted"


async def test_claim_invalid_policy_number(client):
    r = await client.post(
        "/claims", json={"policy_number": "POL-0000-00000", **ACCIDENT}
    )
    claim_id = r.json()["id"]

    r = await client.post(f"/claims/{claim_id}/verify")
    assert r.status_code == 200
    assert r.json()["valid"] is False

    r = await client.post(f"/claims/{claim_id}/confirm")
    assert r.status_code == 409


async def test_claim_status_not_found(client):
    r = await client.get("/claims/CLM-9999-99999")
    assert r.status_code == 404
