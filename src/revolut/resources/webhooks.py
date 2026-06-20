"""Webhooks management resource (sync + async).

Manages webhook *endpoints* via the Merchant API. For verifying delivered
payloads, see :func:`revolut.webhooks_verify.verify_signature`.
"""

from __future__ import annotations

from typing import Any

from .._http.base import RequestSpec
from ..models.webhook import Webhook
from .base import AsyncResource, SyncResource, drop_none

_BASE = "/api/1.0/webhooks"


def _create_spec(url: str, events: list[str], idempotency_key: str | None) -> RequestSpec:
    body = drop_none({"url": url, "events": events})
    return RequestSpec("POST", _BASE, json=body, idempotency_key=idempotency_key)


def _parse_webhook_list(raw: Any) -> list[Webhook]:
    if isinstance(raw, dict):
        raw = raw.get("webhooks", raw.get("data", []))
    return [Webhook.model_validate(item) for item in (raw or [])]


class WebhooksResource(SyncResource):
    """Synchronous webhook-endpoint management."""

    def create(self, *, url: str, events: list[str], idempotency_key: str | None = None) -> Webhook:
        spec = _create_spec(url, events, idempotency_key)
        return Webhook.model_validate(self._transport.request(spec))

    def list(self) -> list[Webhook]:
        spec = RequestSpec("GET", _BASE)
        return _parse_webhook_list(self._transport.request(spec))

    def retrieve(self, webhook_id: str) -> Webhook:
        spec = RequestSpec("GET", f"{_BASE}/{webhook_id}")
        return Webhook.model_validate(self._transport.request(spec))

    def update(self, webhook_id: str, **fields: Any) -> Webhook:
        spec = RequestSpec("PATCH", f"{_BASE}/{webhook_id}", json=fields)
        return Webhook.model_validate(self._transport.request(spec))

    def delete(self, webhook_id: str) -> None:
        spec = RequestSpec("DELETE", f"{_BASE}/{webhook_id}")
        self._transport.request(spec)

    def rotate_signing_secret(self, webhook_id: str) -> Webhook:
        spec = RequestSpec("POST", f"{_BASE}/{webhook_id}/rotate-signing-secret")
        return Webhook.model_validate(self._transport.request(spec))


class AsyncWebhooksResource(AsyncResource):
    """Asynchronous webhook-endpoint management."""

    async def create(
        self, *, url: str, events: list[str], idempotency_key: str | None = None
    ) -> Webhook:
        spec = _create_spec(url, events, idempotency_key)
        return Webhook.model_validate(await self._transport.request(spec))

    async def list(self) -> list[Webhook]:
        spec = RequestSpec("GET", _BASE)
        return _parse_webhook_list(await self._transport.request(spec))

    async def retrieve(self, webhook_id: str) -> Webhook:
        spec = RequestSpec("GET", f"{_BASE}/{webhook_id}")
        return Webhook.model_validate(await self._transport.request(spec))

    async def update(self, webhook_id: str, **fields: Any) -> Webhook:
        spec = RequestSpec("PATCH", f"{_BASE}/{webhook_id}", json=fields)
        return Webhook.model_validate(await self._transport.request(spec))

    async def delete(self, webhook_id: str) -> None:
        spec = RequestSpec("DELETE", f"{_BASE}/{webhook_id}")
        await self._transport.request(spec)

    async def rotate_signing_secret(self, webhook_id: str) -> Webhook:
        spec = RequestSpec("POST", f"{_BASE}/{webhook_id}/rotate-signing-secret")
        return Webhook.model_validate(await self._transport.request(spec))
