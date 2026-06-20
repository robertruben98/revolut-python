"""Shared model primitives: base model, enums and money helpers."""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal
from enum import Enum

from pydantic import BaseModel, ConfigDict


class RevolutModel(BaseModel):
    """Base for all API models.

    ``extra="allow"`` keeps fields the API adds in future versions accessible
    instead of dropping them, so the client degrades gracefully.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)


class OrderState(str, Enum):
    """Lifecycle states of an order."""

    PENDING = "pending"
    PROCESSING = "processing"
    AUTHORISED = "authorised"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"


class OrderType(str, Enum):
    """The kind of order."""

    PAYMENT = "payment"
    PAYMENT_REQUEST = "payment_request"
    REFUND = "refund"
    CHARGEBACK = "chargeback"
    CHARGEBACK_REVERSAL = "chargeback_reversal"
    CREDIT_REIMBURSEMENT = "credit_reimbursement"


class CaptureMode(str, Enum):
    """Whether funds are captured automatically or manually."""

    AUTOMATIC = "automatic"
    MANUAL = "manual"


class PaymentState(str, Enum):
    """Fine-grained states of a payment sub-object."""

    PENDING = "pending"
    AUTHENTICATION_CHALLENGE = "authentication_challenge"
    AUTHENTICATION_VERIFIED = "authentication_verified"
    AUTHORISATION_STARTED = "authorisation_started"
    AUTHORISATION_PASSED = "authorisation_passed"
    AUTHORISED = "authorised"
    CAPTURE_STARTED = "capture_started"
    CAPTURED = "captured"
    REFUND_VALIDATED = "refund_validated"
    REFUND_STARTED = "refund_started"
    CANCELLATION_STARTED = "cancellation_started"
    DECLINING = "declining"
    COMPLETING = "completing"
    CANCELLING = "cancelling"
    FAILING = "failing"
    COMPLETED = "completed"
    DECLINED = "declined"
    SOFT_DECLINED = "soft_declined"
    CANCELLED = "cancelled"
    FAILED = "failed"


# Number of minor units per major unit for currencies that do not use 2 decimals.
_MINOR_UNIT_EXPONENT: dict[str, int] = {
    "JPY": 0,
    "KRW": 0,
    "CLP": 0,
    "ISK": 0,
    "VND": 0,
    "BHD": 3,
    "KWD": 3,
    "OMR": 3,
    "TND": 3,
}


class Money:
    """Convenience helper to convert between major and minor currency units.

    The Revolut API always works with integer minor units (e.g. ``1099`` for
    £10.99). These helpers make conversions explicit and currency-aware.
    """

    def __init__(self, amount: int, currency: str) -> None:
        self.amount = amount
        self.currency = currency.upper()

    @staticmethod
    def _exponent(currency: str) -> int:
        return _MINOR_UNIT_EXPONENT.get(currency.upper(), 2)

    @classmethod
    def from_major(cls, value: str | int | float | Decimal, currency: str) -> Money:
        """Build from a major-unit value, e.g. ``Money.from_major("10.99", "GBP")``."""
        exponent = cls._exponent(currency)
        quantum = Decimal(1).scaleb(-exponent)
        minor = (Decimal(str(value)) / quantum).quantize(Decimal(1), rounding=ROUND_HALF_UP)
        return cls(int(minor), currency)

    def to_major(self) -> Decimal:
        """Return the major-unit value as a :class:`~decimal.Decimal`."""
        exponent = self._exponent(self.currency)
        return Decimal(self.amount).scaleb(-exponent)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        return self.amount == other.amount and self.currency == other.currency

    def __repr__(self) -> str:
        return f"Money(amount={self.amount}, currency={self.currency!r})"
