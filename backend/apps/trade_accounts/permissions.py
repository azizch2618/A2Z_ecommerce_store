from rest_framework.permissions import BasePermission

from apps.trade_accounts.services import TradeAccountService


class IsApprovedTradeAccount(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        account = TradeAccountService.get_for_user(request.user)
        return account is not None
