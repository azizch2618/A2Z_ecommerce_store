"""Accounting URL routing."""
from django.urls import path

from apps.accounting import views

urlpatterns = [
    path("admin/chart-of-accounts/", views.ChartOfAccountListCreateView.as_view(), name="coa-list"),
    path(
        "admin/chart-of-accounts/<uuid:account_id>/",
        views.ChartOfAccountDetailView.as_view(),
        name="coa-detail",
    ),
    path("admin/fiscal-years/", views.FiscalYearListCreateView.as_view(), name="fy-list"),
    path(
        "admin/periods/<uuid:period_id>/close/",
        views.AccountingPeriodCloseView.as_view(),
        name="period-close",
    ),
    path(
        "admin/periods/<uuid:period_id>/reopen/",
        views.AccountingPeriodReopenView.as_view(),
        name="period-reopen",
    ),
    path("admin/journals/", views.JournalEntryListCreateView.as_view(), name="je-list"),
    path("admin/journals/<uuid:entry_id>/", views.JournalEntryDetailView.as_view(), name="je-detail"),
    path(
        "admin/journals/<uuid:entry_id>/lines/",
        views.JournalLineCreateView.as_view(),
        name="je-lines",
    ),
    path(
        "admin/journals/<uuid:entry_id>/post/",
        views.JournalEntryPostView.as_view(),
        name="je-post",
    ),
    path("admin/event-mappings/", views.EventMappingListView.as_view(), name="event-mappings"),
    path("admin/tax/calculate/", views.TaxCalculateView.as_view(), name="tax-calculate"),
    path("admin/reports/trial-balance/", views.TrialBalanceReportView.as_view(), name="trial-balance"),
    path("admin/reports/general-ledger/", views.GeneralLedgerReportView.as_view(), name="general-ledger"),
    path("admin/reports/gst-summary/", views.GstSummaryReportView.as_view(), name="gst-summary"),
    path("admin/audit-log/", views.AccountingAuditLogListView.as_view(), name="accounting-audit"),
]
