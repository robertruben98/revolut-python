# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and this project adheres
to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Auto-pagination helpers: `orders.iter()` (cursor) and `customers.iter()`
  (`page_token`), sync and async, with `max_items`.
- Saved payment methods resource (`client.payment_methods`): list, retrieve,
  update, delete; plus the `PaymentMethod` model.
- New resources (sync + async) with models: `subscriptions`, `payouts`,
  `disputes`, `report_runs`, `locations`.

## [0.1.0] - 2026-06-21

### Added
- Initial project scaffolding, tooling and CI.
- Revolut Merchant API client (sync + async): config, exceptions, HTTP layer,
  models, resources (orders, payments, refunds, customers, webhooks) and
  webhook signature verification.
- Published to PyPI as `revolut-merchant-py` (import package: `revolut`).
