from django.urls import path

from apps.inventory.admin_views import (
    WarehouseAdminDetailView,
    WarehouseAdminListCreateView,
)
from apps.inventory.views import (    InventoryLevelDetailView,
    InventoryListView,
    InventoryNotificationAcknowledgeView,
    InventoryNotificationCountView,
    InventoryNotificationListView,
    LedgerSummaryView,
    LowStockAlertListView,
    StockAdjustmentView,
    StockInView,
    StockMovementDetailView,
    StockMovementListView,
    StockOutView,
    StockTransferView,
    TransferListView,
    ValuationSummaryView,
    VariantInventoryView,
    WarehouseListView,
)

app_name = "inventory"

urlpatterns = [
    path("warehouses/", WarehouseListView.as_view(), name="warehouse-list"),
    path(
        "admin/warehouses/",
        WarehouseAdminListCreateView.as_view(),
        name="warehouse-admin-list",
    ),
    path(
        "admin/warehouses/<uuid:warehouse_id>/",
        WarehouseAdminDetailView.as_view(),
        name="warehouse-admin-detail",
    ),
    path("levels/", InventoryListView.as_view(), name="inventory-list"),
    path("levels/<uuid:level_id>/", InventoryLevelDetailView.as_view(), name="inventory-detail"),
    path("movements/", StockMovementListView.as_view(), name="movement-list"),
    path("movements/<uuid:movement_id>/", StockMovementDetailView.as_view(), name="movement-detail"),
    path("transfers/", TransferListView.as_view(), name="transfer-list"),
    path("ledger/summary/", LedgerSummaryView.as_view(), name="ledger-summary"),
    path("valuation/", ValuationSummaryView.as_view(), name="valuation-summary"),
    path("stock-in/", StockInView.as_view(), name="stock-in"),
    path("stock-out/", StockOutView.as_view(), name="stock-out"),
    path("stock-transfer/", StockTransferView.as_view(), name="stock-transfer"),
    path("adjustments/", StockAdjustmentView.as_view(), name="stock-adjustment"),
    path("alerts/low-stock/", LowStockAlertListView.as_view(), name="low-stock-alerts"),
    path("notifications/", InventoryNotificationListView.as_view(), name="notification-list"),
    path(
        "notifications/unread-count/",
        InventoryNotificationCountView.as_view(),
        name="notification-count",
    ),
    path(
        "notifications/<uuid:alert_id>/acknowledge/",
        InventoryNotificationAcknowledgeView.as_view(),
        name="notification-acknowledge",
    ),
    path("variants/<uuid:variant_id>/", VariantInventoryView.as_view(), name="variant-inventory"),
]
