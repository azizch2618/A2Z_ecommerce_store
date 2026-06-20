from django.urls import path

from apps.receivables import views

urlpatterns = [
    path("admin/summary/", views.ReceivablesSummaryView.as_view(), name="ar-summary"),
    path("admin/invoices/", views.CustomerInvoiceListCreateView.as_view(), name="ar-invoice-list"),
    path("admin/invoices/<uuid:invoice_id>/", views.CustomerInvoiceDetailView.as_view(), name="ar-invoice-detail"),
    path(
        "admin/invoices/<uuid:invoice_id>/lines/",
        views.CustomerInvoiceLineCreateView.as_view(),
        name="ar-invoice-lines",
    ),
    path(
        "admin/invoices/<uuid:invoice_id>/issue/",
        views.CustomerInvoiceIssueView.as_view(),
        name="ar-invoice-issue",
    ),
    path(
        "admin/invoices/<uuid:invoice_id>/cancel/",
        views.CustomerInvoiceCancelView.as_view(),
        name="ar-invoice-cancel",
    ),
    path("admin/payments/", views.CustomerPaymentCreateView.as_view(), name="ar-payment"),
    path("admin/credit-notes/", views.CreditNoteCreateView.as_view(), name="ar-credit-note"),
    path(
        "admin/credit-notes/<uuid:credit_note_id>/issue/",
        views.CreditNoteIssueView.as_view(),
        name="ar-credit-note-issue",
    ),
    path(
        "admin/customers/<uuid:customer_id>/statement/",
        views.CustomerStatementView.as_view(),
        name="ar-statement",
    ),
    path("admin/reports/aging/", views.CustomerAgingReportView.as_view(), name="ar-aging"),
    path("admin/reports/outstanding/", views.OutstandingBalancesView.as_view(), name="ar-outstanding"),
]
