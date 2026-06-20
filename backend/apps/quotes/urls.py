"""Quote URL routing."""
from django.urls import path

from apps.quotes import views

urlpatterns = [
    path("admin/dashboard/", views.QuoteDashboardView.as_view(), name="quotes-admin-dashboard"),
    path("admin/", views.QuoteListCreateView.as_view(), name="quotes-admin-list"),
    path("admin/<uuid:quote_id>/", views.QuoteDetailView.as_view(), name="quotes-admin-detail"),
    path("admin/<uuid:quote_id>/lines/", views.QuoteLineCreateView.as_view(), name="quotes-admin-lines"),
    path("admin/<uuid:quote_id>/submit/", views.QuoteSubmitView.as_view(), name="quotes-admin-submit"),
    path("admin/<uuid:quote_id>/approve/", views.QuoteApproveView.as_view(), name="quotes-admin-approve"),
    path("admin/<uuid:quote_id>/reject/", views.QuoteRejectView.as_view(), name="quotes-admin-reject"),
    path("admin/<uuid:quote_id>/send/", views.QuoteSendView.as_view(), name="quotes-admin-send"),
    path("admin/<uuid:quote_id>/convert/", views.QuoteConvertView.as_view(), name="quotes-admin-convert"),
    path("admin/<uuid:quote_id>/pdf/", views.QuotePdfView.as_view(), name="quotes-admin-pdf"),
    path("my/", views.CustomerQuoteListView.as_view(), name="quotes-customer-list"),
    path("my/<uuid:quote_id>/", views.CustomerQuoteDetailView.as_view(), name="quotes-customer-detail"),
    path("my/<uuid:quote_id>/accept/", views.CustomerQuoteAcceptView.as_view(), name="quotes-customer-accept"),
    path("my/<uuid:quote_id>/reject/", views.CustomerQuoteRejectView.as_view(), name="quotes-customer-reject"),
    path("my/<uuid:quote_id>/pdf/", views.CustomerQuotePdfView.as_view(), name="quotes-customer-pdf"),
]
