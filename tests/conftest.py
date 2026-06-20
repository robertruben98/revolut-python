"""Shared test fixtures."""

from __future__ import annotations

import pytest

from revolut import AsyncRevolutMerchantClient, RevolutMerchantClient
from revolut.config import base_url_for

SANDBOX_URL = base_url_for("sandbox")
SECRET_KEY = "sk_test_secret"


@pytest.fixture
def client() -> RevolutMerchantClient:
    c = RevolutMerchantClient(secret_key=SECRET_KEY, environment="sandbox")
    yield c
    c.close()


@pytest.fixture
async def async_client() -> AsyncRevolutMerchantClient:
    c = AsyncRevolutMerchantClient(secret_key=SECRET_KEY, environment="sandbox")
    yield c
    await c.aclose()
