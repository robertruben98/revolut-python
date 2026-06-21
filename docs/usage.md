# Usage

## Money

Amounts are integers in minor units (e.g. `1099` = £10.99).

```python
from revolut import Money

Money.from_major("10.99", "GBP").amount   # 1099
Money(1234, "BHD").to_major()             # Decimal("1.234")
```

## Orders

```python
order = client.orders.create(
    amount=5000, currency="EUR",
    capture_mode="manual",
    merchant_order_data={"reference": "INV-42"},
    idempotency_key="INV-42",
)
client.orders.capture(order.id, amount=5000)
client.orders.cancel(order.id)

for o in client.orders.iter(state="completed"):
    ...
```

## Refunds

```python
refund = client.refunds.create(order.id, amount=2500, idempotency_key="INV-42-r1")
```

## Customers & saved payment methods

```python
customer = client.customers.create(email="a@b.com")
methods = client.payment_methods.list(customer.id, only_merchant=True)
client.payments.pay(order.id, payment_method_id=methods[0].id)
```

## Webhooks

```python
from revolut import verify_signature, SignatureVerificationError

event = verify_signature(
    raw_body=request.body,
    signature_header=request.headers["Revolut-Signature"],
    timestamp_header=request.headers["Revolut-Request-Timestamp"],
    signing_secret="wsk_...",
)
```

## Async

Every resource has an async twin via `AsyncRevolutMerchantClient`:

```python
async with AsyncRevolutMerchantClient(secret_key="sk_...") as client:
    order = await client.orders.create(amount=1000, currency="GBP")
    async for o in client.orders.iter():
        ...
```

## Errors & retries

Non-2xx responses raise typed `RevolutError` subclasses. Transient `429`/`5xx`
are retried with exponential backoff; tune with `RetryConfig(max_retries=..., jitter=...)`.
