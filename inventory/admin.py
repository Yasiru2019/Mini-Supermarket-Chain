from django.contrib import admin

from .models import Category, Item, PackagingLevel, StockLedger, StockLevel


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)


class PackagingLevelInline(admin.TabularInline):
    model = PackagingLevel
    extra = 1
    fields = (
        'name', 'quantity_in_base_units', 'barcode',
        'cost_price', 'sell_price', 'is_purchase_unit', 'is_sale_unit', 'is_active',
    )


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = (
        'sku', 'name', 'category', 'unit_of_measure',
        'cost_price', 'sell_price', 'reorder_level', 'is_active',
    )
    list_filter = ('category', 'is_active', 'unit_of_measure')
    search_fields = ('sku', 'barcode', 'name')
    inlines = [PackagingLevelInline]


class ReadOnlyAdminMixin:
    """
    Lets staff view these rows in /admin/ for visibility, but blocks
    add/change/delete — every change to stock must go through
    inventory.services.adjust_stock() so StockLedger stays trustworthy.
    """

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(StockLevel)
class StockLevelAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    list_display = ('item', 'outlet', 'quantity', 'updated_at')
    list_filter = ('outlet',)
    search_fields = ('item__sku', 'item__name')


@admin.register(StockLedger)
class StockLedgerAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    list_display = (
        'created_at', 'item', 'outlet', 'change_qty',
        'balance_after', 'reason', 'reference', 'created_by',
    )
    list_filter = ('outlet', 'reason')
    search_fields = ('item__sku', 'item__name', 'reference')
    date_hierarchy = 'created_at'
