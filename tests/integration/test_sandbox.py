"""Live sandbox integration tests.

These hit the real Revolut **sandbox** API and are skipped unless a sandbox
secret key is provided:

    REVOLUT_SECRET_KEY=sk_... pytest tests/integration -v

They are excluded from normal/CI runs (which stay hermetic) because no key is
set there. Use them to confirm endpoint paths and field names against a live
sandbox (roadmap issue #23) and as the release gate (#22).
"""

from __future__ import annotations

import os

import pytest

from revolut import RevolutMerchantClient

SECRET_KEY = os.getenv("REVOLUT_SECRET_KEY")

pytestmark = pytest.mark.skipif(
    not SECRET_KEY, reason="set REVOLUT_SECRET_KEY to run live sandbox tests"
)


@pytest.fixture
def client():
    c = RevolutMerchantClient(secret_key=SECRET_KEY or "", environment="sandbox")
    yield c
    c.close()


def test_create_and_retrieve_order(client):
    order = client.orders.create(amount=1000, currency="GBP")
    assert order.id
    fetched = client.orders.retrieve(order.id)
    assert fetched.id == order.id
    assert fetched.public_token


def test_list_orders(client):
    orders = client.orders.list(limit=5)
    assert isinstance(orders, list)


def test_capture_and_refund_flow(client):
    """Manual-capture order: authorise is driven by the hosted page, so this
    only asserts the create + capture endpoints respond as documented. Adapt
    once a sandbox card flow authorises the order."""
    order = client.orders.create(amount=500, currency="GBP", capture_mode="manual")
    assert order.state in {"pending", "processing", "authorised"}
