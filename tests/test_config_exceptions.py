"""Tests for config and the exception hierarchy."""

from __future__ import annotations

import httpx
import pytest

from revolut._http.base import parse_response
from revolut.config import Environment, base_url_for
from revolut.exceptions import (
    APIStatusError,
    AuthenticationError,
    BadRequestError,
    InvalidRequestError,
    NotFoundError,
    PermissionDeniedError,
    RateLimitError,
    ServerError,
    exception_for_status,
)


def test_base_url_for_accepts_enum_and_string():
    assert base_url_for(Environment.SANDBOX) == "https://sandbox-merchant.revolut.com"
    assert base_url_for("production") == "https://merchant.revolut.com"


def test_base_url_for_rejects_unknown():
    with pytest.raises(ValueError):
        base_url_for("staging")


@pytest.mark.parametrize(
    ("status", "expected"),
    [
        (400, BadRequestError),
        (401, AuthenticationError),
        (403, PermissionDeniedError),
        (404, NotFoundError),
        (422, InvalidRequestError),
        (429, RateLimitError),
        (500, ServerError),
        (503, ServerError),
        (418, APIStatusError),
    ],
)
def test_exception_for_status(status, expected):
    assert exception_for_status(status) is expected


def test_parse_response_success_returns_json():
    resp = httpx.Response(200, json={"id": "abc"})
    assert parse_response(resp) == {"id": "abc"}


def test_parse_response_empty_returns_none():
    resp = httpx.Response(204)
    assert parse_response(resp) is None


def test_parse_response_maps_error_body():
    resp = httpx.Response(
        422,
        json={"code": "invalid_state", "message": "Bad state", "timestamp": 1},
        headers={"X-Request-Id": "req_1"},
    )
    with pytest.raises(InvalidRequestError) as exc:
        parse_response(resp)
    assert exc.value.status_code == 422
    assert exc.value.code == "invalid_state"
    assert exc.value.message == "Bad state"
    assert exc.value.request_id == "req_1"


def test_parse_response_rate_limit_parses_retry_after():
    resp = httpx.Response(429, headers={"Retry-After": "2.5"}, json={"message": "slow"})
    with pytest.raises(RateLimitError) as exc:
        parse_response(resp)
    assert exc.value.retry_after == 2.5
