from django.conf import settings
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name


class Item(models.Model):
    """
    The base sellable unit for a product (e.g. one bar of soap, one can of Coke).
    Bulk packaging (boxes, cartons, etc.) is described separately in
    PackagingLevel below — an item can have as many packaging levels as it
    needs, each with its own barcode, price, and purchase/sale flags.
    """

    class UnitOfMeasure(models.TextChoices):
        EACH = 'each', 'Each'
        KG = 'kg', 'Kilogram'
        G = 'g', 'Gram'
        LITRE = 'l', 'Litre'
        ML = 'ml', 'Millilitre'
        PACK = 'pack', 'Pack'
        BOX = 'box', 'Box'

    sku = models.CharField(max_length=50, unique=True)
    barcode = models.CharField(
        max_length=50, unique=True, blank=True, null=True,
        help_text='Barcode for a single base unit (e.g. one piece). Leave blank if it has none of its own.',
    )
    name = models.CharField(max_length=200)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='items',
    )
    unit_of_measure = models.CharField(
        max_length=10,
        choices=UnitOfMeasure.choices,
        default=UnitOfMeasure.EACH,
    )
    cost_price = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        help_text='Cost for one base unit (e.g. one piece).',
    )
    sell_price = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        help_text='Selling price for one base unit (e.g. one piece).',
    )
    reorder_level = models.PositiveIntegerField(
        default=0,
        help_text='Trigger a low-stock alert once quantity on hand (in base units) drops to this level.',
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def save(self, *args, **kwargs):
        # Normalize "" to None so multiple items can have no barcode without
        # violating the unique constraint (Postgres allows multiple NULLs,
        # but not multiple empty strings, in a unique column).
        if not self.barcode:
            self.barcode = None
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.sku} — {self.name}'


class PackagingLevel(models.Model):
    """
    One extra way this item is bought or sold in bulk — e.g. "Box of 5" or
    "Carton (25 pcs)". quantity_in_base_units always counts back to the
    item's own base unit (not the level above it), so nothing compounds or
    drifts if a middle level is ever edited later.
    """

    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='packaging_levels')
    name = models.CharField(max_length=100, help_text='e.g. "Box of 5", "Carton (25 pcs)"')
    quantity_in_base_units = models.PositiveIntegerField(
        help_text='How many base units (pieces) this level contains in total.',
    )
    barcode = models.CharField(max_length=50, unique=True, blank=True, null=True)
    cost_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        help_text="Leave blank to auto-calculate as the item's base cost × quantity.",
    )
    sell_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        help_text="Leave blank to auto-calculate as the item's base sell price × quantity.",
    )
    is_purchase_unit = models.BooleanField(
        default=False, help_text='Can this level be ordered from a supplier (Purchasing module)?',
    )
    is_sale_unit = models.BooleanField(
        default=True, help_text='Can this level be sold at the till?',
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['quantity_in_base_units']

    def save(self, *args, **kwargs):
        if not self.barcode:
            self.barcode = None
        super().save(*args, **kwargs)

    @property
    def effective_cost_price(self):
        if self.cost_price is not None:
            return self.cost_price
        return self.item.cost_price * self.quantity_in_base_units

    @property
    def effective_sell_price(self):
        if self.sell_price is not None:
            return self.sell_price
        return self.item.sell_price * self.quantity_in_base_units

    def __str__(self):
        return f'{self.item.sku} — {self.name} ({self.quantity_in_base_units} base units)'


class StockLevel(models.Model):
    """
    Cached current quantity on hand, in base units, for one item at one
    outlet. This table is a read cache — the only thing allowed to change
    it is inventory.services.adjust_stock(), which keeps it in sync with
    StockLedger inside one atomic transaction. Never edit this by hand.
    """

    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='stock_levels')
    outlet = models.ForeignKey('outlets.Outlet', on_delete=models.CASCADE, related_name='stock_levels')
    quantity = models.IntegerField(default=0, help_text='Current quantity on hand, in base units.')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['item', 'outlet'], name='unique_stocklevel_item_outlet'),
        ]
        ordering = ['item__name']

    def __str__(self):
        return f'{self.item.sku} @ {self.outlet.name}: {self.quantity}'


class StockLedger(models.Model):
    """
    Immutable, append-only record of every stock change. Nothing should
    ever UPDATE or DELETE a row here — adjust_stock() only ever INSERTs.
    This is the audit trail: StockLevel.quantity should always equal the
    running sum of change_qty for that (item, outlet) pair, and
    balance_after on the latest row should always match it.
    """

    class Reason(models.TextChoices):
        PURCHASE_RECEIPT = 'purchase_receipt', 'Purchase receipt (goods received)'
        SALE = 'sale', 'Sale'
        SALE_VOID = 'sale_void', 'Sale voided / refunded'
        DAMAGE = 'damage', 'Damaged / written off'
        ADJUSTMENT = 'adjustment', 'Manual adjustment'
        TRANSFER_IN = 'transfer_in', 'Transfer in from another outlet'
        TRANSFER_OUT = 'transfer_out', 'Transfer out to another outlet'

    item = models.ForeignKey(Item, on_delete=models.PROTECT, related_name='ledger_entries')
    outlet = models.ForeignKey('outlets.Outlet', on_delete=models.PROTECT, related_name='ledger_entries')
    change_qty = models.IntegerField(help_text='Positive for stock in, negative for stock out. Never zero.')
    balance_after = models.IntegerField(help_text='Quantity on hand immediately after this entry, in base units.')
    reason = models.CharField(max_length=20, choices=Reason.choices)
    reference = models.CharField(
        max_length=100, blank=True,
        help_text='Optional free-text reference, e.g. a receipt or PO number.',
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='stock_ledger_entries',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        sign = '+' if self.change_qty > 0 else ''
        return f'{self.item.sku} @ {self.outlet.name}: {sign}{self.change_qty} ({self.reason})'
