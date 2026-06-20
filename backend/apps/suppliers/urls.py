from django.urls import path

from apps.suppliers.admin_views import SupplierAdminDetailView, SupplierAdminListCreateView
from apps.suppliers.views import (
    PurchaseOrderCancelView,
    PurchaseOrderConfirmView,
    PurchaseOrderDetailView,
    PurchaseOrderListCreateView,
    PurchaseOrderReceiveView,
    PurchaseOrderSubmitView,
    SupplierListView,
)

app_name = "suppliers"

urlpatterns = [
    path("", SupplierListView.as_view(), name="supplier-list"),
    path("admin/", SupplierAdminListCreateView.as_view(), name="supplier-admin-list"),
    path(
        "admin/<uuid:supplier_id>/",
        SupplierAdminDetailView.as_view(),
        name="supplier-admin-detail",
    ),    path(
        "purchase-orders/",
        PurchaseOrderListCreateView.as_view(),
        name="purchase-order-list",
    ),
    path(
        "purchase-orders/<uuid:po_id>/",
        PurchaseOrderDetailView.as_view(),
        name="purchase-order-detail",
    ),
    path(
        "purchase-orders/<uuid:po_id>/submit/",
        PurchaseOrderSubmitView.as_view(),
        name="purchase-order-submit",
    ),
    path(
        "purchase-orders/<uuid:po_id>/confirm/",
        PurchaseOrderConfirmView.as_view(),
        name="purchase-order-confirm",
    ),
    path(
        "purchase-orders/<uuid:po_id>/receive/",
        PurchaseOrderReceiveView.as_view(),
        name="purchase-order-receive",
    ),
    path(
        "purchase-orders/<uuid:po_id>/cancel/",
        PurchaseOrderCancelView.as_view(),
        name="purchase-order-cancel",
    ),
]
