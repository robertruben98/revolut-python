"""Base classes binding resources to a transport."""

from __future__ import annotations

from typing import Any

from .._http.async_client import AsyncTransport
from .._http.sync_client import SyncTransport


def drop_none(data: dict[str, Any]) -> dict[str, Any]:
    """Return ``data`` without keys whose value is ``None``."""
    return {k: v for k, v in data.items() if v is not None}


def merge_extra(payload: dict[str, Any], extra: dict[str, Any]) -> dict[str, Any]:
    """Merge caller-supplied ``extra`` fields onto a built payload."""
    return {**payload, **extra}


class SyncResource:
    """A resource bound to a :class:`SyncTransport`."""

    def __init__(self, transport: SyncTransport) -> None:
        self._transport = transport


class AsyncResource:
    """A resource bound to an :class:`AsyncTransport`."""

    def __init__(self, transport: AsyncTransport) -> None:
        self._transport = transport


def clean_params(params: dict[str, Any] | None) -> dict[str, Any] | None:
    """Drop ``None`` query params; return ``None`` if nothing remains."""
    if not params:
        return None
    cleaned = drop_none(params)
    return cleaned or None
