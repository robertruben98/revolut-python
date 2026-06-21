# revolut-merchant-py

A typed Python client for the [Revolut Merchant API](https://developer.revolut.com/docs/merchant/merchant-api)
— online payments (orders, payments, refunds, customers, saved methods,
subscriptions, payouts, disputes, report runs, locations) and webhooks — with
both **synchronous** and **asynchronous** clients.

## Install

```bash
pip install revolut-merchant-py
```

The distribution is `revolut-merchant-py`; the import package is `revolut`.

## Quick start

```python
from revolut import RevolutMerchantClient

with RevolutMerchantClient(secret_key="sk_...", environment="sandbox") as client:
    order = client.orders.create(amount=1000, currency="GBP")  # 1000 = £10.00
    print(order.id, order.state, order.public_token)
```

See [Usage](usage.md) for the full guide and [API reference](api.md) for every
type.
