"""Location models."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from .common import RevolutModel


class Location(RevolutModel):
    """A merchant location / domain used for checkout."""

    id: str | None = None
    name: str | None = None
    type: str | None = None
    details: dict[str, Any] | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
