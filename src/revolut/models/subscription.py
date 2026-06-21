"""Subscription models."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from .common import RevolutModel


class Subscription(RevolutModel):
    """A recurring-payment subscription."""

    id: str | None = None
    customer_id: str | None = None
    state: str | None = None
    amount: int | None = None
    currency: str | None = None
    payment_method_id: str | None = None
    metadata: dict[str, Any] | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
