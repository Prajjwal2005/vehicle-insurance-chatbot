"""Apply-for-insurance flow tests."""


async def test_apply_happy_path(client, seed_catalogue, application_payload):
    # Open a draft application
    r = await client.post("/applications", json=application_payload)
    assert r.status_code == 201
    app_id = r.json()["id"]
    assert r.json()["status"] == "draft"

    # Applicable policies are all full-coverage plans
    r = await client.get(f"/applications/{app_id}/policies")
    assert r.status_code == 200
    policies = r.json()
    assert len(policies) >= 1
    assert all(p["coverage_type"] == "full" for p in policies)

    # Select a plan
    product_id = policies[0]["id"]
    r = await client.patch(
        f"/applications/{app_id}", json={"selected_product_id": product_id}
    )
    assert r.status_code == 200
    assert r.json()["selected_product"]["id"] == product_id

    # Confirm -> submitted + a policy number
    r = await client.post(f"/applications/{app_id}/confirm")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "submitted"
    assert body["policy_number"].startswith("POL-")


async def test_confirm_without_plan_conflicts(client, application_payload):
    r = await client.post("/applications", json=application_payload)
    app_id = r.json()["id"]
    r = await client.post(f"/applications/{app_id}/confirm")
    assert r.status_code == 409


async def test_missing_application_returns_404(client):
    r = await client.get("/applications/9999")
    assert r.status_code == 404


async def test_invalid_payload_returns_422(client):
    r = await client.post(
        "/applications",
        json={"customer": {}, "vehicle": {}, "coverage_type": "full"},
    )
    assert r.status_code == 422
