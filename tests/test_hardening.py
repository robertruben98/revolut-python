"""Tests for hardening: backoff jitter, logging and per-request timeout."""

from __future__ import annotations

import logging

import httpx
import respx

from revolut._http.base import RequestSpec, RetryConfig
from revolut._http.sync_client import SyncTransport

BASE = "https://sandbox-merchant.revolut.com"


def test_backoff_without_jitter_is_deterministic():
    cfg = RetryConfig(backoff_factor=0.5, jitter=0.0)
    assert cfg.backoff_seconds(0, None) == 0.5
    assert cfg.backoff_seconds(1, None) == 1.0


def test_backoff_with_jitter_uses_rng_within_bounds():
    cfg = RetryConfig(backoff_factor=0.5, jitter=0.5)
    base = 0.5  # attempt 0
    assert cfg.backoff_seconds(0, None, rng=lambda: 0.0) == base
    assert cfg.backoff_seconds(0, None, rng=lambda: 1.0) == base + 0.5 * base


def test_backoff_respects_retry_after_over_computed():
    cfg = RetryConfig(jitter=0.0)
    assert cfg.backoff_seconds(5, retry_after=2.0) == 2.0


def test_backoff_capped_at_max():
    cfg = RetryConfig(backoff_factor=100.0, max_backoff=10.0, jitter=1.0)
    assert cfg.backoff_seconds(3, None, rng=lambda: 1.0) == 10.0


@respx.mock
def test_request_logs_at_debug(caplog):
    respx.get(f"{BASE}/api/orders/o").mock(return_value=httpx.Response(200, json={"id": "o"}))
    transport = SyncTransport(secret_key="sk", environment="sandbox")
    with caplog.at_level(logging.DEBUG, logger="revolut"):
        transport.request(RequestSpec("GET", "/api/orders/o"))
    transport.close()
    messages = [r.getMessage() for r in caplog.records]
    assert any("revolut request: GET /api/orders/o" in m for m in messages)
    assert any("revolut response" in m for m in messages)


@respx.mock
def test_per_request_timeout_is_accepted():
    route = respx.get(f"{BASE}/api/orders/o").mock(
        return_value=httpx.Response(200, json={"id": "o"})
    )
    transport = SyncTransport(secret_key="sk", environment="sandbox")
    result = transport.request(RequestSpec("GET", "/api/orders/o", timeout=1.5))
    transport.close()
    assert result == {"id": "o"}
    assert route.called
