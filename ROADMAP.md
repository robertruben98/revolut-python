# Roadmap — revolut-merchant-py

A typed Python client for the **Revolut Merchant API** with both synchronous and
asynchronous clients. Versioning follows [SemVer](https://semver.org/).

> Current published version: **0.1.0a2** (alpha) on
> [PyPI](https://pypi.org/project/revolut-merchant-py/). Auto-publish via PyPI
> Trusted Publishing on `v*` tags.

## v0.1.0 — Foundations ✅ (shipped)

- [x] Project scaffolding: `src` layout, `hatchling` packaging, MIT license
- [x] Tooling: `ruff` (lint + format), `mypy --strict`, `pytest` + `respx`
- [x] CI matrix (Python 3.10–3.13) via GitHub Actions
- [x] Config + constants (base URLs, API version header)
- [x] Exception hierarchy mapped from HTTP status codes
- [x] Core HTTP layer (sync `httpx.Client` + async `httpx.AsyncClient`)
- [x] Auth via secret API key (Bearer) + idempotency keys

## v0.2.0 — Orders & Payments ✅ (shipped)

- [x] Pydantic models: `Money`, enums, `Order`, `Payment`, `Refund`, `Customer`
- [x] `orders` resource: create, retrieve, list, update, capture, cancel
- [x] `payments` resource: retrieve, list, pay (saved method)
- [x] `refunds` resource: create refund
- [ ] Pagination helpers (auto-iterating list endpoints) — moved to v0.5.0

## v0.3.0 — Customers & Webhooks ✅ (shipped)

- [x] `customers` resource: create, retrieve, list, update, delete
- [x] `webhooks` resource: create, list, retrieve, update, rotate secret, delete
- [x] Webhook signature verification (HMAC-SHA256, timestamp tolerance)
- [x] Typed webhook event payloads

## v0.4.0 — Polish & Docs ✅ (shipped)

- [x] Full README usage guide (sync + async, webhooks)
- [x] Auto-retry with backoff for 429 / 5xx
- [x] 100% of public API type-annotated; `mypy --strict` clean
- [x] Test coverage ≥ 90% (currently 98%)
- [x] Packaging + PyPI release pipeline (Trusted Publishing, OIDC)

## v0.5.0 — Pagination, saved methods & live verification

- [ ] Auto-pagination helpers: `iter()` over list endpoints (cursor / `page_token`)
- [ ] Saved payment methods / tokenization CRUD (list / retrieve / update / delete)
- [ ] Live sandbox integration tests: order → capture → refund → webhook delivery
- [ ] Verify endpoint path strings against a real sandbox (resolve the docs caveat)

## v0.6.0 — Remaining resources & docs site

- [ ] `subscriptions` resource (or explicit out-of-scope decision)
- [ ] `payouts` resource
- [ ] `disputes` resource
- [ ] `report runs` and `locations` resources
- [ ] Documentation site (mkdocs or Sphinx) published from CI

## v1.0.0 — Stable API

- [ ] Public API frozen; no breaking changes expected
- [ ] Documented deprecation policy and SemVer commitment
- [ ] All in-scope Merchant API resources covered (or scope documented)
- [ ] Green live-sandbox integration suite gating the release
- [ ] Hardening: logging hooks, per-request timeout override, backoff jitter

## Future / maybe

- [ ] Optional: Business API module
- [ ] Optional: Open Banking module
