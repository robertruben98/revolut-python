"""Dispute models."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from .common import RevolutModel


class Dispute(RevolutModel):
    """A payment dispute / chargeback case."""

    id: str | None = None
    order_id: str | None = None
    state: str | None = None
    reason: str | None = None
    amount: int | None = None
    currency: str | None = None
    evidence: dict[str, Any] | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
