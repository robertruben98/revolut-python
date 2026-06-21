"""Report runs resource (sync + async).

Path strings follow Revolut's documented REST convention; confirmed against a
live sandbox in #23.
"""

from __future__ import annotations

from typing import Any

from .._http.base import RequestSpec
from ..models.report_run import ReportRun
from .base import AsyncResource, SyncResource, clean_params, drop_none

_BASE = "/api/report-runs"


def _parse_list(raw: Any) -> list[ReportRun]:
    if isinstance(raw, dict):
        raw = raw.get("report_runs", raw.get("data", []))
    return [ReportRun.model_validate(item) for item in (raw or [])]


class ReportRunsResource(SyncResource):
    """Synchronous report-run operations."""

    def create(self, *, idempotency_key: str | None = None, **fields: Any) -> ReportRun:
        spec = RequestSpec("POST", _BASE, json=drop_none(fields), idempotency_key=idempotency_key)
        return ReportRun.model_validate(self._transport.request(spec))

    def retrieve(self, report_run_id: str) -> ReportRun:
        spec = RequestSpec("GET", f"{_BASE}/{report_run_id}")
        return ReportRun.model_validate(self._transport.request(spec))

    def list(self, **params: Any) -> list[ReportRun]:
        spec = RequestSpec("GET", _BASE, params=clean_params(params))
        return _parse_list(self._transport.request(spec))


class AsyncReportRunsResource(AsyncResource):
    """Asynchronous report-run operations."""

    async def create(self, *, idempotency_key: str | None = None, **fields: Any) -> ReportRun:
        spec = RequestSpec("POST", _BASE, json=drop_none(fields), idempotency_key=idempotency_key)
        return ReportRun.model_validate(await self._transport.request(spec))

    async def retrieve(self, report_run_id: str) -> ReportRun:
        spec = RequestSpec("GET", f"{_BASE}/{report_run_id}")
        return ReportRun.model_validate(await self._transport.request(spec))

    async def list(self, **params: Any) -> list[ReportRun]:
        spec = RequestSpec("GET", _BASE, params=clean_params(params))
        return _parse_list(await self._transport.request(spec))
