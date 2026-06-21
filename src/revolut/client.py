"""User-facing client facades for the Revolut Merchant API."""

from __future__ import annotations

import httpx

from ._http.async_client import AsyncTransport
from ._http.base import RetryConfig
from ._http.sync_client import SyncTransport
from .config import DEFAULT_API_VERSION, DEFAULT_TIMEOUT, Environment
from .resources import (
    AsyncCustomersResource,
    AsyncDisputesResource,
    AsyncLocationsResource,
    AsyncOrdersResource,
    AsyncPaymentMethodsResource,
    AsyncPaymentsResource,
    AsyncPayoutsResource,
    AsyncRefundsResource,
    AsyncReportRunsResource,
    AsyncSubscriptionsResource,
    AsyncWebhooksResource,
    CustomersResource,
    DisputesResource,
    LocationsResource,
    OrdersResource,
    PaymentMethodsResource,
    PaymentsResource,
    PayoutsResource,
    RefundsResource,
    ReportRunsResource,
    SubscriptionsResource,
    WebhooksResource,
)


class RevolutMerchantClient:
    """Synchronous Revolut Merchant API client.

    Example:
        >>> client = RevolutMerchantClient(secret_key="sk_...", environment="sandbox")
        >>> order = client.orders.create(amount=1000, currency="GBP")
    """

    def __init__(
        self,
        secret_key: str,
        *,
        environment: Environment | str = Environment.SANDBOX,
        api_version: str = DEFAULT_API_VERSION,
        timeout: float = DEFAULT_TIMEOUT,
        retry: RetryConfig | None = None,
        http_client: httpx.Client | None = None,
    ) -> None:
        self._transport = SyncTransport(
            secret_key=secret_key,
            environment=environment,
            api_version=api_version,
            timeout=timeout,
            retry=retry,
            http_client=http_client,
        )
        self.orders = OrdersResource(self._transport)
        self.payments = PaymentsResource(self._transport)
        self.refunds = RefundsResource(self._transport)
        self.customers = CustomersResource(self._transport)
        self.payment_methods = PaymentMethodsResource(self._transport)
        self.subscriptions = SubscriptionsResource(self._transport)
        self.payouts = PayoutsResource(self._transport)
        self.disputes = DisputesResource(self._transport)
        self.report_runs = ReportRunsResource(self._transport)
        self.locations = LocationsResource(self._transport)
        self.webhooks = WebhooksResource(self._transport)

    def close(self) -> None:
        self._transport.close()

    def __enter__(self) -> RevolutMerchantClient:
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()


class AsyncRevolutMerchantClient:
    """Asynchronous Revolut Merchant API client.

    Example:
        >>> async with AsyncRevolutMerchantClient(secret_key="sk_...") as client:
        ...     order = await client.orders.create(amount=1000, currency="GBP")
    """

    def __init__(
        self,
        secret_key: str,
        *,
        environment: Environment | str = Environment.SANDBOX,
        api_version: str = DEFAULT_API_VERSION,
        timeout: float = DEFAULT_TIMEOUT,
        retry: RetryConfig | None = None,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self._transport = AsyncTransport(
            secret_key=secret_key,
            environment=environment,
            api_version=api_version,
            timeout=timeout,
            retry=retry,
            http_client=http_client,
        )
        self.orders = AsyncOrdersResource(self._transport)
        self.payments = AsyncPaymentsResource(self._transport)
        self.refunds = AsyncRefundsResource(self._transport)
        self.customers = AsyncCustomersResource(self._transport)
        self.payment_methods = AsyncPaymentMethodsResource(self._transport)
        self.subscriptions = AsyncSubscriptionsResource(self._transport)
        self.payouts = AsyncPayoutsResource(self._transport)
        self.disputes = AsyncDisputesResource(self._transport)
        self.report_runs = AsyncReportRunsResource(self._transport)
        self.locations = AsyncLocationsResource(self._transport)
        self.webhooks = AsyncWebhooksResource(self._transport)

    async def aclose(self) -> None:
        await self._transport.aclose()

    async def __aenter__(self) -> AsyncRevolutMerchantClient:
        return self

    async def __aexit__(self, *exc_info: object) -> None:
        await self.aclose()
