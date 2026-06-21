"""Subscriptions resource (sync + async).

Path strings follow Revolut's documented REST convention; confirmed against a
live sandbox in #23.
"""

from __future__ import annotations

from typing import Any

from .._http.base import RequestSpec
from ..models.subscription import Subscription
from .base import AsyncResource, SyncResource, clean_params, drop_none

_BASE = "/api/subscriptions"


def _parse_list(raw: Any) -> list[Subscription]:
    if isinstance(raw, dict):
        raw = raw.get("subscriptions", raw.get("data", []))
    return [Subscription.model_validate(item) for item in (raw or [])]


class SubscriptionsResource(SyncResource):
    """Synchronous subscription operations."""

    def create(self, *, idempotency_key: str | None = None, **fields: Any) -> Subscription:
        spec = RequestSpec("POST", _BASE, json=drop_none(fields), idempotency_key=idempotency_key)
        return Subscription.model_validate(self._transport.request(spec))

    def retrieve(self, subscription_id: str) -> Subscription:
        spec = RequestSpec("GET", f"{_BASE}/{subscription_id}")
        return Subscription.model_validate(self._transport.request(spec))

    def list(self, **params: Any) -> list[Subscription]:
        spec = RequestSpec("GET", _BASE, params=clean_params(params))
        return _parse_list(self._transport.request(spec))

    def cancel(self, subscription_id: str) -> Subscription:
        spec = RequestSpec("POST", f"{_BASE}/{subscription_id}/cancel")
        return Subscription.model_validate(self._transport.request(spec))


class AsyncSubscriptionsResource(AsyncResource):
    """Asynchronous subscription operations."""

    async def create(self, *, idempotency_key: str | None = None, **fields: Any) -> Subscription:
        spec = RequestSpec("POST", _BASE, json=drop_none(fields), idempotency_key=idempotency_key)
        return Subscription.model_validate(await self._transport.request(spec))

    async def retrieve(self, subscription_id: str) -> Subscription:
        spec = RequestSpec("GET", f"{_BASE}/{subscription_id}")
        return Subscription.model_validate(await self._transport.request(spec))

    async def list(self, **params: Any) -> list[Subscription]:
        spec = RequestSpec("GET", _BASE, params=clean_params(params))
        return _parse_list(await self._transport.request(spec))

    async def cancel(self, subscription_id: str) -> Subscription:
        spec = RequestSpec("POST", f"{_BASE}/{subscription_id}/cancel")
        return Subscription.model_validate(await self._transport.request(spec))
