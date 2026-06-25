"""Async HTTP client for the insurance API.

Holds one shared httpx.AsyncClient for the process (connection pooling); it is
closed on shutdown via aclose(). One method per insurance endpoint. Every
request carries the X-API-Key header so the insurance API accepts it.
"""

import httpx

from app.config import get_settings


class InsuranceClient:
    """Talks to the insurance system over REST, reusing one pooled client."""

    def __init__(self, base_url: str | None = None, timeout: float = 10.0) -> None:
        settings = get_settings()
        self.base_url = base_url or settings.insurance_api_url
        self.timeout = timeout
        self.headers = {"X-API-Key": settings.insurance_api_key}
        self._client: httpx.AsyncClient | None = None

    def _http(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url, timeout=self.timeout, headers=self.headers,
            )
        return self._client

    async def aclose(self) -> None:
        if self._client is not None and not self._client.is_closed:
            await self._client.aclose()

    async def _request(self, method: str, path: str, **kwargs) -> httpx.Response:
        response = await self._http().request(method, path, **kwargs)
        response.raise_for_status()
        return response

    # -- Apply flow --
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

    # -- Claim flow --
    async def create_claim(self, payload: dict) -> dict:
        return (await self._request("POST", "/claims", json=payload)).json()

    async def verify_claim(self, claim_id: int) -> dict:
        return (await self._request("POST", f"/claims/{claim_id}/verify")).json()

    async def confirm_claim(self, claim_id: int) -> dict:
        return (await self._request("POST", f"/claims/{claim_id}/confirm")).json()

    async def get_claim_status(self, claim_number: str) -> dict:
        return (await self._request("GET", f"/claims/{claim_number}")).json()