"""Locations resource (sync + async).

The ``/api/locations`` path is confirmed from Revolut docs examples.
"""

from __future__ import annotations

from typing import Any

from .._http.base import RequestSpec
from ..models.location import Location
from .base import AsyncResource, SyncResource, clean_params, drop_none

_BASE = "/api/locations"


def _parse_list(raw: Any) -> list[Location]:
    if isinstance(raw, dict):
        raw = raw.get("locations", raw.get("data", []))
    return [Location.model_validate(item) for item in (raw or [])]


class LocationsResource(SyncResource):
    """Synchronous location operations."""

    def create(self, *, idempotency_key: str | None = None, **fields: Any) -> Location:
        spec = RequestSpec("POST", _BASE, json=drop_none(fields), idempotency_key=idempotency_key)
        return Location.model_validate(self._transport.request(spec))

    def retrieve(self, location_id: str) -> Location:
        spec = RequestSpec("GET", f"{_BASE}/{location_id}")
        return Location.model_validate(self._transport.request(spec))

    def list(self, **params: Any) -> list[Location]:
        spec = RequestSpec("GET", _BASE, params=clean_params(params))
        return _parse_list(self._transport.request(spec))

    def update(self, location_id: str, **fields: Any) -> Location:
        spec = RequestSpec("PATCH", f"{_BASE}/{location_id}", json=fields)
        return Location.model_validate(self._transport.request(spec))

    def delete(self, location_id: str) -> None:
        spec = RequestSpec("DELETE", f"{_BASE}/{location_id}")
        self._transport.request(spec)


class AsyncLocationsResource(AsyncResource):
    """Asynchronous location operations."""

    async def create(self, *, idempotency_key: str | None = None, **fields: Any) -> Location:
        spec = RequestSpec("POST", _BASE, json=drop_none(fields), idempotency_key=idempotency_key)
        return Location.model_validate(await self._transport.request(spec))

    async def retrieve(self, location_id: str) -> Location:
        spec = RequestSpec("GET", f"{_BASE}/{location_id}")
        return Location.model_validate(await self._transport.request(spec))

    async def list(self, **params: Any) -> list[Location]:
        spec = RequestSpec("GET", _BASE, params=clean_params(params))
        return _parse_list(await self._transport.request(spec))

    async def update(self, location_id: str, **fields: Any) -> Location:
        spec = RequestSpec("PATCH", f"{_BASE}/{location_id}", json=fields)
        return Location.model_validate(await self._transport.request(spec))

    async def delete(self, location_id: str) -> None:
        spec = RequestSpec("DELETE", f"{_BASE}/{location_id}")
        await self._transport.request(spec)
