"""Accounts Receivable API views."""
from __future__ import annotations

from uuid import UUID

from django.utils.dateparse import parse_date
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.exceptions import NotFoundError
from apps.customers.models import Customer
from apps.orders.models import Order
from apps.receivables.permissions import CanApproveReceivables, CanManageReceivables, CanViewReceivables
from apps.receivables.serializers import (
    serialize_credit_note,
    serialize_customer_invoice,
    serialize_customer_payment,
)
from apps.receivables.services import (
    CreditNoteService,
    CustomerInvoiceService,
    CustomerPaymentService,
    ReceivablesReportingService,
)


class ReceivablesSummaryView(APIView):
    permission_classes = [CanViewReceivables]

    def get(self, request):
        return Response(ReceivablesReportingService.ar_summary())


class CustomerInvoiceListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == "POST":
            return [CanManageReceivables()]
        return [CanViewReceivables()]

    def get(self, request):
        customer_id = request.query_params.get("customerId")
        cid = UUID(customer_id) if customer_id else None
        qs = CustomerInvoiceService.list_invoices(
            status=request.query_params.get("status"),
            customer_id=cid,
        )
        return Response({"data": [serialize_customer_invoice(inv) for inv in qs[:200]]})

    def post(self, request):
        data = request.data
        customer = Customer.objects.filter(public_id=data["customerId"]).first()
        if not customer:
            raise NotFoundError("Customer not found.")
        order = None
        if data.get("orderId"):
            order = Order.objects.filter(public_id=data["orderId"]).first()
            if order:
                inv = CustomerInvoiceService.create_from_order(order=order, actor=request.user)
                return Response(serialize_customer_invoice(inv), status=status.HTTP_201_CREATED)
        inv = CustomerInvoiceService.create(
            customer=customer,
            actor=request.user,
            payment_terms_days=data.get("paymentTermsDays"),
            notes=data.get("notes", ""),
        )
        return Response(serialize_customer_invoice(inv), status=status.HTTP_201_CREATED)


class CustomerInvoiceDetailView(APIView):
    permission_classes = [CanViewReceivables]

    def get(self, request, invoice_id: UUID):
        inv = CustomerInvoiceService.get_invoice(invoice_id)
        return Response(serialize_customer_invoice(inv))


class CustomerInvoiceLineCreateView(APIView):
    permission_classes = [CanManageReceivables]

    def post(self, request, invoice_id: UUID):
        inv = CustomerInvoiceService.get_invoice(invoice_id)
        data = request.data
        CustomerInvoiceService.add_line(
            invoice=inv,
            description=data["description"],
            quantity=int(data.get("quantity", 1)),
            unit_price_ex_gst_cents=int(data["unitPriceExGstCents"]),
        )
        inv = CustomerInvoiceService.get_invoice(invoice_id)
        return Response(serialize_customer_invoice(inv), status=status.HTTP_201_CREATED)


class CustomerInvoiceIssueView(APIView):
    permission_classes = [CanManageReceivables]

    def post(self, request, invoice_id: UUID):
        inv = CustomerInvoiceService.get_invoice(invoice_id)
        issue_date = parse_date(request.data.get("issueDate", "")) if request.data.get("issueDate") else None
        inv = CustomerInvoiceService.issue(invoice=inv, actor=request.user, issue_date=issue_date)
        return Response(serialize_customer_invoice(inv))


class CustomerInvoiceCancelView(APIView):
    permission_classes = [CanManageReceivables]

    def post(self, request, invoice_id: UUID):
        inv = CustomerInvoiceService.get_invoice(invoice_id)
        inv = CustomerInvoiceService.cancel(invoice=inv, actor=request.user)
        return Response(serialize_customer_invoice(inv))


class CustomerPaymentCreateView(APIView):
    permission_classes = [CanManageReceivables]

    def post(self, request):
        data = request.data
        customer = Customer.objects.filter(public_id=data["customerId"]).first()
        if not customer:
            raise NotFoundError("Customer not found.")
        payment = CustomerPaymentService.record_payment(
            customer=customer,
            amount_cents=int(data["amountCents"]),
            payment_date=parse_date(data["paymentDate"]),
            actor=request.user,
            payment_method=data.get("paymentMethod", "bank_transfer"),
            reference=data.get("reference", ""),
            allocations=data.get("allocations"),
        )
        return Response(serialize_customer_payment(payment), status=status.HTTP_201_CREATED)


class CreditNoteCreateView(APIView):
    permission_classes = [CanManageReceivables]

    def post(self, request):
        data = request.data
        customer = Customer.objects.filter(public_id=data["customerId"]).first()
        if not customer:
            raise NotFoundError("Customer not found.")
        invoice = None
        if data.get("invoiceId"):
            invoice = CustomerInvoiceService.get_invoice(data["invoiceId"])
        cn = CreditNoteService.create(
            customer=customer,
            actor=request.user,
            invoice=invoice,
            subtotal_ex_gst_cents=int(data["subtotalExGstCents"]),
            reason=data.get("reason", ""),
        )
        return Response(serialize_credit_note(cn), status=status.HTTP_201_CREATED)


class CreditNoteIssueView(APIView):
    permission_classes = [CanApproveReceivables]

    def post(self, request, credit_note_id: UUID):
        from apps.receivables.models import CreditNote

        cn = CreditNote.objects.filter(public_id=credit_note_id).first()
        if not cn:
            raise NotFoundError("Credit note not found.")
        cn = CreditNoteService.issue(credit_note=cn, actor=request.user)
        return Response(serialize_credit_note(cn))


class CustomerStatementView(APIView):
    permission_classes = [CanViewReceivables]

    def get(self, request, customer_id: UUID):
        customer = Customer.objects.filter(public_id=customer_id).first()
        if not customer:
            raise NotFoundError("Customer not found.")
        return Response(ReceivablesReportingService.customer_statement(customer=customer))


class CustomerAgingReportView(APIView):
    permission_classes = [CanViewReceivables]

    def get(self, request):
        return Response({"data": ReceivablesReportingService.customer_aging()})


class OutstandingBalancesView(APIView):
    permission_classes = [CanViewReceivables]

    def get(self, request):
        aging = ReceivablesReportingService.customer_aging()
        return Response(
            {
                "totalOutstandingCents": sum(r["totalOutstandingCents"] for r in aging),
                "customers": aging,
            }
        )
