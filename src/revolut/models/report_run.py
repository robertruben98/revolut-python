"""Report run models."""

from __future__ import annotations

from datetime import datetime

from .common import RevolutModel


class ReportRun(RevolutModel):
    """An asynchronous report generation job."""

    id: str | None = None
    state: str | None = None
    report_type: str | None = None
    from_date: str | None = None
    to_date: str | None = None
    download_url: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
