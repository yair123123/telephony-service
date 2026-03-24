from collections.abc import Mapping
from typing import Any

import httpx

from app.domain.schemas.process_order_result import ProcessOrderResult
from app.domain.schemas.routing_decision import RoutingDecision


class CoreClient:
    def __init__(self, base_url: str, timeout_seconds: float = 10.0):
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    async def _post(self, path: str, json_payload: dict[str, Any]) -> dict[str, Any]:
        async with httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout_seconds) as client:
            response = await client.post(path, json=json_payload)
            response.raise_for_status()
            return response.json()

    async def resolve_call_route(self, phone: str) -> RoutingDecision:
        payload = await self._post("/internal/call-routing/resolve", {"phone": phone})
        return RoutingDecision.model_validate(payload)

    async def process_call_order(self, payload: Mapping[str, Any]) -> ProcessOrderResult:
        body = dict(payload)
        response_payload = await self._post("/internal/orders/process-call-order", body)
        return ProcessOrderResult.model_validate(response_payload)

    async def confirm_ride(self, ride_id: str | int) -> dict[str, Any]:
        return await self._post(f"/internal/rides/{ride_id}/confirm", {})

    async def cancel_searching_by_customer_phone(self, phone: str) -> dict[str, Any]:
        return await self._post(f"/internal/rides/by-customer/{phone}/cancel-searching", {})
