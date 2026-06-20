"""Tests for the orders resource (sync + async)."""

from __future__ import annotations

import json

import httpx
import respx

BASE = "https://sandbox-merchant.revolut.com"


@respx.mock
def test_create_order_posts_minor_units(client):
    route = respx.post(f"{BASE}/api/orders").mock(
        return_value=httpx.Response(201, json={"id": "ord_1", "token": "tok_1", "state": "pending"})
    )
    order = client.orders.create(
        amount=1000, currency="GBP", capture_mode="manual", idempotency_key="idem-1"
    )
    assert order.id == "ord_1"
    assert order.public_token == "tok_1"
    req = route.calls.last.request
    body = json.loads(req.content)
    assert body == {"amount": 1000, "currency": "GBP", "capture_mode": "manual"}
    assert req.headers["idempotency-key"] == "idem-1"


@respx.mock
def test_create_order_merges_extra_fields(client):
    route = respx.post(f"{BASE}/api/orders").mock(
        return_value=httpx.Response(201, json={"id": "ord_1"})
    )
    client.orders.create(
        amount=500,
        currency="EUR",
        merchant_order_data={"reference": "A1"},
        description="hello",
    )
    body = json.loads(route.calls.last.request.content)
    assert body["merchant_order_data"] == {"reference": "A1"}
    assert body["description"] == "hello"


@respx.mock
def test_retrieve_order(client):
    respx.get(f"{BASE}/api/orders/ord_1").mock(
        return_value=httpx.Response(200, json={"id": "ord_1", "state": "completed"})
    )
    order = client.orders.retrieve("ord_1")
    assert order.state == "completed"


@respx.mock
def test_list_orders_unwraps_and_passes_params(client):
    route = respx.get(f"{BASE}/api/orders").mock(
        return_value=httpx.Response(200, json={"orders": [{"id": "a"}, {"id": "b"}]})
    )
    orders = client.orders.list(limit=50, state="completed")
    assert [o.id for o in orders] == ["a", "b"]
    assert dict(route.calls.last.request.url.params) == {"limit": "50", "state": "completed"}


@respx.mock
def test_update_order_patches(client):
    route = respx.patch(f"{BASE}/api/orders/ord_1").mock(
        return_value=httpx.Response(200, json={"id": "ord_1"})
    )
    client.orders.update("ord_1", metadata={"k": "v"})
    assert json.loads(route.calls.last.request.content) == {"metadata": {"k": "v"}}


@respx.mock
def test_capture_order_with_amount(client):
    route = respx.post(f"{BASE}/api/orders/ord_1/capture").mock(
        return_value=httpx.Response(200, json={"id": "ord_1", "state": "completed"})
    )
    order = client.orders.capture("ord_1", amount=750)
    assert order.state == "completed"
    assert json.loads(route.calls.last.request.content) == {"amount": 750}


@respx.mock
def test_capture_order_without_amount_sends_no_body(client):
    route = respx.post(f"{BASE}/api/orders/ord_1/capture").mock(
        return_value=httpx.Response(200, json={"id": "ord_1"})
    )
    client.orders.capture("ord_1")
    assert route.calls.last.request.content in (b"", b"null")


@respx.mock
def test_cancel_order(client):
    respx.post(f"{BASE}/api/orders/ord_1/cancel").mock(
        return_value=httpx.Response(200, json={"id": "ord_1", "state": "cancelled"})
    )
    assert client.orders.cancel("ord_1").state == "cancelled"


@respx.mock
async def test_async_create_and_capture(async_client):
    respx.post(f"{BASE}/api/orders").mock(
        return_value=httpx.Response(201, json={"id": "ord_1", "token": "tok"})
    )
    respx.post(f"{BASE}/api/orders/ord_1/capture").mock(
        return_value=httpx.Response(200, json={"id": "ord_1", "state": "completed"})
    )
    order = await async_client.orders.create(amount=1000, currency="GBP")
    assert order.id == "ord_1"
    captured = await async_client.orders.capture("ord_1", amount=1000)
    assert captured.state == "completed"


@respx.mock
async def test_async_list_orders(async_client):
    respx.get(f"{BASE}/api/orders").mock(
        return_value=httpx.Response(200, json={"orders": [{"id": "a"}]})
    )
    orders = await async_client.orders.list()
    assert [o.id for o in orders] == ["a"]
