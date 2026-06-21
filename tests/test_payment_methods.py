"""Tests for the saved payment methods resource (sync + async)."""

from __future__ import annotations

import json

import httpx
import respx

BASE = "https://sandbox-merchant.revolut.com"
PM = "/api/customers/cus_1/payment-methods"


@respx.mock
def test_list_payment_methods_with_only_merchant(client):
    route = respx.get(f"{BASE}{PM}").mock(
        return_value=httpx.Response(200, json={"payment_methods": [{"id": "pm_1"}, {"id": "pm_2"}]})
    )
    methods = client.payment_methods.list("cus_1", only_merchant=True)
    assert [m.id for m in methods] == ["pm_1", "pm_2"]
    assert route.calls.last.request.url.params["only_merchant"] == "true"


@respx.mock
def test_retrieve_payment_method(client):
    respx.get(f"{BASE}{PM}/pm_1").mock(
        return_value=httpx.Response(200, json={"id": "pm_1", "type": "card", "state": "active"})
    )
    pm = client.payment_methods.retrieve("cus_1", "pm_1")
    assert pm.type == "card"
    assert pm.state == "active"


@respx.mock
def test_update_payment_method(client):
    route = respx.patch(f"{BASE}{PM}/pm_1").mock(
        return_value=httpx.Response(200, json={"id": "pm_1"})
    )
    client.payment_methods.update("cus_1", "pm_1", method_details={"label": "main"})
    assert json.loads(route.calls.last.request.content) == {"method_details": {"label": "main"}}


@respx.mock
def test_delete_payment_method(client):
    respx.delete(f"{BASE}{PM}/pm_1").mock(return_value=httpx.Response(204))
    assert client.payment_methods.delete("cus_1", "pm_1") is None


@respx.mock
async def test_async_payment_methods(async_client):
    respx.get(f"{BASE}{PM}").mock(return_value=httpx.Response(200, json=[{"id": "pm_1"}]))
    respx.get(f"{BASE}{PM}/pm_1").mock(return_value=httpx.Response(200, json={"id": "pm_1"}))
    respx.delete(f"{BASE}{PM}/pm_1").mock(return_value=httpx.Response(204))
    assert [m.id for m in await async_client.payment_methods.list("cus_1")] == ["pm_1"]
    assert (await async_client.payment_methods.retrieve("cus_1", "pm_1")).id == "pm_1"
    assert await async_client.payment_methods.delete("cus_1", "pm_1") is None
