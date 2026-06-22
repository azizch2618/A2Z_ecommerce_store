"""Quote & sales workflow API views."""
from __future__ import annotations

from uuid import UUID

from django.http import HttpResponse
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.customers.models import Customer
from apps.quotes.pdf_service import generate_quote_pdf
from apps.quotes.permissions import CanApproveQuotes, CanManageQuotes, CanViewQuotes
from apps.quotes.serializers import serialize_quote
from apps.quotes.services import QuoteService


def _parse_uuid(value: str | None) -> UUID | None:
    if not value:
        return None
    return UUID(str(value))


class IsAuthenticatedCustomer(IsAuthenticated):
    """Customer portal user with a linked Customer profile."""

    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        return Customer.objects.filter(user=request.user).exists()


class QuoteDashboardView(APIView):
    permission_classes = [CanViewQuotes]

    def get(self, request):
        kpis = QuoteService.get_dashboard_kpis()
        return Response(
            {
                "draftQuotes": kpis["draft_quotes"],
                "pendingApproval": kpis["pending_approval"],
                "accepted": kpis["accepted"],
                "converted": kpis["converted"],
                "conversionRate": kpis["conversion_rate"],
            }
        )


class QuoteListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == "POST":
            return [CanManageQuotes()]
        return [CanViewQuotes()]

    def get(self, request):
        qs = QuoteService.list_quotes(
            status=request.query_params.get("status"),
            search=request.query_params.get("search"),
            customer_id=_parse_uuid(request.query_params.get("customerId")),
        )
        return Response({"data": [serialize_quote(q) for q in qs[:200]]})

    def post(self, request):
        data = request.data
        quote = QuoteService.create_quote(
            actor=request.user,
            data={
                "customer_id": data.get("customerId"),
                "party_id": data.get("partyId"),
                "trade_account_id": data.get("tradeAccountId"),
                "crm_opportunity_id": data.get("opportunityId"),
                "notes": data.get("notes", ""),
                "terms_and_conditions": data.get("termsAndConditions"),
                "valid_until": data.get("validUntil"),
            },
        )
        return Response(serialize_quote(quote), status=status.HTTP_201_CREATED)


class QuoteDetailView(APIView):
    def get_permissions(self):
        if self.request.method in ("PATCH", "PUT"):
            return [CanManageQuotes()]
        return [CanViewQuotes()]

    def get(self, request, quote_id):
        quote = QuoteService.get_quote(quote_id)
        return Response(serialize_quote(quote))

    def patch(self, request, quote_id):
        quote = QuoteService.get_quote(quote_id)
        quote = QuoteService.update_quote(
            quote=quote,
            actor=request.user,
            data={
                k: v
                for k, v in {
                    "notes": request.data.get("notes"),
                    "terms_and_conditions": request.data.get("termsAndConditions"),
                    "valid_until": request.data.get("validUntil"),
                    "discount_cents": request.data.get("discountCents"),
                }.items()
                if v is not None
            },
        )
        return Response(serialize_quote(quote))


class QuoteLineCreateView(APIView):
    permission_classes = [CanManageQuotes]

    def post(self, request, quote_id):
        quote = QuoteService.get_quote(quote_id)
        line = QuoteService.add_line(
            quote=quote,
            actor=request.user,
            data={
                "variant_id": request.data.get("variantId"),
                "quantity": request.data.get("quantity", 1),
                "unit_price_ex_gst_cents": request.data.get("unitPriceExGstCents"),
                "discount_cents": request.data.get("discountCents", 0),
            },
        )
        quote.refresh_from_db()
        return Response(serialize_quote(quote), status=status.HTTP_201_CREATED)


class QuoteSubmitView(APIView):
    permission_classes = [CanManageQuotes]

    def post(self, request, quote_id):
        quote = QuoteService.submit_for_approval(
            quote=QuoteService.get_quote(quote_id), actor=request.user
        )
        return Response(serialize_quote(quote))


