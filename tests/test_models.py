"""Tests for models: Money conversions, Order helpers, forward-compat."""

from __future__ import annotations

from decimal import Decimal

import pytest

from revolut import Money, Order, OrderList


@pytest.mark.parametrize(
    ("major", "currency", "minor"),
    [
        ("10.99", "GBP", 1099),
        ("70.34", "EUR", 7034),
        ("1000", "JPY", 1000),
        ("1.234", "BHD", 1234),
        (5, "USD", 500),
    ],
)
def test_money_from_major(major, currency, minor):
    assert Money.from_major(major, currency).amount == minor


@pytest.mark.parametrize(
    ("minor", "currency", "major"),
    [
        (1099, "GBP", Decimal("10.99")),
        (1000, "JPY", Decimal("1000")),
        (1234, "BHD", Decimal("1.234")),
    ],
)
def test_money_to_major(minor, currency, major):
    assert Money(minor, currency).to_major() == major


def test_money_equality_and_currency_normalised():
    assert Money(100, "gbp") == Money(100, "GBP")
    assert Money(100, "GBP") != Money(101, "GBP")


def test_order_public_token_prefers_token():
    assert Order(token="tok", public_id="leg").public_token == "tok"
    assert Order(public_id="leg").public_token == "leg"


def test_order_keeps_unknown_fields():
    order = Order.model_validate({"id": "ord", "brand_new_field": 42})
    assert order.id == "ord"
    assert order.model_extra["brand_new_field"] == 42


def test_order_list_parses_orders():
    parsed = OrderList.model_validate({"orders": [{"id": "a"}, {"id": "b"}]})
    assert [o.id for o in parsed.orders] == ["a", "b"]
