# Design — revolut-python (Revolut Merchant API client)

Date: 2026-06-20
Status: approved (autonomous goal execution)

## Goal

A typed, well-tested Python client for the **Revolut Merchant API** (online
payments) exposing both a **synchronous** and an **asynchronous** client, with
parity between them. Public GitHub repo, issue-driven roadmap, tests before any
merge to `main`.

## Decisions

- **Scope:** Merchant API only (orders, payments, refunds, customers, webhooks).
- **HTTP clients:** both sync (`httpx.Client`) and async (`httpx.AsyncClient`).
- **Models:** Pydantic v2. Money handled as integer minor units.
- **Repo:** `github.com/robertruben98/revolut-merchant-py`, public, default branch `main`.
- **Workflow:** feature branch → PR → CI green → merge to `main`.

## Architecture

Layered, single-responsibility modules under `src/revolut/`:

```
revolut/
  __init__.py          # public exports: clients, errors, models
  py.typed             # PEP 561 typing marker
  config.py            # Environment enum, base URLs, API version constant
  exceptions.py        # RevolutError hierarchy
  _http/
    base.py            # RequestSpec, response/error handling shared by both clients
    sync_client.py     # Transport wrapping httpx.Client
    async_client.py    # Transport wrapping httpx.AsyncClient
  models/
    common.py          # enums (OrderState, CaptureMode, ...), Money, pagination
    order.py           # Order, OrderLineItem, ...
    payment.py         # Payment
    refund.py          # Refund
    customer.py        # Customer
    webhook.py         # Webhook endpoint config + event payloads
  resources/
    base.py            # SyncResource / AsyncResource base bound to a transport
    orders.py          # OrdersResource / AsyncOrdersResource
    payments.py
    refunds.py
    customers.py
    webhooks.py
  webhooks_verify.py   # verify_signature() — HMAC-SHA256 over v1.{ts}.{body}
  client.py            # RevolutMerchantClient / AsyncRevolutMerchantClient facades
```

### Boundaries

- **config**: pure data. No I/O. Maps `Environment` → base URL; holds the API
  version date string sent as a header.
- **exceptions**: pure. `RevolutError(message, *, status_code, code, request_id,
  response)` base; subclasses `AuthenticationError`, `PermissionDeniedError`,
  `NotFoundError`, `InvalidRequestError`, `RateLimitError`, `APIStatusError`.
  A `from_response(httpx.Response)` factory maps status → class.
- **_http.base**: builds headers (auth Bearer, `Accept`, `Content-Type`,
  api-version, optional idempotency key), serializes JSON, and converts a raw
  `httpx.Response` into either parsed JSON or a raised exception. No knowledge of
  resources. Both transports share this logic; only the actual `send` differs
  (sync vs async), keeping behavior identical.
- **models**: Pydantic models, no I/O. `Money` is `(amount: int, currency: str)`
  with `from_major()`/`to_major()` helpers; the wire format is integer minor units.
- **resources**: thin typed wrappers translating method calls into `RequestSpec`
  objects, delegating to a transport, and parsing responses into models. Sync and
  async variants share request-building helpers, differing only in `await`.
- **client.py**: user-facing facade. Constructs a transport and attaches resource
  objects (`client.orders`, `client.payments`, ...). Supports context-manager use
  and explicit `close()`/`aclose()`.

### Data flow (create order, sync)

```
client.orders.create(amount=1000, currency="GBP")
  -> OrdersResource builds RequestSpec(POST, "/orders", json={...})
  -> SyncTransport.request(spec): add headers, httpx.Client.send
  -> base.handle_response: 2xx -> dict ; else -> raise RevolutError subclass
  -> OrdersResource parses dict -> Order model -> returned to caller
```

Async path is identical except `await transport.request(...)`.

### Error handling

- Non-2xx responses raise the mapped `RevolutError` subclass carrying status code,
  Revolut error code/message (parsed from body when present) and the request id.
