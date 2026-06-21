"""Synchronous transport built on :class:`httpx.Client`."""

from __future__ import annotations

import time
from collections.abc import Callable
from typing import Any

import httpx

from ..config import DEFAULT_API_VERSION, DEFAULT_TIMEOUT, Environment, base_url_for
from ..exceptions import APIConnectionError, APIStatusError
from .base import (
    RequestSpec,
    RetryConfig,
    build_headers,
    is_retryable,
    logger,
    parse_response,
    retry_after_from,
)


class SyncTransport:
    """Issues requests against the Merchant API and returns parsed JSON."""

    def __init__(
        self,
        *,
        secret_key: str,
        environment: Environment | str = Environment.SANDBOX,
        api_version: str = DEFAULT_API_VERSION,
        timeout: float = DEFAULT_TIMEOUT,
        retry: RetryConfig | None = None,
        http_client: httpx.Client | None = None,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self._secret_key = secret_key
        self._api_version = api_version
        self._retry = retry or RetryConfig()
        self._sleep = sleep
        self._owns_client = http_client is None
        self._client = http_client or httpx.Client(
            base_url=base_url_for(environment),
            timeout=timeout,
        )

    def request(self, spec: RequestSpec) -> Any:
        headers = build_headers(
            secret_key=self._secret_key,
            api_version=self._api_version,
            idempotency_key=spec.idempotency_key,
        )
        extra: dict[str, Any] = {}
        if spec.timeout is not None:
            extra["timeout"] = spec.timeout
        attempt = 0
        while True:
            logger.debug("revolut request: %s %s", spec.method, spec.path)
            try:
                response = self._client.request(
                    spec.method,
                    spec.path,
                    params=spec.params,
                    json=spec.json,
                    headers=headers,
                    **extra,
                )
            except httpx.HTTPError as exc:  # network/timeout
                raise APIConnectionError(str(exc)) from exc
            logger.debug("revolut response: %s -> %s", spec.path, response.status_code)
            try:
                return parse_response(response)
            except APIStatusError as exc:
                if not is_retryable(exc, attempt, self._retry):
                    raise
                delay = self._retry.backoff_seconds(attempt, retry_after_from(exc))
                logger.debug(
                    "revolut retry %s after %.3fs (status %s)", attempt + 1, delay, exc.status_code
                )
                self._sleep(delay)
                attempt += 1

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def __enter__(self) -> SyncTransport:
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()
