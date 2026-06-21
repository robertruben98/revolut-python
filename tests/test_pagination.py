"""Tests for auto-pagination helpers (orders + customers, sync + async)."""

from __future__ import annotations

import httpx
import respx

BASE = "https://sandbox-merchant.revolut.com"


def _orders_responder():
    calls = {"n": 0}

    def responder(request):
        calls["n"] += 1
        if calls["n"] == 1:
            return httpx.Response(
                200,
                json={
                    "orders": [
                        {"id": "o1", "created_at": "2026-01-02T00:00:00Z"},
                        {"id": "o2", "created_at": "2026-01-01T00:00:00Z"},
                    ]
                },
            )
        return httpx.Response(
            200, json={"orders": [{"id": "o3", "created_at": "2025-12-31T00:00:00Z"}]}
        )

    return calls, responder


@respx.mock
def test_orders_iter_follows_created_before(client):
    calls, responder = _orders_responder()
    route = respx.get(f"{BASE}/api/orders").mock(side_effect=responder)
    ids = [o.id for o in client.orders.iter(limit=2)]
    assert ids == ["o1", "o2", "o3"]
    assert calls["n"] == 2
    # second request carries the cursor from the oldest order of page 1
    assert route.calls[1].request.url.params["created_before"] == "2026-01-01T00:00:00Z"


@respx.mock
def test_orders_iter_respects_max_items(client):
    _, responder = _orders_responder()
    respx.get(f"{BASE}/api/orders").mock(side_effect=responder)
    ids = [o.id for o in client.orders.iter(limit=2, max_items=1)]
    assert ids == ["o1"]


@respx.mock
async def test_async_orders_iter(async_client):
    _, responder = _orders_responder()
    respx.get(f"{BASE}/api/orders").mock(side_effect=responder)
    ids = [o.id async for o in async_client.orders.iter(limit=2)]
    assert ids == ["o1", "o2", "o3"]


def _customers_responder():
    calls = {"n": 0}

    def responder(request):
        calls["n"] += 1
        if calls["n"] == 1:
            return httpx.Response(
                200, json={"customers": [{"id": "c1"}, {"id": "c2"}], "page_token": "tok2"}
            )
        return httpx.Response(200, json={"customers": [{"id": "c3"}]})

    return calls, responder


@respx.mock
def test_customers_iter_follows_page_token(client):
    calls, responder = _customers_responder()
    route = respx.get(f"{BASE}/api/customers").mock(side_effect=responder)
    ids = [c.id for c in client.customers.iter(limit=2)]
    assert ids == ["c1", "c2", "c3"]
    assert calls["n"] == 2
    assert route.calls[1].request.url.params["page_token"] == "tok2"


@respx.mock
def test_customers_iter_stops_without_token(client):
    # full page but no next token -> stop after first page
    respx.get(f"{BASE}/api/customers").mock(
        return_value=httpx.Response(200, json={"customers": [{"id": "c1"}, {"id": "c2"}]})
    )
    ids = [c.id for c in client.customers.iter(limit=2)]
    assert ids == ["c1", "c2"]


@respx.mock
async def test_async_customers_iter(async_client):
    _, responder = _customers_responder()
    respx.get(f"{BASE}/api/customers").mock(side_effect=responder)
    ids = [c.id async for c in async_client.customers.iter(limit=2)]
    assert ids == ["c1", "c2", "c3"]
