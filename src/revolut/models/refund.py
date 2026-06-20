"""Refund models.

In the Merchant API a refund is not a standalone resource: issuing a refund
(``POST /api/orders/{id}/refund``) creates a *new order* of ``type: refund``
linked to the original via ``related_order_id``. ``Refund`` is therefore an
alias of :class:`~revolut.models.order.Order` for readable call sites.
"""

from __future__ import annotations

from .order import Order

Refund = Order

__all__ = ["Refund"]
