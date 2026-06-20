# revolut-python

[![CI](https://github.com/robertruben98/revolut-python/actions/workflows/ci.yml/badge.svg)](https://github.com/robertruben98/revolut-python/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/)
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
pip install git+https://github.com/robertruben98/revolut-python.git
```

(A PyPI release will follow — see the roadmap.)

## Quick start

```python
from revolut import RevolutMerchantClient

client = RevolutMerchantClient(secret_key="sk_...", environment="sandbox")

order = client.orders.create(amount=1000, currency="GBP")  # 1000 = £10.00
print(order.id, order.state, order.checkout_url)
```

Async:

```python
import asyncio
from revolut import AsyncRevolutMerchantClient

async def main():
    async with AsyncRevolutMerchantClient(secret_key="sk_...", environment="sandbox") as client:
        order = await client.orders.create(amount=1000, currency="GBP")
        print(order.id)

asyncio.run(main())
```

## Development

```bash
pip install -e ".[dev]"
ruff check . && ruff format --check .
mypy
pytest
```

## License

[MIT](LICENSE)
