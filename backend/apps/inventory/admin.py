"""Django admin for inventory."""
from django.contrib import admin

from apps.inventory.models import InventoryLevel, InventoryTransaction, Warehouse


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "warehouse_type", "state", "is_active")
    search_fields = ("code", "name")
    list_filter = ("warehouse_type", "is_active")


@admin.register(InventoryLevel)
class InventoryLevelAdmin(admin.ModelAdmin):
    list_display = (
        "warehouse",
        "variant",
        "quantity_on_hand",
        "quantity_reserved",
        "average_cost_cents",
        "last_sale_price_cents",
    )
    search_fields = ("variant__sku", "warehouse__code")
    list_filter = ("warehouse",)


@admin.register(InventoryTransaction)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = (
        "movement_number",
        "transaction_type",
        "warehouse",
        "variant",
        "quantity_change",
        "unit_cost_cents",
        "sale_price_cents",
        "created_at",
    )
    search_fields = ("movement_number", "variant__sku", "warehouse__code")
    list_filter = ("transaction_type", "warehouse")
    readonly_fields = ("movement_number", "quantity_after", "created_at", "updated_at")