class QuoteApproveView(APIView):
    permission_classes = [CanApproveQuotes]

    def post(self, request, quote_id):
        quote = QuoteService.approve(
            quote=QuoteService.get_quote(quote_id),
            actor=request.user,
            comment=request.data.get("comment", ""),
        )
        return Response(serialize_quote(quote))


class QuoteRejectView(APIView):
    permission_classes = [CanApproveQuotes]

    def post(self, request, quote_id):
        quote = QuoteService.reject(
            quote=QuoteService.get_quote(quote_id),
            actor=request.user,
            comment=request.data.get("comment", ""),
        )
        return Response(serialize_quote(quote))


class QuoteSendView(APIView):
    permission_classes = [CanManageQuotes]

    def post(self, request, quote_id):
        quote = QuoteService.send_to_customer(
            quote=QuoteService.get_quote(quote_id), actor=request.user
        )
        return Response(serialize_quote(quote))


class QuoteConvertView(APIView):
    permission_classes = [CanManageQuotes]

    def post(self, request, quote_id):
        order = QuoteService.convert_to_order(
            quote=QuoteService.get_quote(quote_id), actor=request.user
        )
        quote = QuoteService.get_quote(quote_id)
        return Response(
            {
                "orderId": str(order.public_id),
                "orderNumber": order.order_number,
                "quote": serialize_quote(quote),
            },
            status=status.HTTP_201_CREATED,
        )


class QuotePdfView(APIView):
    permission_classes = [CanViewQuotes]

    def get(self, request, quote_id):
        quote = QuoteService.get_quote(quote_id)
        pdf_bytes = generate_quote_pdf(quote)
        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        response["Content-Disposition"] = f'inline; filename="{quote.quote_number}.pdf"'
        return response


class CustomerQuoteListView(APIView):
    permission_classes = [IsAuthenticatedCustomer]

    def get(self, request):
        customer = Customer.objects.filter(user=request.user).first()
        if not customer:
            return Response({"data": []})
        qs = QuoteService.list_quotes(customer_id=customer.public_id).filter(
            status__in=["sent", "accepted", "expired", "converted"]
        )
        return Response({"data": [serialize_quote(q) for q in qs[:100]]})


class CustomerQuoteDetailView(APIView):
    permission_classes = [IsAuthenticatedCustomer]

    def get(self, request, quote_id):
        quote = QuoteService.get_quote(quote_id)
        customer = Customer.objects.filter(user=request.user).first()
        if quote.customer_id and customer and quote.customer_id != customer.id:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(serialize_quote(quote))


class CustomerQuoteAcceptView(APIView):
    permission_classes = [IsAuthenticatedCustomer]

    def post(self, request, quote_id):
        customer = Customer.objects.filter(user=request.user).first()
        if not customer:
            return Response({"detail": "Customer profile required."}, status=status.HTTP_400_BAD_REQUEST)
        quote = QuoteService.customer_accept(
            quote=QuoteService.get_quote(quote_id), customer=customer
        )
        return Response(serialize_quote(quote))


class CustomerQuoteRejectView(APIView):
    permission_classes = [IsAuthenticatedCustomer]

    def post(self, request, quote_id):
        customer = Customer.objects.filter(user=request.user).first()
        if not customer:
            return Response({"detail": "Customer profile required."}, status=status.HTTP_400_BAD_REQUEST)
        quote = QuoteService.customer_reject(
            quote=QuoteService.get_quote(quote_id),
            customer=customer,
            reason=request.data.get("reason", ""),
        )
        return Response(serialize_quote(quote))


class CustomerQuotePdfView(APIView):
    permission_classes = [IsAuthenticatedCustomer]

    def get(self, request, quote_id):
        quote = QuoteService.get_quote(quote_id)
        customer = Customer.objects.filter(user=request.user).first()
        if quote.customer_id and customer and quote.customer_id != customer.id:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        pdf_bytes = generate_quote_pdf(quote)
        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        response["Content-Disposition"] = f'inline; filename="{quote.quote_number}.pdf"'
        return response