- Network/timeout errors from httpx are wrapped in `APIConnectionError`.
- `RateLimitError` exposes `retry_after` when the header is present.

### Webhooks

- `verify_signature(raw_body: bytes, *, signature_header, timestamp_header,
  signing_secret, tolerance_seconds=300, now=None)`:
  - Reconstruct the signed payload `v1.{timestamp}.{raw_body}`.
  - Compute HMAC-SHA256 with the signing secret, hex-encode.
  - Constant-time compare (`hmac.compare_digest`) against the provided signature
    (which may contain multiple space/comma-separated `v1=...` values).
  - Reject if `|now - timestamp| > tolerance_seconds` (replay protection).
  - Raise `SignatureVerificationError` on failure; return parsed event on success.

> Exact header names, base URLs, API-version string, endpoint paths, object
> fields and webhook event names are taken from the Revolut developer docs
> research captured during implementation and pinned in `config.py` + models.

### Testing strategy

- `respx` mocks `httpx` at the transport layer; every resource method has a test
  asserting method, path, headers (auth + api-version), request body and parsed
  response, for **both** sync and async clients.
- Webhook verification: positive, tampered-body, wrong-secret, and expired-
  timestamp cases.
- `mypy --strict` and `ruff` gate in CI across Python 3.9–3.13.

## API reference (pinned from Revolut developer docs, June 2026)

- Base URLs: production `https://merchant.revolut.com`, sandbox
  `https://sandbox-merchant.revolut.com`. API under `/api`.
- Auth: `Authorization: Bearer <secret_key>` (keys prefixed `sk_`).
- Version header: `Revolut-Api-Version: 2026-04-20` (latest; webhooks need ≥ `2024-09-01`).
- Idempotency: optional `Idempotency-Key` header (recommended for refunds).
- Amounts: integers in ISO-4217 minor units.
- Orders: `POST /api/orders`, `GET /api/orders`, `GET /api/orders/{id}`,
  `PATCH /api/orders/{id}`, `POST /api/orders/{id}/capture`, `.../cancel`,
  `.../refund`, `.../payments` (pay + list), `.../increment-authorisation`.
- Customers: `POST/GET /api/customers`, `GET/PATCH/DELETE /api/customers/{id}`,
  plus customer payment methods.
- Webhooks: `POST/GET /api/1.0/webhooks` (create/list), `GET/PATCH/DELETE
  /api/1.0/webhooks/{id}`, `POST /api/1.0/webhooks/{id}/rotate-signing-secret`.
  (Path family confirmed as `/api/1.0/webhooks` in docs examples.)
- Order `state`: `pending, processing, authorised, completed, cancelled, failed`.
- Order `type`: `payment, payment_request, refund, chargeback,
  chargeback_reversal, credit_reimbursement`.
- `capture_mode`: `automatic | manual`. `authorisation_type`: `final |
  pre_authorisation`.
- Create-order response exposes `token` (public id) — **not** `checkout_url`.
  Models allow unknown fields for forward-compat and tolerate legacy `public_id`.
- Webhook signature: `v1.{timestamp}.{raw_body}`, HMAC-SHA256 hex, header
  `Revolut-Signature: v1=<hex>` (may be comma-separated during rotation);
  timestamp header `Revolut-Request-Timestamp` (unix ms); 5-min tolerance.
  Test vector: secret `wsk_r59a4HfWVAKycbCaNO1RvgCJec02gRd8`, ts `1683650202360`
  → `v1=bca326fb378d0da7f7c490ad584a8106bab9723d8d9cdd0d50b4c5b3be3837c0`.
- Error body: `{"code": str, "message": str, "timestamp": int}`.

> Path strings are high-confidence (doc examples) but not byte-verified against a
> live sandbox; resources centralize paths so they are trivially adjustable.

## Non-goals (YAGNI for v0.x)

- Business API and Open Banking modules.
- A CLI.
- Persistent storage / caching beyond in-process.
