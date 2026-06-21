"""Payouts resource (sync + async).

Path strings follow Revolut's documented REST convention; confirmed against a
live sandbox in #23.
"""

from __future__ import annotations

from typing import Any

from .._http.base import RequestSpec
from ..models.payout import Payout
from .base import AsyncResource, SyncResource, clean_params

_BASE = "/api/payouts"


def _parse_list(raw: Any) -> list[Payout]:
    if isinstance(raw, dict):
        raw = raw.get("payouts", raw.get("data", []))
    return [Payout.model_validate(item) for item in (raw or [])]


class PayoutsResource(SyncResource):
    """Synchronous payout operations."""

    def retrieve(self, payout_id: str) -> Payout:
        spec = RequestSpec("GET", f"{_BASE}/{payout_id}")
        return Payout.model_validate(self._transport.request(spec))

    def list(self, **params: Any) -> list[Payout]:
        spec = RequestSpec("GET", _BASE, params=clean_params(params))
        return _parse_list(self._transport.request(spec))


class AsyncPayoutsResource(AsyncResource):
    """Asynchronous payout operations."""

    async def retrieve(self, payout_id: str) -> Payout:
        spec = RequestSpec("GET", f"{_BASE}/{payout_id}")
        return Payout.model_validate(await self._transport.request(spec))

    async def list(self, **params: Any) -> list[Payout]:
        spec = RequestSpec("GET", _BASE, params=clean_params(params))
        return _parse_list(await self._transport.request(spec))
