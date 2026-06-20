"""Customer models."""

from __future__ import annotations

from datetime import datetime

from .common import RevolutModel


class Customer(RevolutModel):
    """A Merchant API customer."""

    id: str | None = None
    full_name: str | None = None
    business_name: str | None = None
    email: str | None = None
    phone: str | None = None
    date_of_birth: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
