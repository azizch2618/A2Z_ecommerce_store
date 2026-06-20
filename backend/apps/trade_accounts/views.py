from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.customers.serializers import OrganizationSerializer
from apps.trade_accounts.permissions import IsApprovedTradeAccount
from apps.trade_accounts.serializers import QuoteSerializer, TradeAccountSerializer
from apps.trade_accounts.services import TradeAccountService


class TradeAccountMeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        account = TradeAccountService.get_for_user(request.user)
        if not account:
            return Response({"detail": "No trade account found."}, status=404)
        data = TradeAccountSerializer(account).data
        data["organization"] = OrganizationSerializer(account.organization).data
        return Response(data)


class QuoteListView(generics.ListAPIView):
    serializer_class = QuoteSerializer
    permission_classes = [IsAuthenticated, IsApprovedTradeAccount]

    def get_queryset(self):
        account = TradeAccountService.get_for_user(self.request.user)
        return account.quotes.all() if account else []
