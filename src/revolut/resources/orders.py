"""Orders resource (sync + async)."""

from __future__ import annotations

from typing import Any

from .._http.base import RequestSpec
from ..models.order import Order
from .base import AsyncResource, SyncResource, clean_params, drop_none

_BASE = "/api/orders"


def _create_spec(
    *,
    amount: int,
    currency: str,
    capture_mode: str | None,
    customer: dict[str, Any] | None,
    merchant_order_data: dict[str, Any] | None,
    metadata: dict[str, Any] | None,
    idempotency_key: str | None,
    extra: dict[str, Any],
) -> RequestSpec:
    body = drop_none(
        {
            "amount": amount,
            "currency": currency,
            "capture_mode": capture_mode,
            "customer": customer,
            "merchant_order_data": merchant_order_data,
            "metadata": metadata,
        }
    )
    body.update(extra)
    return RequestSpec("POST", _BASE, json=body, idempotency_key=idempotency_key)


def _list_spec(params: dict[str, Any]) -> RequestSpec:
    return RequestSpec("GET", _BASE, params=clean_params(params))


def _capture_spec(order_id: str, amount: int | None, idempotency_key: str | None) -> RequestSpec:
    body = drop_none({"amount": amount}) or None
    return RequestSpec(
        "POST", f"{_BASE}/{order_id}/capture", json=body, idempotency_key=idempotency_key
    )


def _parse_order_list(raw: Any) -> list[Order]:
    if isinstance(raw, dict):
        raw = raw.get("orders", [])
    return [Order.model_validate(item) for item in (raw or [])]


class OrdersResource(SyncResource):
    """Synchronous orders operations."""

    def create(
        self,
        *,
        amount: int,
        currency: str,
        capture_mode: str | None = None,
        customer: dict[str, Any] | None = None,
        merchant_order_data: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
        idempotency_key: str | None = None,
        **extra: Any,
    ) -> Order:
        spec = _create_spec(
            amount=amount,
            currency=currency,
            capture_mode=capture_mode,
            customer=customer,
            merchant_order_data=merchant_order_data,
            metadata=metadata,
            idempotency_key=idempotency_key,
            extra=extra,
        )
        return Order.model_validate(self._transport.request(spec))

    def retrieve(self, order_id: str) -> Order:
        spec = RequestSpec("GET", f"{_BASE}/{order_id}")
        return Order.model_validate(self._transport.request(spec))

    def list(
        self,
        *,
        limit: int | None = None,
        from_: str | None = None,
        to: str | None = None,
        customer_id: str | None = None,
        state: str | None = None,
        **params: Any,
    ) -> list[Order]:
        merged = {
            "limit": limit,
            "from": from_,
            "to": to,
            "customer_id": customer_id,
            "state": state,
            **params,
        }
        return _parse_order_list(self._transport.request(_list_spec(merged)))

    def update(self, order_id: str, **fields: Any) -> Order:
        spec = RequestSpec("PATCH", f"{_BASE}/{order_id}", json=fields)
        return Order.model_validate(self._transport.request(spec))

    def capture(
        self,
        order_id: str,
        *,
        amount: int | None = None,
        idempotency_key: str | None = None,
    ) -> Order:
        spec = _capture_spec(order_id, amount, idempotency_key)
        return Order.model_validate(self._transport.request(spec))

    def cancel(self, order_id: str) -> Order:
        spec = RequestSpec("POST", f"{_BASE}/{order_id}/cancel")
        return Order.model_validate(self._transport.request(spec))


class AsyncOrdersResource(AsyncResource):
    """Asynchronous orders operations."""

    async def create(
        self,
        *,
        amount: int,
        currency: str,
        capture_mode: str | None = None,
        customer: dict[str, Any] | None = None,
        merchant_order_data: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
        idempotency_key: str | None = None,
        **extra: Any,
    ) -> Order:
        spec = _create_spec(
            amount=amount,
            currency=currency,
            capture_mode=capture_mode,
            customer=customer,
            merchant_order_data=merchant_order_data,
            metadata=metadata,
            idempotency_key=idempotency_key,
            extra=extra,
        )
        return Order.model_validate(await self._transport.request(spec))

    async def retrieve(self, order_id: str) -> Order:
        spec = RequestSpec("GET", f"{_BASE}/{order_id}")
        return Order.model_validate(await self._transport.request(spec))

    async def list(
        self,
        *,
        limit: int | None = None,
        from_: str | None = None,
        to: str | None = None,
        customer_id: str | None = None,
        state: str | None = None,
        **params: Any,
    ) -> list[Order]:
        merged = {
            "limit": limit,
            "from": from_,
            "to": to,
            "customer_id": customer_id,
            "state": state,
            **params,
        }
        return _parse_order_list(await self._transport.request(_list_spec(merged)))

    async def update(self, order_id: str, **fields: Any) -> Order:
        spec = RequestSpec("PATCH", f"{_BASE}/{order_id}", json=fields)
        return Order.model_validate(await self._transport.request(spec))

    async def capture(
        self,
        order_id: str,
        *,
        amount: int | None = None,
        idempotency_key: str | None = None,
    ) -> Order:
        spec = _capture_spec(order_id, amount, idempotency_key)
        return Order.model_validate(await self._transport.request(spec))

    async def cancel(self, order_id: str) -> Order:
        spec = RequestSpec("POST", f"{_BASE}/{order_id}/cancel")
        return Order.model_validate(await self._transport.request(spec))
