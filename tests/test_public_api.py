"""Guard the public API surface (frozen for 1.0).

Adding or removing a name here is intentional and must be paired with a
CHANGELOG entry and an appropriate SemVer bump.
"""

from __future__ import annotations

import revolut

EXPECTED_PUBLIC_API = {
    "APIConnectionError",
    "APIStatusError",
    "AsyncRevolutMerchantClient",
    "AuthenticationError",
    "BadRequestError",
    "CaptureMode",
    "Customer",
    "DEFAULT_API_VERSION",
    "Dispute",
    "Environment",
    "InvalidRequestError",
    "Location",
    "Money",
    "NotFoundError",
    "Order",
    "OrderList",
    "OrderState",
    "OrderType",
    "Payment",
    "PaymentMethod",
    "PaymentState",
    "Payout",
    "PermissionDeniedError",
    "RateLimitError",
    "Refund",
    "ReportRun",
    "RetryConfig",
    "RevolutError",
    "RevolutMerchantClient",
    "ServerError",
    "SignatureVerificationError",
    "Subscription",
    "Webhook",
    "WebhookEvent",
    "WebhookEventPayload",
    "__version__",
    "compute_signature",
    "verify_signature",
}


def test_public_api_is_frozen():
    assert set(revolut.__all__) == EXPECTED_PUBLIC_API


def test_every_exported_name_is_importable():
    for name in revolut.__all__:
        assert hasattr(revolut, name), f"missing export: {name}"


def test_client_exposes_all_resources():
    client = revolut.RevolutMerchantClient(secret_key="sk", environment="sandbox")
    for resource in (
        "orders",
        "payments",
        "refunds",
        "customers",
        "payment_methods",
        "subscriptions",
        "payouts",
        "disputes",
        "report_runs",
        "locations",
        "webhooks",
    ):
        assert hasattr(client, resource)
    client.close()
