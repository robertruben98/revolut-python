"""Saved payment methods resource (sync + async).

Saved methods (tokenization) live under a customer. Charge one by passing its
``id`` as ``payment_method_id`` to ``client.payments.pay(order_id, ...)``.
"""

from __future__ import annotations

from typing import Any

from .._http.base import RequestSpec
from ..models.payment_method import PaymentMethod
from .base import AsyncResource, SyncResource, clean_params


def _base(customer_id: str) -> str:
    return f"/api/customers/{customer_id}/payment-methods"


def _parse_list(raw: Any) -> list[PaymentMethod]:
    if isinstance(raw, dict):
        raw = raw.get("payment_methods", raw.get("data", []))
    return [PaymentMethod.model_validate(item) for item in (raw or [])]


class PaymentMethodsResource(SyncResource):
    """Synchronous saved-payment-method operations."""

    def list(
        self, customer_id: str, *, only_merchant: bool | None = None, **params: Any
    ) -> list[PaymentMethod]:
        merged = {"only_merchant": only_merchant, **params}
        spec = RequestSpec("GET", _base(customer_id), params=clean_params(merged))
        return _parse_list(self._transport.request(spec))

    def retrieve(self, customer_id: str, payment_method_id: str) -> PaymentMethod:
        spec = RequestSpec("GET", f"{_base(customer_id)}/{payment_method_id}")
        return PaymentMethod.model_validate(self._transport.request(spec))

    def update(self, customer_id: str, payment_method_id: str, **fields: Any) -> PaymentMethod:
        spec = RequestSpec("PATCH", f"{_base(customer_id)}/{payment_method_id}", json=fields)
        return PaymentMethod.model_validate(self._transport.request(spec))

    def delete(self, customer_id: str, payment_method_id: str) -> None:
        spec = RequestSpec("DELETE", f"{_base(customer_id)}/{payment_method_id}")
        self._transport.request(spec)


class AsyncPaymentMethodsResource(AsyncResource):
    """Asynchronous saved-payment-method operations."""

    async def list(
        self, customer_id: str, *, only_merchant: bool | None = None, **params: Any
    ) -> list[PaymentMethod]:
        merged = {"only_merchant": only_merchant, **params}
        spec = RequestSpec("GET", _base(customer_id), params=clean_params(merged))
        return _parse_list(await self._transport.request(spec))

    async def retrieve(self, customer_id: str, payment_method_id: str) -> PaymentMethod:
        spec = RequestSpec("GET", f"{_base(customer_id)}/{payment_method_id}")
        return PaymentMethod.model_validate(await self._transport.request(spec))

    async def update(
        self, customer_id: str, payment_method_id: str, **fields: Any
    ) -> PaymentMethod:
        spec = RequestSpec("PATCH", f"{_base(customer_id)}/{payment_method_id}", json=fields)
        return PaymentMethod.model_validate(await self._transport.request(spec))

    async def delete(self, customer_id: str, payment_method_id: str) -> None:
        spec = RequestSpec("DELETE", f"{_base(customer_id)}/{payment_method_id}")
        await self._transport.request(spec)
