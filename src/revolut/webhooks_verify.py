"""Verify the authenticity of webhook payloads delivered by Revolut.

Revolut signs each delivery with HMAC-SHA256 over ``v1.{timestamp}.{raw_body}``
and sends the result in the ``Revolut-Signature`` header (``v1=<hex>``; possibly
several comma-separated values during signing-secret rotation), alongside the
``Revolut-Request-Timestamp`` header (Unix milliseconds).
"""

from __future__ import annotations

import hashlib
import hmac
import json
import time

from .exceptions import SignatureVerificationError
from .models.webhook import WebhookEventPayload

#: Default replay-protection window, in seconds (Revolut uses 5 minutes).
DEFAULT_TOLERANCE_SECONDS = 300


def compute_signature(*, timestamp: str, raw_body: str, signing_secret: str) -> str:
    """Return the expected ``v1=<hex>`` signature for a payload."""
    payload_to_sign = f"v1.{timestamp}.{raw_body}"
    digest = hmac.new(
        signing_secret.encode("utf-8"),
        payload_to_sign.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return f"v1={digest}"


def _as_text(raw_body: str | bytes) -> str:
    return raw_body.decode("utf-8") if isinstance(raw_body, bytes) else raw_body


def verify_signature(
    raw_body: str | bytes,
    *,
    signature_header: str,
    timestamp_header: str,
    signing_secret: str,
    tolerance_seconds: int = DEFAULT_TOLERANCE_SECONDS,
    now: float | None = None,
) -> WebhookEventPayload:
    """Verify a webhook delivery and return its parsed payload.

    Args:
        raw_body: The exact request body as received (do not re-serialize).
        signature_header: The ``Revolut-Signature`` header value.
        timestamp_header: The ``Revolut-Request-Timestamp`` header (Unix ms).
        signing_secret: The webhook's ``signing_secret`` (``wsk_...``).
        tolerance_seconds: Reject deliveries older than this (replay protection).
        now: Current time in epoch seconds; defaults to :func:`time.time`.

    Raises:
        SignatureVerificationError: If the timestamp is stale or no signature matches.
    """
    body_text = _as_text(raw_body)

    try:
        timestamp_ms = int(timestamp_header)
    except (TypeError, ValueError) as exc:
        raise SignatureVerificationError("Invalid timestamp header") from exc

    current = time.time() if now is None else now
    if abs(current - timestamp_ms / 1000.0) > tolerance_seconds:
        raise SignatureVerificationError("Timestamp outside the tolerance window")

    expected = compute_signature(
        timestamp=timestamp_header, raw_body=body_text, signing_secret=signing_secret
    )
    candidates = [part.strip() for part in signature_header.split(",") if part.strip()]
    if not any(hmac.compare_digest(expected, candidate) for candidate in candidates):
        raise SignatureVerificationError("No matching signature")

    return WebhookEventPayload.model_validate(json.loads(body_text))
