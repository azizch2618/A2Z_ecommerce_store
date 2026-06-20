from django.urls import path

from apps.trade_accounts.admin_views import (
    TradeAccountCreditView,
    TradeApplicationListView,
    TradeApplicationReviewView,
)
from apps.trade_accounts.views import QuoteListView, TradeAccountMeView

app_name = "trade_accounts"

urlpatterns = [
    path("me/", TradeAccountMeView.as_view(), name="me"),
    path("quotes/", QuoteListView.as_view(), name="quote-list"),
    path("admin/applications/", TradeApplicationListView.as_view(), name="admin-applications"),
    path(
        "admin/applications/<uuid:application_id>/review/",
        TradeApplicationReviewView.as_view(),
        name="admin-application-review",
    ),
    path(
        "admin/accounts/<uuid:account_id>/credit/",
        TradeAccountCreditView.as_view(),
        name="admin-account-credit",
    ),
]
