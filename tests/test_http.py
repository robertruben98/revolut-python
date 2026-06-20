"""Tests for the HTTP transports: headers, retries, error propagation."""

from __future__ import annotations

import httpx
import pytest
import respx

from revolut import AsyncRevolutMerchantClient, RevolutMerchantClient
from revolut._http.base import RetryConfig, build_headers
from revolut._version import __version__
from revolut.exceptions import APIConnectionError, ServerError

BASE = "https://sandbox-merchant.revolut.com"


def test_build_headers_sets_auth_version_and_idempotency():
    headers = build_headers(secret_key="sk_x", api_version="2026-04-20", idempotency_key="idem-1")
    assert headers["Authorization"] == "Bearer sk_x"
    assert headers["Revolut-Api-Version"] == "2026-04-20"
    assert headers["Idempotency-Key"] == "idem-1"
    assert headers["User-Agent"] == f"revolut-python/{__version__}"


def test_build_headers_omits_idempotency_when_absent():
    assert "Idempotency-Key" not in build_headers(secret_key="sk_x")


@respx.mock
def test_sync_sends_auth_and_version_headers(client):
    route = respx.get(f"{BASE}/api/orders/ord_1").mock(
        return_value=httpx.Response(200, json={"id": "ord_1"})
    )
    client.orders.retrieve("ord_1")
    req = route.calls.last.request
    assert req.headers["authorization"] == "Bearer sk_test_secret"
    assert req.headers["revolut-api-version"] == "2026-04-20"


@respx.mock
def test_sync_retries_on_429_then_succeeds():
    calls = {"n": 0}

    def responder(request):
        calls["n"] += 1
        if calls["n"] == 1:
            return httpx.Response(429, headers={"Retry-After": "0"}, json={"message": "x"})
        return httpx.Response(200, json={"id": "ord_1"})

    respx.get(f"{BASE}/api/orders/ord_1").mock(side_effect=responder)
    c = RevolutMerchantClient(
        secret_key="sk",
        environment="sandbox",
        retry=RetryConfig(max_retries=2, backoff_factor=0),
    )
    order = c.orders.retrieve("ord_1")
    assert order.id == "ord_1"
    assert calls["n"] == 2
    c.close()


@respx.mock
def test_sync_raises_after_exhausting_retries():
    respx.get(f"{BASE}/api/orders/ord_1").mock(
        return_value=httpx.Response(503, json={"message": "down"})
    )
    c = RevolutMerchantClient(
        secret_key="sk",
        environment="sandbox",
        retry=RetryConfig(max_retries=1, backoff_factor=0),
    )
    with pytest.raises(ServerError):
        c.orders.retrieve("ord_1")
    c.close()


@respx.mock
def test_sync_wraps_network_errors():
    respx.get(f"{BASE}/api/orders/ord_1").mock(side_effect=httpx.ConnectError("boom"))
    c = RevolutMerchantClient(
        secret_key="sk",
        environment="sandbox",
        retry=RetryConfig(max_retries=0),
    )
    with pytest.raises(APIConnectionError):
        c.orders.retrieve("ord_1")
    c.close()


@respx.mock
async def test_async_retries_on_429_then_succeeds():
    calls = {"n": 0}

    def responder(request):
        calls["n"] += 1
        if calls["n"] == 1:
            return httpx.Response(429, headers={"Retry-After": "0"}, json={"message": "x"})
        return httpx.Response(200, json={"id": "ord_1"})

    respx.get(f"{BASE}/api/orders/ord_1").mock(side_effect=responder)
    c = AsyncRevolutMerchantClient(
        secret_key="sk",
        environment="sandbox",
        retry=RetryConfig(max_retries=2, backoff_factor=0),
    )
    order = await c.orders.retrieve("ord_1")
    assert order.id == "ord_1"
    assert calls["n"] == 2
    await c.aclose()
