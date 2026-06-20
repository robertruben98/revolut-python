"""Tests for webhook signature verification."""

from __future__ import annotations

import hashlib
import hmac

import pytest

from revolut import compute_signature, verify_signature
from revolut.exceptions import SignatureVerificationError

SECRET = "wsk_test_secret"
TS = "1700000000000"  # unix ms
NOW = 1700000000.0  # same instant, seconds
BODY = '{"event":"ORDER_COMPLETED","order_id":"ord_1"}'


def _sig(body=BODY, ts=TS, secret=SECRET):
    return compute_signature(timestamp=ts, raw_body=body, signing_secret=secret)


def test_compute_signature_matches_documented_formula():
    expected = (
        "v1=" + hmac.new(SECRET.encode(), f"v1.{TS}.{BODY}".encode(), hashlib.sha256).hexdigest()
    )
    assert _sig() == expected


def test_verify_valid_signature_returns_payload():
    payload = verify_signature(
        BODY,
        signature_header=_sig(),
        timestamp_header=TS,
        signing_secret=SECRET,
        now=NOW,
    )
    assert payload.event == "ORDER_COMPLETED"
    assert payload.order_id == "ord_1"


def test_verify_accepts_bytes_body():
    payload = verify_signature(
        BODY.encode(),
        signature_header=_sig(),
        timestamp_header=TS,
        signing_secret=SECRET,
        now=NOW,
    )
    assert payload.event == "ORDER_COMPLETED"


def test_verify_accepts_multiple_signatures_during_rotation():
    header = f"v1=deadbeef,{_sig()}"
    payload = verify_signature(
        BODY, signature_header=header, timestamp_header=TS, signing_secret=SECRET, now=NOW
    )
    assert payload.event == "ORDER_COMPLETED"


def test_verify_rejects_tampered_body():
    with pytest.raises(SignatureVerificationError, match="No matching signature"):
        verify_signature(
            '{"event":"ORDER_FAILED"}',
            signature_header=_sig(),
            timestamp_header=TS,
            signing_secret=SECRET,
            now=NOW,
        )


def test_verify_rejects_wrong_secret():
    with pytest.raises(SignatureVerificationError):
        verify_signature(
            BODY,
            signature_header=_sig(secret="wsk_other"),
            timestamp_header=TS,
            signing_secret=SECRET,
            now=NOW,
        )


def test_verify_rejects_stale_timestamp():
    with pytest.raises(SignatureVerificationError, match="tolerance"):
        verify_signature(
            BODY,
            signature_header=_sig(),
            timestamp_header=TS,
            signing_secret=SECRET,
            now=NOW + 600,  # 10 minutes later
        )


def test_verify_rejects_invalid_timestamp_header():
    with pytest.raises(SignatureVerificationError, match="Invalid timestamp"):
        verify_signature(
            BODY,
            signature_header=_sig(),
            timestamp_header="not-a-number",
            signing_secret=SECRET,
            now=NOW,
        )
