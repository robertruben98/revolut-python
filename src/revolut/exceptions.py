"""Exception hierarchy for the Revolut Merchant API client."""

from __future__ import annotations

from typing import Any


class RevolutError(Exception):
    """Base class for every error raised by this library."""


class APIConnectionError(RevolutError):
    """Raised when the request could not reach the API (network/timeout)."""


class SignatureVerificationError(RevolutError):
    """Raised when a webhook signature fails verification."""


class APIStatusError(RevolutError):
    """Raised when the API returns a non-2xx HTTP status.

    Attributes:
        status_code: The HTTP status code.
        code: The Revolut error ``code`` from the response body, if any.
        request_id: The Revolut request id (from the ``X-Request-Id`` header).
        body: The parsed JSON body, if any.
    """

    def __init__(
        self,
        message: str,
        *,
        status_code: int,
        code: str | None = None,
        request_id: str | None = None,
        body: Any | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.code = code
        self.request_id = request_id
        self.body = body


class BadRequestError(APIStatusError):
    """HTTP 400."""


class AuthenticationError(APIStatusError):
    """HTTP 401 — missing or invalid API key."""


class PermissionDeniedError(APIStatusError):
    """HTTP 403."""


class NotFoundError(APIStatusError):
    """HTTP 404."""


class InvalidRequestError(APIStatusError):
    """HTTP 422 — the operation is not valid for the resource's current state."""


class RateLimitError(APIStatusError):
    """HTTP 429 — too many requests.

    Attributes:
        retry_after: Seconds to wait, parsed from the ``Retry-After`` header.
    """

    def __init__(
        self,
        message: str,
        *,
        status_code: int,
        retry_after: float | None = None,
        code: str | None = None,
        request_id: str | None = None,
        body: Any | None = None,
    ) -> None:
        super().__init__(
            message,
            status_code=status_code,
            code=code,
            request_id=request_id,
            body=body,
        )
        self.retry_after = retry_after


class ServerError(APIStatusError):
    """HTTP 5xx."""


_STATUS_MAP: dict[int, type[APIStatusError]] = {
    400: BadRequestError,
    401: AuthenticationError,
    403: PermissionDeniedError,
    404: NotFoundError,
    422: InvalidRequestError,
    429: RateLimitError,
}


def exception_for_status(status_code: int) -> type[APIStatusError]:
    """Return the most specific :class:`APIStatusError` subclass for a status."""
    if status_code in _STATUS_MAP:
        return _STATUS_MAP[status_code]
    if status_code >= 500:
        return ServerError
    return APIStatusError
