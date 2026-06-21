# Roadmap — revolut-merchant-py

A typed Python client for the **Revolut Merchant API** with both synchronous and
asynchronous clients. Versioning follows [SemVer](https://semver.org/).

## v0.1.0 — Foundations (current)

- [x] Project scaffolding: `src` layout, `hatchling` packaging, MIT license
- [x] Tooling: `ruff` (lint + format), `mypy --strict`, `pytest` + `respx`
- [x] CI matrix (Python 3.10–3.13) via GitHub Actions
- [ ] Config + constants (base URLs, API version header)
- [ ] Exception hierarchy mapped from HTTP status codes
- [ ] Core HTTP layer (sync `httpx.Client` + async `httpx.AsyncClient`)
- [ ] Auth via secret API key (Bearer) + idempotency keys

## v0.2.0 — Orders & Payments

- [ ] Pydantic models: `Money`, enums, `Order`, `Payment`, `Refund`, `Customer`
- [ ] `orders` resource: create, retrieve, list, update, capture, cancel
- [ ] `payments` resource: retrieve, list
- [ ] `refunds` resource: create refund
- [ ] Pagination helpers

## v0.3.0 — Customers & Webhooks

- [ ] `customers` resource: create, retrieve, list, update
- [ ] `webhooks` resource: create, list, rotate secret, delete
- [ ] Webhook signature verification (HMAC-SHA256, timestamp tolerance)
- [ ] Typed webhook event payloads

## v0.4.0 — Polish & Docs

- [ ] Full README usage guide (sync + async, webhooks)
- [ ] Auto-retry with backoff for 429 / 5xx
- [ ] 100% of public API type-annotated; `mypy --strict` clean
- [ ] Test coverage ≥ 90%

## Future

- [x] Packaging ready for PyPI as `revolut-merchant-py`; release workflow via Trusted Publishing
- [ ] First PyPI release (`v0.1.0` tag) after sandbox verification
- [ ] Optional: Business API module
- [ ] Sphinx / mkdocs documentation site
