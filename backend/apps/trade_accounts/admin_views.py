"""Admin trade account API views."""
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import CanApproveTrade, CanViewTrade
from apps.core.pagination import A2ZCursorPagination
from apps.trade_accounts.models import TradeAccount, TradeApplication
from apps.trade_accounts.services import TradeAdminService


class TradeApplicationPagination(A2ZCursorPagination):
    ordering = "-submitted_at"


class TradeApplicationListView(generics.ListAPIView):
    """GET /trade-accounts/admin/applications/"""

    permission_classes = [CanViewTrade]
    pagination_class = TradeApplicationPagination

    def list(self, request, *args, **kwargs):
        status_filter = request.query_params.get("status")
        qs = TradeAdminService.list_applications(status=status_filter)
        page = self.paginate_queryset(qs)
        rows = page if page is not None else qs[:100]
        data = [
            {
                "id": str(app.public_id),
                "companyName": app.organization.trading_name or app.organization.legal_name,
                "contactName": app.organization.legal_name,
                "email": app.organization.email,
                "abn": app.organization.abn or "",
                "status": app.status or "pending",
                "submittedAt": app.submitted_at.isoformat(),
                "notes": app.notes,
            }
            for app in rows
        ]
        if page is not None:
            return self.get_paginated_response(data)
        return Response({"data": data})


class TradeApplicationReviewView(APIView):
    """POST /trade-accounts/admin/applications/{id}/review/"""

    permission_classes = [CanApproveTrade]

    def post(self, request, application_id):
        application = TradeAdminService.get_application(application_id)
        action = request.data.get("status")
        notes = request.data.get("notes", "")

        if action == "approved":
            application = TradeAdminService.approve_application(
                application=application,
                reviewer=request.user,
                credit_limit_cents=int(request.data.get("credit_limit_cents", 0)),
                payment_terms_days=int(request.data.get("payment_terms_days", 30)),
                notes=notes,
            )
        elif action == "rejected":
            application = TradeAdminService.reject_application(
                application=application,
                reviewer=request.user,
                notes=notes,
            )
        else:
            return Response({"status": ["Must be approved or rejected."]}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {
                "id": str(application.public_id),
                "status": application.status,
                "notes": application.notes,
            }
        )


class TradeAccountCreditView(APIView):
    """PATCH /trade-accounts/admin/accounts/{id}/credit/"""

    permission_classes = [CanApproveTrade]

    def patch(self, request, account_id):
        account = TradeAccount.objects.filter(public_id=account_id).first()
        if not account:
            return Response({"detail": "Trade account not found."}, status=status.HTTP_404_NOT_FOUND)

        account = TradeAdminService.update_credit_limit(
            account=account,
            credit_limit_cents=int(request.data.get("credit_limit_cents", 0)),
            user=request.user,
        )
        return Response(
            {
                "id": str(account.public_id),
                "creditLimitCents": account.credit_limit_cents,
                "creditUsedCents": account.credit_used_cents,
            }
        )
