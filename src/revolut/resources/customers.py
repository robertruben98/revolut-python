"""Customers resource (sync + async)."""

from __future__ import annotations

from typing import Any

from .._http.base import RequestSpec
from ..models.customer import Customer
from .base import AsyncResource, SyncResource, clean_params, drop_none

_BASE = "/api/customers"


def _create_spec(
    *,
    full_name: str | None,
    email: str | None,
    phone: str | None,
    extra: dict[str, Any],
    idempotency_key: str | None,
) -> RequestSpec:
    body = drop_none({"full_name": full_name, "email": email, "phone": phone})
    body.update(extra)
    return RequestSpec("POST", _BASE, json=body, idempotency_key=idempotency_key)


def _parse_customer_list(raw: Any) -> list[Customer]:
    if isinstance(raw, dict):
        raw = raw.get("customers", raw.get("data", []))
    return [Customer.model_validate(item) for item in (raw or [])]


class CustomersResource(SyncResource):
    """Synchronous customer operations."""

    def create(
        self,
        *,
        full_name: str | None = None,
        email: str | None = None,
        phone: str | None = None,
        idempotency_key: str | None = None,
        **extra: Any,
    ) -> Customer:
        spec = _create_spec(
            full_name=full_name,
            email=email,
            phone=phone,
            extra=extra,
            idempotency_key=idempotency_key,
        )
        return Customer.model_validate(self._transport.request(spec))

    def retrieve(self, customer_id: str) -> Customer:
        spec = RequestSpec("GET", f"{_BASE}/{customer_id}")
        return Customer.model_validate(self._transport.request(spec))

    def list(
        self,
        *,
        limit: int | None = None,
        page_token: str | None = None,
        **params: Any,
    ) -> list[Customer]:
        merged = {"limit": limit, "page_token": page_token, **params}
        spec = RequestSpec("GET", _BASE, params=clean_params(merged))
        return _parse_customer_list(self._transport.request(spec))

    def update(self, customer_id: str, **fields: Any) -> Customer:
        spec = RequestSpec("PATCH", f"{_BASE}/{customer_id}", json=fields)
        return Customer.model_validate(self._transport.request(spec))

    def delete(self, customer_id: str) -> None:
        spec = RequestSpec("DELETE", f"{_BASE}/{customer_id}")
        self._transport.request(spec)


class AsyncCustomersResource(AsyncResource):
    """Asynchronous customer operations."""

    async def create(
        self,
        *,
        full_name: str | None = None,
        email: str | None = None,
        phone: str | None = None,
        idempotency_key: str | None = None,
        **extra: Any,
    ) -> Customer:
        spec = _create_spec(
            full_name=full_name,
            email=email,
            phone=phone,
            extra=extra,
            idempotency_key=idempotency_key,
        )
        return Customer.model_validate(await self._transport.request(spec))

    async def retrieve(self, customer_id: str) -> Customer:
        spec = RequestSpec("GET", f"{_BASE}/{customer_id}")
        return Customer.model_validate(await self._transport.request(spec))

    async def list(
        self,
        *,
        limit: int | None = None,
        page_token: str | None = None,
        **params: Any,
    ) -> list[Customer]:
        merged = {"limit": limit, "page_token": page_token, **params}
        spec = RequestSpec("GET", _BASE, params=clean_params(merged))
        return _parse_customer_list(await self._transport.request(spec))

    async def update(self, customer_id: str, **fields: Any) -> Customer:
        spec = RequestSpec("PATCH", f"{_BASE}/{customer_id}", json=fields)
        return Customer.model_validate(await self._transport.request(spec))

    async def delete(self, customer_id: str) -> None:
        spec = RequestSpec("DELETE", f"{_BASE}/{customer_id}")
        await self._transport.request(spec)
