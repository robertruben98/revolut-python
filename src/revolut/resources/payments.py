"""Payments resource (sync + async).

Payments are sub-objects of an order: you list the payments of an order, retrieve
a single payment, or charge a saved payment method against an existing order.
"""

from __future__ import annotations

from typing import Any

from .._http.base import RequestSpec
from ..models.payment import Payment
from .base import AsyncResource, SyncResource, drop_none


def _parse_payment_list(raw: Any) -> list[Payment]:
    if isinstance(raw, dict):
        raw = raw.get("payments", raw.get("data", []))
    return [Payment.model_validate(item) for item in (raw or [])]


def _pay_spec(
    order_id: str, payment_method_id: str, extra: dict[str, Any], idempotency_key: str | None
) -> RequestSpec:
    body = drop_none({"payment_method_id": payment_method_id})
    body.update(extra)
    return RequestSpec(
        "POST", f"/api/orders/{order_id}/payments", json=body, idempotency_key=idempotency_key
    )


class PaymentsResource(SyncResource):
    """Synchronous payments operations."""

    def list_for_order(self, order_id: str) -> list[Payment]:
        spec = RequestSpec("GET", f"/api/orders/{order_id}/payments")
        return _parse_payment_list(self._transport.request(spec))

    def retrieve(self, payment_id: str) -> Payment:
        spec = RequestSpec("GET", f"/api/payments/{payment_id}")
        return Payment.model_validate(self._transport.request(spec))

    def pay(
        self,
        order_id: str,
        *,
        payment_method_id: str,
        idempotency_key: str | None = None,
        **extra: Any,
    ) -> Payment:
        spec = _pay_spec(order_id, payment_method_id, extra, idempotency_key)
        return Payment.model_validate(self._transport.request(spec))


class AsyncPaymentsResource(AsyncResource):
    """Asynchronous payments operations."""

    async def list_for_order(self, order_id: str) -> list[Payment]:
        spec = RequestSpec("GET", f"/api/orders/{order_id}/payments")
        return _parse_payment_list(await self._transport.request(spec))

    async def retrieve(self, payment_id: str) -> Payment:
        spec = RequestSpec("GET", f"/api/payments/{payment_id}")
        return Payment.model_validate(await self._transport.request(spec))

    async def pay(
        self,
        order_id: str,
        *,
        payment_method_id: str,
        idempotency_key: str | None = None,
        **extra: Any,
    ) -> Payment:
        spec = _pay_spec(order_id, payment_method_id, extra, idempotency_key)
        return Payment.model_validate(await self._transport.request(spec))
