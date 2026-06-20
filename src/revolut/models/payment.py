"""Payment models (payments are sub-objects of an order)."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from .common import RevolutModel


class Payment(RevolutModel):
    """A single payment attempt against an order."""

    id: str | None = None
    order_id: str | None = None
    payment_method: dict[str, Any] | None = None
    state: str | None = None
    amount: int | None = None
    currency: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
