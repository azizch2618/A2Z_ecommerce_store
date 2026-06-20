"""Accounts Payable API views."""
from __future__ import annotations

from uuid import UUID

from django.utils.dateparse import parse_date
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.exceptions import NotFoundError
from apps.payables.permissions import CanApprovePayables, CanManagePayables, CanViewPayables
from apps.payables.serializers import (
    serialize_debit_note,
    serialize_supplier_invoice,
    serialize_supplier_payment,
)
from apps.payables.services import (
    DebitNoteService,
    PayablesReportingService,
    SupplierInvoiceService,
    SupplierPaymentService,
)
from apps.procurement.models import GoodsReceipt
from apps.suppliers.models import PurchaseOrder, Supplier


class PayablesSummaryView(APIView):
    permission_classes = [CanViewPayables]

    def get(self, request):
        return Response(PayablesReportingService.ap_summary())


class SupplierInvoiceListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == "POST":
            return [CanManagePayables()]
        return [CanViewPayables()]

    def get(self, request):
        supplier_id = request.query_params.get("supplierId")
        sid = UUID(supplier_id) if supplier_id else None
        qs = SupplierInvoiceService.list_invoices(
            status=request.query_params.get("status"),
            supplier_id=sid,
        )
        return Response({"data": [serialize_supplier_invoice(inv) for inv in qs[:200]]})

    def post(self, request):
        data = request.data
        po = PurchaseOrder.objects.filter(public_id=data["poId"]).select_related("supplier").first()
        if not po:
            raise NotFoundError("Purchase order not found.")
        grn = None
        if data.get("grnId"):
            grn = GoodsReceipt.objects.filter(public_id=data["grnId"]).first()
        inv = SupplierInvoiceService.create_from_po(
            purchase_order=po,
            actor=request.user,
            supplier_invoice_ref=data.get("supplierInvoiceRef", ""),
            goods_receipt=grn,
        )
        return Response(serialize_supplier_invoice(inv), status=status.HTTP_201_CREATED)


class SupplierInvoiceDetailView(APIView):
    permission_classes = [CanViewPayables]

    def get(self, request, invoice_id: UUID):
        inv = SupplierInvoiceService.get_invoice(invoice_id)
        return Response(serialize_supplier_invoice(inv))


class SupplierInvoiceSubmitView(APIView):
    permission_classes = [CanManagePayables]

    def post(self, request, invoice_id: UUID):
        inv = SupplierInvoiceService.get_invoice(invoice_id)
        inv = SupplierInvoiceService.submit(invoice=inv, actor=request.user)
        return Response(serialize_supplier_invoice(inv))


class SupplierInvoiceMatchView(APIView):
    permission_classes = [CanManagePayables]

    def post(self, request, invoice_id: UUID):
        inv = SupplierInvoiceService.get_invoice(invoice_id)
        inv = SupplierInvoiceService.match(invoice=inv, actor=request.user)
        return Response(serialize_supplier_invoice(inv))


class SupplierInvoiceApproveView(APIView):
    permission_classes = [CanApprovePayables]

    def post(self, request, invoice_id: UUID):
        inv = SupplierInvoiceService.get_invoice(invoice_id)
        inv = SupplierInvoiceService.approve(invoice=inv, actor=request.user)
        return Response(serialize_supplier_invoice(inv))


class SupplierInvoiceCancelView(APIView):
    permission_classes = [CanManagePayables]

    def post(self, request, invoice_id: UUID):
        inv = SupplierInvoiceService.get_invoice(invoice_id)
        inv = SupplierInvoiceService.cancel(invoice=inv, actor=request.user)
        return Response(serialize_supplier_invoice(inv))


class SupplierPaymentCreateView(APIView):
    permission_classes = [CanManagePayables]

    def post(self, request):
        data = request.data
        supplier = Supplier.objects.filter(public_id=data["supplierId"]).first()
        if not supplier:
            raise NotFoundError("Supplier not found.")
        payment = SupplierPaymentService.record_payment(
            supplier=supplier,
            amount_cents=int(data["amountCents"]),
            payment_date=parse_date(data["paymentDate"]),
            actor=request.user,
            reference=data.get("reference", ""),
            allocations=data.get("allocations"),
        )
        return Response(serialize_supplier_payment(payment), status=status.HTTP_201_CREATED)


class DebitNoteCreateView(APIView):
    permission_classes = [CanManagePayables]

    def post(self, request):
        data = request.data
        supplier = Supplier.objects.filter(public_id=data["supplierId"]).first()
        if not supplier:
            raise NotFoundError("Supplier not found.")
        invoice = None
        if data.get("invoiceId"):
            invoice = SupplierInvoiceService.get_invoice(data["invoiceId"])
        dn = DebitNoteService.create(
            supplier=supplier,
            actor=request.user,
            invoice=invoice,
            subtotal_ex_gst_cents=int(data["subtotalExGstCents"]),
            reason=data.get("reason", ""),
        )
        return Response(serialize_debit_note(dn), status=status.HTTP_201_CREATED)


class DebitNoteIssueView(APIView):
    permission_classes = [CanApprovePayables]

    def post(self, request, debit_note_id: UUID):
        from apps.payables.models import DebitNote

        dn = DebitNote.objects.filter(public_id=debit_note_id).first()
        if not dn:
            raise NotFoundError("Debit note not found.")
        dn = DebitNoteService.issue(debit_note=dn, actor=request.user)
        return Response(serialize_debit_note(dn))


class SupplierStatementView(APIView):
    permission_classes = [CanViewPayables]

    def get(self, request, supplier_id: UUID):
        supplier = Supplier.objects.filter(public_id=supplier_id).first()
        if not supplier:
            raise NotFoundError("Supplier not found.")
        return Response(PayablesReportingService.supplier_statement(supplier=supplier))


class SupplierAgingReportView(APIView):
    permission_classes = [CanViewPayables]

    def get(self, request):
        return Response({"data": PayablesReportingService.supplier_aging()})


class ApOutstandingBalancesView(APIView):
    permission_classes = [CanViewPayables]

    def get(self, request):
        aging = PayablesReportingService.supplier_aging()
        return Response(
            {
                "totalOutstandingCents": sum(r["totalOutstandingCents"] for r in aging),
                "suppliers": aging,
            }
        )
