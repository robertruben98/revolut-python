"""Shared HTTP plumbing for the sync and async transports.

This module is transport-agnostic: it builds request headers, parses responses
into JSON or raises the mapped :class:`~revolut.exceptions.APIStatusError`, and
decides whether a failed attempt should be retried. The actual ``send`` (sync vs
async) lives in :mod:`revolut._http.sync_client` and
:mod:`revolut._http.async_client`, so both clients behave identically.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import httpx

from .._version import __version__
from ..config import DEFAULT_API_VERSION
from ..exceptions import (
    APIStatusError,
    RateLimitError,
    exception_for_status,
)


@dataclass
class RequestSpec:
    """A transport-independent description of a single API request."""

    method: str
    path: str
    params: dict[str, Any] | None = None
    json: Any | None = None
    idempotency_key: str | None = None


@dataclass
class RetryConfig:
    """Controls automatic retries for transient failures."""

    max_retries: int = 2
    backoff_factor: float = 0.5
    max_backoff: float = 30.0
    retry_statuses: frozenset[int] = field(
        default_factory=lambda: frozenset({429, 500, 502, 503, 504})
    )

    def backoff_seconds(self, attempt: int, retry_after: float | None) -> float:
        """Seconds to wait before the next attempt (0-indexed ``attempt``)."""
        if retry_after is not None:
            return min(retry_after, self.max_backoff)
        return min(self.backoff_factor * (2.0**attempt), self.max_backoff)


def build_headers(
    *,
    secret_key: str,
    api_version: str = DEFAULT_API_VERSION,
    idempotency_key: str | None = None,
) -> dict[str, str]:
    """Build the headers common to every Merchant API request."""
    headers = {
        "Authorization": f"Bearer {secret_key}",
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Revolut-Api-Version": api_version,
        "User-Agent": f"revolut-python/{__version__}",
    }
    if idempotency_key is not None:
        headers["Idempotency-Key"] = idempotency_key
    return headers


def _parse_retry_after(value: str | None) -> float | None:
    if not value:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def parse_response(response: httpx.Response) -> Any:
    """Return parsed JSON for a 2xx response, or raise the mapped error.

    A ``204 No Content`` (or any empty body) returns ``None``.
    """
    if response.is_success:
        if not response.content:
            return None
        return response.json()

    body: Any = None
    code: str | None = None
    message = f"HTTP {response.status_code}"
    try:
        body = response.json()
    except ValueError:
        body = response.text or None
    if isinstance(body, dict):
        code = body.get("code")
        message = body.get("message") or message

    request_id = response.headers.get("X-Request-Id")
    exc_class = exception_for_status(response.status_code)

    if exc_class is RateLimitError:
        raise RateLimitError(
            message,
            status_code=response.status_code,
            retry_after=_parse_retry_after(response.headers.get("Retry-After")),
            code=code,
            request_id=request_id,
            body=body,
        )
    raise exc_class(
        message,
        status_code=response.status_code,
        code=code,
        request_id=request_id,
        body=body,
    )


def is_retryable(exc: APIStatusError, attempt: int, config: RetryConfig) -> bool:
    """Whether a failed attempt should be retried."""
    return attempt < config.max_retries and exc.status_code in config.retry_statuses


def retry_after_from(exc: APIStatusError) -> float | None:
    """Extract a ``Retry-After`` hint from a rate-limit error, if present."""
    if isinstance(exc, RateLimitError):
        return exc.retry_after
    return None
