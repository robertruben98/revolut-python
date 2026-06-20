"""Order models."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import Field

from .common import RevolutModel
from .customer import Customer
from .payment import Payment


class Order(RevolutModel):
    """A Merchant API order.

    Amounts are integers in the currency's minor units. The public identifier is
    ``token``; ``public_id`` is accepted for compatibility with the legacy
    create-order endpoint.
    """

    id: str | None = None
    token: str | None = None
    public_id: str | None = None
    type: str | None = None
    state: str | None = None
    amount: int | None = None
    currency: str | None = None
    outstanding_amount: int | None = None
    capture_mode: str | None = None
    enforce_challenge: str | None = None
    related_order_id: str | None = None
    customer: Customer | None = None
    payments: list[Payment] | None = None
    metadata: dict[str, Any] | None = None
    merchant_order_data: dict[str, Any] | None = None
    line_items: list[dict[str, Any]] | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @property
    def public_token(self) -> str | None:
        """The public identifier, preferring ``token`` over legacy ``public_id``."""
        return self.token or self.public_id


class OrderList(RevolutModel):
    """A page of orders as returned by the list endpoint."""

    orders: list[Order] = Field(default_factory=list)
