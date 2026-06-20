"""Procurement URL routing."""
from django.urls import path

from apps.procurement import views

urlpatterns = [
    path("admin/dashboard/", views.ProcurementDashboardView.as_view(), name="procurement-dashboard"),
    path("admin/requests/", views.PurchaseRequestListCreateView.as_view(), name="pr-list"),
    path("admin/requests/<uuid:request_id>/", views.PurchaseRequestDetailView.as_view(), name="pr-detail"),
    path(
        "admin/requests/<uuid:request_id>/lines/",
        views.PurchaseRequestLineCreateView.as_view(),
        name="pr-lines",
    ),
    path(
        "admin/requests/<uuid:request_id>/submit/",
        views.PurchaseRequestSubmitView.as_view(),
        name="pr-submit",
    ),
    path(
        "admin/requests/<uuid:request_id>/approve/",
        views.PurchaseRequestApproveView.as_view(),
        name="pr-approve",
    ),
    path(
        "admin/requests/<uuid:request_id>/reject/",
        views.PurchaseRequestRejectView.as_view(),
        name="pr-reject",
    ),
    path(
        "admin/requests/<uuid:request_id>/convert/",
        views.PurchaseRequestConvertView.as_view(),
        name="pr-convert",
    ),
    path("admin/goods-receipts/", views.GoodsReceiptListView.as_view(), name="grn-list"),
    path(
        "admin/suppliers/<uuid:supplier_id>/performance/",
        views.SupplierPerformanceView.as_view(),
        name="supplier-performance",
    ),
    path(
        "admin/purchase-orders/<uuid:po_id>/approve/",
        views.PurchaseOrderApproveView.as_view(),
        name="po-approve",
    ),
    path("portal/dashboard/", views.SupplierPortalDashboardView.as_view(), name="portal-dashboard"),
    path("portal/purchase-orders/", views.SupplierPortalPOListView.as_view(), name="portal-po-list"),
    path(
        "portal/purchase-orders/<uuid:po_id>/",
        views.SupplierPortalPODetailView.as_view(),
        name="portal-po-detail",
    ),
    path(
        "portal/purchase-orders/<uuid:po_id>/acknowledge/",
        views.SupplierPortalPOAcknowledgeView.as_view(),
        name="portal-po-ack",
    ),
    path(
        "portal/purchase-orders/<uuid:po_id>/expected-delivery/",
        views.SupplierPortalPOExpectedDeliveryView.as_view(),
        name="portal-po-expected",
    ),
    path(
        "portal/purchase-orders/<uuid:po_id>/payment-status/",
        views.SupplierPortalPaymentStatusView.as_view(),
        name="portal-po-payment",
    ),
    path("portal/documents/", views.SupplierPortalDocumentListView.as_view(), name="portal-docs"),
    path(
        "portal/documents/upload/",
        views.SupplierPortalDocumentUploadView.as_view(),
        name="portal-doc-upload",
    ),
]
