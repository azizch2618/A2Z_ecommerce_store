from django.urls import path

from apps.payables import views

urlpatterns = [
    path("admin/summary/", views.PayablesSummaryView.as_view(), name="ap-summary"),
    path("admin/invoices/", views.SupplierInvoiceListCreateView.as_view(), name="ap-invoice-list"),
    path("admin/invoices/<uuid:invoice_id>/", views.SupplierInvoiceDetailView.as_view(), name="ap-invoice-detail"),
    path(
        "admin/invoices/<uuid:invoice_id>/submit/",
        views.SupplierInvoiceSubmitView.as_view(),
        name="ap-invoice-submit",
    ),
    path(
        "admin/invoices/<uuid:invoice_id>/match/",
        views.SupplierInvoiceMatchView.as_view(),
        name="ap-invoice-match",
    ),
    path(
        "admin/invoices/<uuid:invoice_id>/approve/",
        views.SupplierInvoiceApproveView.as_view(),
        name="ap-invoice-approve",
    ),
    path(
        "admin/invoices/<uuid:invoice_id>/cancel/",
        views.SupplierInvoiceCancelView.as_view(),
        name="ap-invoice-cancel",
    ),
    path("admin/payments/", views.SupplierPaymentCreateView.as_view(), name="ap-payment"),
    path("admin/debit-notes/", views.DebitNoteCreateView.as_view(), name="ap-debit-note"),
    path(
        "admin/debit-notes/<uuid:debit_note_id>/issue/",
        views.DebitNoteIssueView.as_view(),
        name="ap-debit-note-issue",
    ),
    path(
        "admin/suppliers/<uuid:supplier_id>/statement/",
        views.SupplierStatementView.as_view(),
        name="ap-statement",
    ),
    path("admin/reports/aging/", views.SupplierAgingReportView.as_view(), name="ap-aging"),
    path("admin/reports/outstanding/", views.ApOutstandingBalancesView.as_view(), name="ap-outstanding"),
]
