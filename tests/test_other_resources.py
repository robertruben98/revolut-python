"""Tests for payments, refunds, customers and webhooks resources."""

from __future__ import annotations

import json

import httpx
import respx

BASE = "https://sandbox-merchant.revolut.com"


# --- payments ---------------------------------------------------------------
@respx.mock
def test_list_payments_for_order(client):
    respx.get(f"{BASE}/api/orders/ord_1/payments").mock(
        return_value=httpx.Response(200, json=[{"id": "pay_1"}, {"id": "pay_2"}])
    )
    payments = client.payments.list_for_order("ord_1")
    assert [p.id for p in payments] == ["pay_1", "pay_2"]


@respx.mock
def test_retrieve_payment(client):
    respx.get(f"{BASE}/api/payments/pay_1").mock(
        return_value=httpx.Response(200, json={"id": "pay_1", "state": "completed"})
    )
    assert client.payments.retrieve("pay_1").state == "completed"


@respx.mock
def test_pay_with_saved_method(client):
    route = respx.post(f"{BASE}/api/orders/ord_1/payments").mock(
        return_value=httpx.Response(201, json={"id": "pay_1"})
    )
    client.payments.pay("ord_1", payment_method_id="pm_1", idempotency_key="i1")
    assert json.loads(route.calls.last.request.content) == {"payment_method_id": "pm_1"}
    assert route.calls.last.request.headers["idempotency-key"] == "i1"


# --- refunds ----------------------------------------------------------------
@respx.mock
def test_create_refund_returns_refund_order(client):
    route = respx.post(f"{BASE}/api/orders/ord_1/refund").mock(
        return_value=httpx.Response(
            201, json={"id": "ord_2", "type": "refund", "related_order_id": "ord_1"}
        )
    )
    refund = client.refunds.create("ord_1", amount=250, idempotency_key="r1")
    assert refund.type == "refund"
    assert refund.related_order_id == "ord_1"
    assert json.loads(route.calls.last.request.content) == {"amount": 250}
    assert route.calls.last.request.headers["idempotency-key"] == "r1"


@respx.mock
async def test_async_create_refund(async_client):
    respx.post(f"{BASE}/api/orders/ord_1/refund").mock(
        return_value=httpx.Response(201, json={"id": "ord_2", "type": "refund"})
    )
    refund = await async_client.refunds.create("ord_1", amount=100)
    assert refund.id == "ord_2"


# --- customers --------------------------------------------------------------
@respx.mock
def test_create_customer(client):
    route = respx.post(f"{BASE}/api/customers").mock(
        return_value=httpx.Response(201, json={"id": "cus_1", "email": "a@b.com"})
    )
    cust = client.customers.create(full_name="Ann", email="a@b.com")
    assert cust.id == "cus_1"
    assert json.loads(route.calls.last.request.content) == {
        "full_name": "Ann",
        "email": "a@b.com",
    }


@respx.mock
def test_list_customers_with_page_token(client):
    route = respx.get(f"{BASE}/api/customers").mock(
        return_value=httpx.Response(200, json={"customers": [{"id": "cus_1"}]})
    )
    customers = client.customers.list(limit=10, page_token="tok")
    assert [c.id for c in customers] == ["cus_1"]
    assert dict(route.calls.last.request.url.params) == {"limit": "10", "page_token": "tok"}


@respx.mock
def test_delete_customer_returns_none(client):
    respx.delete(f"{BASE}/api/customers/cus_1").mock(return_value=httpx.Response(204))
    assert client.customers.delete("cus_1") is None


# --- webhooks (management) --------------------------------------------------
@respx.mock
def test_create_webhook(client):
    route = respx.post(f"{BASE}/api/1.0/webhooks").mock(
        return_value=httpx.Response(
            201,
            json={
                "id": "wh_1",
                "url": "https://x/cb",
                "events": ["ORDER_COMPLETED"],
                "signing_secret": "wsk_abc",
            },
        )
    )
    wh = client.webhooks.create(url="https://x/cb", events=["ORDER_COMPLETED"])
    assert wh.signing_secret == "wsk_abc"
    assert json.loads(route.calls.last.request.content) == {
        "url": "https://x/cb",
        "events": ["ORDER_COMPLETED"],
    }


@respx.mock
def test_rotate_webhook_secret(client):
    respx.post(f"{BASE}/api/1.0/webhooks/wh_1/rotate-signing-secret").mock(
        return_value=httpx.Response(200, json={"id": "wh_1", "signing_secret": "wsk_new"})
    )
    assert client.webhooks.rotate_signing_secret("wh_1").signing_secret == "wsk_new"


@respx.mock
def test_list_and_delete_webhook(client):
    respx.get(f"{BASE}/api/1.0/webhooks").mock(
        return_value=httpx.Response(200, json=[{"id": "wh_1"}])
    )
    respx.delete(f"{BASE}/api/1.0/webhooks/wh_1").mock(return_value=httpx.Response(204))
    assert [w.id for w in client.webhooks.list()] == ["wh_1"]
    assert client.webhooks.delete("wh_1") is None


@respx.mock
async def test_async_webhook_create(async_client):
    respx.post(f"{BASE}/api/1.0/webhooks").mock(
        return_value=httpx.Response(201, json={"id": "wh_1", "signing_secret": "wsk_a"})
    )
    wh = await async_client.webhooks.create(url="https://x", events=["ORDER_FAILED"])
    assert wh.id == "wh_1"
