"""
Stock mutation logic for the inventory app.

adjust_stock() is the ONLY function anything in this codebase is allowed to
use to change how much stock is on hand. Sales, purchase receipts, damage
write-offs, manual corrections, transfers — all of them call this, never
StockLevel.objects.update() or similar. That's what keeps StockLedger a
trustworthy, complete audit trail: every change to StockLevel.quantity has
exactly one corresponding StockLedger row explaining why it happened.
"""
from django.db import transaction

from .models import StockLedger, StockLevel


class InsufficientStockError(Exception):
    """Raised when a stock decrease would take quantity on hand below zero."""

    def __init__(self, item, outlet, current_quantity, requested_change):
        self.item = item
        self.outlet = outlet
        self.current_quantity = current_quantity
        self.requested_change = requested_change
        super().__init__(
            f'Cannot apply change of {requested_change} to {item.sku} at {outlet.name}: '
            f'only {current_quantity} on hand.'
        )


@transaction.atomic
def adjust_stock(item, outlet, change_qty, reason, reference='', user=None):
    """
    Apply a stock change for one item at one outlet, atomically.

    - `change_qty` is signed: positive for stock coming in (a purchase
      receipt, a transfer in), negative for stock going out (a sale, a
      transfer out, damage). It must be a non-zero integer, in base units.
    - `reason` must be one of StockLedger.Reason's values.
    - Raises InsufficientStockError, and makes no change at all, if the
      result would go below zero.
    - Returns the updated StockLevel.

    The row is locked with select_for_update() so two concurrent calls for
    the same (item, outlet) — e.g. two tills selling the last unit at the
    same instant — can't both read the same starting balance and push
    stock negative.
    """
    if change_qty == 0:
        raise ValueError('change_qty must not be zero.')

    stock_level, _ = StockLevel.objects.select_for_update().get_or_create(
        item=item, outlet=outlet, defaults={'quantity': 0},
    )

    new_balance = stock_level.quantity + change_qty
    if new_balance < 0:
        raise InsufficientStockError(item, outlet, stock_level.quantity, change_qty)

    stock_level.quantity = new_balance
    stock_level.save(update_fields=['quantity', 'updated_at'])

    StockLedger.objects.create(
        item=item,
        outlet=outlet,
        change_qty=change_qty,
        balance_after=new_balance,
        reason=reason,
        reference=reference,
        created_by=user,
    )

    return stock_level
