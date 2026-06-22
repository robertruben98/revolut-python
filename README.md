# revolut-merchant-py

[![CI](https://github.com/robertruben98/revolut-merchant-py/actions/workflows/ci.yml/badge.svg)](https://github.com/robertruben98/revolut-merchant-py/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/revolut-merchant-py)](https://pypi.org/project/revolut-merchant-py/)
[![Docs](https://img.shields.io/badge/docs-online-blue)](https://robertruben98.github.io/revolut-merchant-py/)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

A typed Python client for the [Revolut Merchant API](https://developer.revolut.com/docs/merchant/merchant-api)
— online payments (orders, payments, refunds, customers) and webhooks — with
**both synchronous and asynchronous** clients.

> Status: early development (v0.1.0). See the [ROADMAP](ROADMAP.md).

## Features

- Sync (`RevolutMerchantClient`) and async (`AsyncRevolutMerchantClient`) clients
- Typed request/response models (Pydantic v2)
- Amounts handled safely in **minor units** (integers)
- Sandbox and production environments
- Webhook signature verification (HMAC-SHA256)
- `mypy --strict` clean, fully type-annotated

## Installation

```bash
pip install revolut-merchant-py
```

The distribution is published as **`revolut-merchant-py`**; the import package is
**`revolut`**:

```python
import revolut
```

Latest from source:

```bash
pip install git+https://github.com/robertruben98/revolut-merchant-py.git
```

## Quick start

```python
from revolut import RevolutMerchantClient

with RevolutMerchantClient(secret_key="sk_...", environment="sandbox") as client:
    order = client.orders.create(amount=1000, currency="GBP")  # 1000 = £10.00
    # `token` is the public id used by the Web SDK / hosted checkout page.
    print(order.id, order.state, order.public_token)
```

Async — the same API, awaited:

```python
import asyncio
from revolut import AsyncRevolutMerchantClient

async def main():
    async with AsyncRevolutMerchantClient(secret_key="sk_...") as client:
        order = await client.orders.create(amount=1000, currency="GBP")
        print(order.id)

asyncio.run(main())
```

## Working with money

Amounts are **integers in minor units** (e.g. `1099` = £10.99). The `Money`
helper converts to/from major units, accounting for zero- and three-decimal
currencies:

```python
from revolut import Money

Money.from_major("10.99", "GBP").amount   # 1099
Money.from_major("1000", "JPY").amount    # 1000  (JPY has no minor unit)
Money(1234, "BHD").to_major()             # Decimal("1.234")
```

## Orders

```python
order = client.orders.create(
    amount=5000, currency="EUR",
    capture_mode="manual",                      # authorise now, capture later
    merchant_order_data={"reference": "INV-42"},
    idempotency_key="INV-42",                   # safe to retry
)
client.orders.capture(order.id, amount=5000)    # capture authorised funds
client.orders.cancel(order.id)                  # or cancel before capture
client.orders.list(limit=50, state="completed") # paginated listing
```

## Refunds

```python
# Refunds create a new order of type "refund" linked to the original.
refund = client.refunds.create(order.id, amount=2500, idempotency_key="INV-42-r1")
assert refund.type == "refund"
```

## Pagination

List endpoints accept paging params, or use `iter()` to stream across all pages
transparently (sync yields, async is an async iterator):

```python
for order in client.orders.iter(state="completed", limit=100):
    ...

for customer in client.customers.iter(max_items=500):
    ...

# async
async for order in async_client.orders.iter():
    ...
```

## Saved payment methods

Tokenized methods live under a customer; charge one via `payments.pay`:

```python
methods = client.payment_methods.list(customer_id, only_merchant=True)
client.payment_methods.retrieve(customer_id, methods[0].id)
client.payment_methods.delete(customer_id, methods[0].id)

# charge a saved method against an existing order
client.payments.pay(order.id, payment_method_id=methods[0].id)
```

## Webhooks

Verify the authenticity of incoming webhook deliveries (HMAC-SHA256, replay
protected). Pass the **raw** request body — do not re-serialize it:

```python
from revolut import verify_signature, SignatureVerificationError

try:
    event = verify_signature(
        raw_body=request.body,                                  # bytes or str
        signature_header=request.headers["Revolut-Signature"],
        timestamp_header=request.headers["Revolut-Request-Timestamp"],
        signing_secret="wsk_...",                               # from webhook creation
    )
    print(event.event, event.order_id)
except SignatureVerificationError:
    ...  # reject the request (401)
```

Manage webhook endpoints via the API:

```python
wh = client.webhooks.create(url="https://example.com/cb", events=["ORDER_COMPLETED"])
print(wh.signing_secret)  # store this to verify future deliveries
```

## More resources

The client also exposes `subscriptions`, `payouts` and `locations`, each with the
same sync/async parity:

```python
client.subscriptions.list()
client.payouts.retrieve("po_...")
client.locations.create(name="Web", type="online")
```

## Error handling

Non-2xx responses raise a typed subclass of `RevolutError`:

```python
from revolut import NotFoundError, RateLimitError, RevolutError

try:
    client.orders.retrieve("missing")
except NotFoundError as exc:
    print(exc.status_code, exc.code, exc.message)
except RateLimitError as exc:
    print("retry after", exc.retry_after)
except RevolutError:
    ...  # base class for everything this library raises
```

Transient failures (`429`, `5xx`) are retried automatically with exponential
backoff; tune via `RetryConfig` (including optional `jitter`). Enable request
tracing with the `revolut` logger:

```python
import logging
logging.getLogger("revolut").setLevel(logging.DEBUG)

from revolut import RetryConfig
client = RevolutMerchantClient(secret_key="sk_...", retry=RetryConfig(max_retries=4, jitter=0.3))
```

## Stability and versioning

This project follows [SemVer](https://semver.org/). From **1.0.0** the public API
is the set of names exported from the top-level `revolut` package (i.e.
`revolut.__all__`) plus the documented resource attributes on the clients.

- **Patch** (`1.0.x`): bug fixes, no API changes.
- **Minor** (`1.x.0`): backwards-compatible additions (new resources, fields,
  optional arguments).
- **Major** (`x.0.0`): backwards-incompatible changes.

Anything under a leading underscore (e.g. `revolut._http`) is internal and may
change at any time. Deprecations are announced in the [CHANGELOG](CHANGELOG.md),
keep working for at least one minor release, and emit `DeprecationWarning` before
removal.

## Development

```bash
pip install -e ".[dev]"
ruff check . && ruff format --check .
mypy
pytest                       # hermetic unit tests (mocked HTTP)
```

Live sandbox integration tests are skipped unless a sandbox key is provided:

```bash
REVOLUT_SECRET_KEY=sk_... pytest tests/integration -v
```

## License

[MIT](LICENSE)

[MIT](LICENSE)
