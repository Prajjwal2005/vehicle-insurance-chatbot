"""Async HTTP client for the insurance API.

A thin wrapper: one method per insurance endpoint, returning the parsed JSON.
The agent's tools call these; HTTP errors propagate to the caller to handle.
"""

import httpx

from app.config import get_settings


class InsuranceClient:
    """Talks to the insurance system over REST."""

    def __init__(self, base_url: str | None = None, timeout: float = 10.0) -> None:
        self.base_url = base_url or get_settings().insurance_api_url
        self.timeout = timeout

    async def _request(self, method: str, path: str, **kwargs) -> httpx.Response:
        async with httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout) as client:
            response = await client.request(method, path, **kwargs)
            response.raise_for_status()
            return response

    # ── Apply flow ──────────────────────────────────────────────
    async def create_application(self, payload: dict) -> dict:
        return (await self._request("POST", "/applications", json=payload)).json()

    async def list_policies(self, application_id: int) -> list[dict]:
        return (await self._request("GET", f"/applications/{application_id}/policies")).json()

    async def select_policy(self, application_id: int, product_id: int) -> dict:
        return (
            await self._request(
                "PATCH", f"/applications/{application_id}",
                json={"selected_product_id": product_id},
            )
        ).json()

    async def confirm_application(self, application_id: int) -> dict:
        return (await self._request("POST", f"/applications/{application_id}/confirm")).json()

    # ── Claim flow ──────────────────────────────────────────────
    async def create_claim(self, payload: dict) -> dict:
        return (await self._request("POST", "/claims", json=payload)).json()

    async def verify_claim(self, claim_id: int) -> dict:
        return (await self._request("POST", f"/claims/{claim_id}/verify")).json()

    async def confirm_claim(self, claim_id: int) -> dict:
        return (await self._request("POST", f"/claims/{claim_id}/confirm")).json()

    async def get_claim_status(self, claim_number: str) -> dict:
        return (await self._request("GET", f"/claims/{claim_number}")).json()
