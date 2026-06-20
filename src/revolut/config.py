"""Configuration constants for the Revolut Merchant API client."""

from __future__ import annotations

from enum import Enum

#: Latest documented Revolut Merchant API version (sent as the
#: ``Revolut-Api-Version`` header). Webhook endpoints require ``>= 2024-09-01``.
DEFAULT_API_VERSION = "2026-04-20"

#: Default per-request timeout, in seconds.
DEFAULT_TIMEOUT = 30.0


class Environment(str, Enum):
    """Target Revolut environment."""

    SANDBOX = "sandbox"
    PRODUCTION = "production"


#: Base URLs per environment. The Merchant API lives under the ``/api`` prefix.
BASE_URLS: dict[Environment, str] = {
    Environment.SANDBOX: "https://sandbox-merchant.revolut.com",
    Environment.PRODUCTION: "https://merchant.revolut.com",
}


def base_url_for(environment: Environment | str) -> str:
    """Return the base URL for an environment (accepts the enum or its value)."""
    env = Environment(environment)
    return BASE_URLS[env]
