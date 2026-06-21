"""Saved payment method (tokenization) models."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from .common import RevolutModel


class PaymentMethod(RevolutModel):
    """A payment method saved against a customer (tokenized)."""

    id: str | None = None
    customer_id: str | None = None
    type: str | None = None
    state: str | None = None
    method_details: dict[str, Any] | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
