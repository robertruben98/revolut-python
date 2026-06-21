"""Disputes resource (sync + async).

Path strings follow Revolut's documented REST convention; confirmed against a
live sandbox in #23.
"""

from __future__ import annotations

from typing import Any

from .._http.base import RequestSpec
from ..models.dispute import Dispute
from .base import AsyncResource, SyncResource, clean_params, drop_none

_BASE = "/api/disputes"


def _parse_list(raw: Any) -> list[Dispute]:
    if isinstance(raw, dict):
        raw = raw.get("disputes", raw.get("data", []))
    return [Dispute.model_validate(item) for item in (raw or [])]


class DisputesResource(SyncResource):
    """Synchronous dispute operations."""

    def retrieve(self, dispute_id: str) -> Dispute:
        spec = RequestSpec("GET", f"{_BASE}/{dispute_id}")
        return Dispute.model_validate(self._transport.request(spec))

    def list(self, **params: Any) -> list[Dispute]:
        spec = RequestSpec("GET", _BASE, params=clean_params(params))
        return _parse_list(self._transport.request(spec))

    def respond(self, dispute_id: str, **fields: Any) -> Dispute:
        spec = RequestSpec("POST", f"{_BASE}/{dispute_id}/respond", json=drop_none(fields))
        return Dispute.model_validate(self._transport.request(spec))


class AsyncDisputesResource(AsyncResource):
    """Asynchronous dispute operations."""

    async def retrieve(self, dispute_id: str) -> Dispute:
        spec = RequestSpec("GET", f"{_BASE}/{dispute_id}")
        return Dispute.model_validate(await self._transport.request(spec))

    async def list(self, **params: Any) -> list[Dispute]:
        spec = RequestSpec("GET", _BASE, params=clean_params(params))
        return _parse_list(await self._transport.request(spec))

    async def respond(self, dispute_id: str, **fields: Any) -> Dispute:
        spec = RequestSpec("POST", f"{_BASE}/{dispute_id}/respond", json=drop_none(fields))
        return Dispute.model_validate(await self._transport.request(spec))
