"""Resource classes for each Merchant API object group."""

from .customers import AsyncCustomersResource, CustomersResource
from .orders import AsyncOrdersResource, OrdersResource
from .payments import AsyncPaymentsResource, PaymentsResource
from .refunds import AsyncRefundsResource, RefundsResource
from .webhooks import AsyncWebhooksResource, WebhooksResource

__all__ = [
    "AsyncCustomersResource",
    "AsyncOrdersResource",
    "AsyncPaymentsResource",
    "AsyncRefundsResource",
    "AsyncWebhooksResource",
    "CustomersResource",
    "OrdersResource",
    "PaymentsResource",
    "RefundsResource",
    "WebhooksResource",
]
