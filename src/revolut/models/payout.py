"""Payout models."""

from __future__ import annotations

from datetime import datetime

from .common import RevolutModel


class Payout(RevolutModel):
    """A settlement payout to the merchant's account."""

    id: str | None = None
    state: str | None = None
    amount: int | None = None
    currency: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
