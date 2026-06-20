"""Webhook models: endpoint configuration and delivered event payloads."""

from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import Field

from .common import RevolutModel


class WebhookEvent(str, Enum):
    """Event types a webhook can subscribe to / be delivered."""

    ORDER_COMPLETED = "ORDER_COMPLETED"
    ORDER_AUTHORISED = "ORDER_AUTHORISED"
    ORDER_CANCELLED = "ORDER_CANCELLED"
    ORDER_FAILED = "ORDER_FAILED"
    ORDER_INCREMENTAL_AUTHORISATION_AUTHORISED = "ORDER_INCREMENTAL_AUTHORISATION_AUTHORISED"
    ORDER_INCREMENTAL_AUTHORISATION_DECLINED = "ORDER_INCREMENTAL_AUTHORISATION_DECLINED"
    ORDER_INCREMENTAL_AUTHORISATION_FAILED = "ORDER_INCREMENTAL_AUTHORISATION_FAILED"
    ORDER_PAYMENT_AUTHENTICATION_CHALLENGED = "ORDER_PAYMENT_AUTHENTICATION_CHALLENGED"
    ORDER_PAYMENT_AUTHENTICATED = "ORDER_PAYMENT_AUTHENTICATED"
    ORDER_PAYMENT_DECLINED = "ORDER_PAYMENT_DECLINED"
    ORDER_PAYMENT_FAILED = "ORDER_PAYMENT_FAILED"
    SUBSCRIPTION_INITIATED = "SUBSCRIPTION_INITIATED"
    SUBSCRIPTION_FINISHED = "SUBSCRIPTION_FINISHED"
    SUBSCRIPTION_CANCELLED = "SUBSCRIPTION_CANCELLED"
    SUBSCRIPTION_OVERDUE = "SUBSCRIPTION_OVERDUE"
    PAYOUT_INITIATED = "PAYOUT_INITIATED"
    PAYOUT_COMPLETED = "PAYOUT_COMPLETED"
    PAYOUT_FAILED = "PAYOUT_FAILED"
    DISPUTE_ACTION_REQUIRED = "DISPUTE_ACTION_REQUIRED"
    DISPUTE_UNDER_REVIEW = "DISPUTE_UNDER_REVIEW"
    DISPUTE_WON = "DISPUTE_WON"
    DISPUTE_LOST = "DISPUTE_LOST"


class Webhook(RevolutModel):
    """A configured webhook endpoint.

    ``signing_secret`` (prefixed ``wsk_``) is returned only on creation and on
    secret rotation; keep it to verify delivered payloads.
    """

    id: str | None = None
    url: str | None = None
    events: list[str] = Field(default_factory=list)
    signing_secret: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class WebhookEventPayload(RevolutModel):
    """The JSON body Revolut POSTs to your webhook URL."""

    event: str | None = None
    order_id: str | None = None
    merchant_order_ext_ref: str | None = None
    incremental_authorisation_ext_reference: str | None = None
    timestamp: str | None = None
