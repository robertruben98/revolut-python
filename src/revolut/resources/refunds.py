"""Refunds resource (sync + async).

A refund is created against an existing order via
``POST /api/orders/{order_id}/refund`` and yields a new order of
``type: refund``. ``Idempotency-Key`` is strongly recommended here.
"""

from __future__ import annotations

from typing import Any

from .._http.base import RequestSpec
from ..models.order import Order
from .base import AsyncResource, SyncResource, drop_none


def _refund_spec(
    order_id: str,
    *,
    amount: int,
    currency: str | None,
    description: str | None,
    extra: dict[str, Any],
    idempotency_key: str | None,
) -> RequestSpec:
    body = drop_none({"amount": amount, "currency": currency, "description": description})
    body.update(extra)
    return RequestSpec(
        "POST", f"/api/orders/{order_id}/refund", json=body, idempotency_key=idempotency_key
    )


class RefundsResource(SyncResource):
    """Synchronous refund operations."""

    def create(
        self,
        order_id: str,
        *,
        amount: int,
        currency: str | None = None,
        description: str | None = None,
        idempotency_key: str | None = None,
        **extra: Any,
    ) -> Order:
        spec = _refund_spec(
            order_id,
            amount=amount,
            currency=currency,
            description=description,
            extra=extra,
            idempotency_key=idempotency_key,
        )
        return Order.model_validate(self._transport.request(spec))


class AsyncRefundsResource(AsyncResource):
    """Asynchronous refund operations."""

    async def create(
        self,
        order_id: str,
        *,
        amount: int,
        currency: str | None = None,
        description: str | None = None,
        idempotency_key: str | None = None,
        **extra: Any,
    ) -> Order:
        spec = _refund_spec(
            order_id,
            amount=amount,
            currency=currency,
            description=description,
            extra=extra,
            idempotency_key=idempotency_key,
        )
        return Order.model_validate(await self._transport.request(spec))
