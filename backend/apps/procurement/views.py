"""Procurement and supplier portal API views."""
from __future__ import annotations

from django.http import HttpResponse
from django.utils.dateparse import parse_datetime
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.exceptions import NotFoundError

from apps.procurement.permissions import (
    CanAccessSupplierPortal,
    CanApproveProcurement,
    CanManageProcurement,
    CanViewProcurement,
)
from apps.procurement.serializers import (
    serialize_goods_receipt,
    serialize_purchase_request,
    serialize_supplier_document,
    serialize_supplier_kpis,
    serialize_supplier_po,
)
from apps.procurement.services import (
    ProcurementDashboardService,
    PurchaseRequestService,
    SupplierPerformanceService,
    SupplierPortalService,
)
from apps.suppliers.serializers import PurchaseOrderSerializer
from apps.suppliers.services import PurchaseOrderService


class ProcurementDashboardView(APIView):
    permission_classes = [CanViewProcurement]

    def get(self, request):
        kpis = ProcurementDashboardService.get_dashboard_kpis()
        perf = kpis.pop("supplier_performance")
        return Response(
            {
                "openRequisitions": kpis["open_requisitions"],
                "openPurchaseOrders": kpis["open_purchase_orders"],
                "procurementSpendCents": kpis["procurement_spend_cents"],
                "onTimeDeliveryPct": perf["on_time_delivery_pct"],
                "avgLeadTimeDays": perf["avg_lead_time_days"],
                "orderAccuracyPct": perf["order_accuracy_pct"],
            }
        )


class PurchaseRequestListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == "POST":
            return [CanManageProcurement()]
        return [CanViewProcurement()]

    def get(self, request):
        qs = PurchaseRequestService.list_requests(
            status=request.query_params.get("status"),
            search=request.query_params.get("search"),
        )
        return Response({"data": [serialize_purchase_request(pr) for pr in qs[:200]]})

    def post(self, request):
        data = request.data
        pr = PurchaseRequestService.create(
            actor=request.user,
            data={
                "warehouse_code": data.get("warehouseCode", "SYD1"),
                "supplier_id": data.get("supplierId"),
                "department_id": data.get("departmentId"),
                "cost_center_id": data.get("costCenterId"),
                "priority": data.get("priority", "medium"),
                "justification": data.get("justification", ""),
            },
        )
        return Response(serialize_purchase_request(pr), status=status.HTTP_201_CREATED)


class PurchaseRequestDetailView(APIView):
    permission_classes = [CanViewProcurement]

    def get(self, request, request_id):
        return Response(serialize_purchase_request(PurchaseRequestService.get_request(request_id)))


class PurchaseRequestLineCreateView(APIView):
    permission_classes = [CanManageProcurement]

    def post(self, request, request_id):
        pr = PurchaseRequestService.get_request(request_id)
        PurchaseRequestService.add_line(
            pr=pr,
            actor=request.user,
            data={
                "sku": request.data.get("sku"),
                "quantity": request.data.get("quantity", 1),
                "unit_cost_cents": request.data.get("unitCostCents", 0),
                "notes": request.data.get("notes", ""),
            },
        )
        pr.refresh_from_db()
        return Response(serialize_purchase_request(pr), status=status.HTTP_201_CREATED)


class PurchaseRequestSubmitView(APIView):
    permission_classes = [CanManageProcurement]

    def post(self, request, request_id):
        pr = PurchaseRequestService.submit(
            pr=PurchaseRequestService.get_request(request_id), actor=request.user
        )
        return Response(serialize_purchase_request(pr))


class PurchaseRequestApproveView(APIView):
    permission_classes = [CanApproveProcurement]

    def post(self, request, request_id):
        pr = PurchaseRequestService.approve(
            pr=PurchaseRequestService.get_request(request_id),
            actor=request.user,
            comment=request.data.get("comment", ""),
        )
        return Response(serialize_purchase_request(pr))


class PurchaseRequestRejectView(APIView):
    permission_classes = [CanApproveProcurement]

    def post(self, request, request_id):
        pr = PurchaseRequestService.reject(
            pr=PurchaseRequestService.get_request(request_id),
            actor=request.user,
            comment=request.data.get("comment", ""),
        )
        return Response(serialize_purchase_request(pr))


class PurchaseRequestConvertView(APIView):
    permission_classes = [CanManageProcurement]

    def post(self, request, request_id):
        po = PurchaseRequestService.convert_to_po(
            pr=PurchaseRequestService.get_request(request_id), actor=request.user
        )
        return Response(
            {
                "poId": str(po.public_id),
                "poNumber": po.po_number,
                "request": serialize_purchase_request(
                    PurchaseRequestService.get_request(request_id)
                ),
            },
            status=status.HTTP_201_CREATED,
        )


class GoodsReceiptListView(APIView):
    permission_classes = [CanViewProcurement]

    def get(self, request):
        from apps.procurement.models import GoodsReceipt

        qs = GoodsReceipt.objects.select_related("purchase_order").order_by("-received_at")[:100]
        return Response({"data": [serialize_goods_receipt(grn) for grn in qs]})


class SupplierPerformanceView(APIView):
    permission_classes = [CanViewProcurement]

    def get(self, request, supplier_id):
        from apps.core.resolvers import resolve_supplier

        supplier = resolve_supplier(supplier_id)
        return Response(
            serialize_supplier_kpis(SupplierPerformanceService.get_supplier_kpis(supplier))
        )


class PurchaseOrderApproveView(APIView):
    permission_classes = [CanApproveProcurement]

    def post(self, request, po_id):
        po = PurchaseOrderService.get_by_public_id(po_id)
        po = PurchaseOrderService.approve(
            po=po, user=request.user, comment=request.data.get("comment", "")
        )
        return Response(PurchaseOrderSerializer(po).data)


# --- Supplier Portal ---


class SupplierPortalMixin:
    def get_supplier(self, request):
        supplier = SupplierPortalService.get_supplier_for_user(request.user)
        if not supplier:
            raise NotFoundError("No supplier linked to this account.")
        return supplier

    def handle_exception(self, exc):
        if isinstance(exc, NotFoundError):
            return Response({"detail": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        return super().handle_exception(exc)


class SupplierPortalDashboardView(SupplierPortalMixin, APIView):
    permission_classes = [CanAccessSupplierPortal]

    def get(self, request):
        supplier = self.get_supplier(request)
        kpis = serialize_supplier_kpis(
            SupplierPerformanceService.get_supplier_kpis(supplier)
        )
        open_pos = SupplierPortalService.list_pos_for_supplier(supplier).count()
        return Response({**kpis, "openPurchaseOrders": open_pos})


class SupplierPortalPOListView(SupplierPortalMixin, APIView):
    permission_classes = [CanAccessSupplierPortal]

    def get(self, request):
        supplier = self.get_supplier(request)
        qs = SupplierPortalService.list_pos_for_supplier(
            supplier, status=request.query_params.get("status")
        )
        return Response({"data": [serialize_supplier_po(po) for po in qs[:100]]})


class SupplierPortalPODetailView(SupplierPortalMixin, APIView):
    permission_classes = [CanAccessSupplierPortal]

    def get(self, request, po_id):
        supplier = self.get_supplier(request)
        po = PurchaseOrderService.get_by_public_id(po_id)
        if po.supplier_id != supplier.id:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(serialize_supplier_po(po))


class SupplierPortalPOAcknowledgeView(SupplierPortalMixin, APIView):
    permission_classes = [CanAccessSupplierPortal]

    def post(self, request, po_id):
        supplier = self.get_supplier(request)
        po = PurchaseOrderService.get_by_public_id(po_id)
        po = SupplierPortalService.acknowledge_po(po=po, supplier=supplier, user=request.user)
        return Response(serialize_supplier_po(po))


class SupplierPortalPOExpectedDeliveryView(SupplierPortalMixin, APIView):
    permission_classes = [CanAccessSupplierPortal]

    def post(self, request, po_id):
        supplier = self.get_supplier(request)
        po = PurchaseOrderService.get_by_public_id(po_id)
        expected_raw = request.data.get("expectedAt")
        expected_at = parse_datetime(expected_raw) if expected_raw else None
        if not expected_at:
            return Response(
                {"detail": "expectedAt is required."}, status=status.HTTP_400_BAD_REQUEST
            )
        po = SupplierPortalService.update_expected_delivery(
            po=po, supplier=supplier, user=request.user, expected_at=expected_at
        )
        return Response(serialize_supplier_po(po))


class SupplierPortalPaymentStatusView(SupplierPortalMixin, APIView):
    permission_classes = [CanAccessSupplierPortal]

    def get(self, request, po_id):
        supplier = self.get_supplier(request)
        po = PurchaseOrderService.get_by_public_id(po_id)
        if po.supplier_id != supplier.id:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(SupplierPortalService.payment_status_for_po(po))


class SupplierPortalDocumentUploadView(SupplierPortalMixin, APIView):
    permission_classes = [CanAccessSupplierPortal]

    def post(self, request):
        supplier = self.get_supplier(request)
        file = request.FILES.get("file")
        if not file:
            return Response({"detail": "file is required."}, status=status.HTTP_400_BAD_REQUEST)
        po = None
        po_id = request.data.get("poId")
        if po_id:
            po = PurchaseOrderService.get_by_public_id(po_id)
            if po.supplier_id != supplier.id:
                return Response({"detail": "PO not found."}, status=status.HTTP_404_NOT_FOUND)
        doc = SupplierPortalService.upload_document(
            supplier=supplier,
            user=request.user,
            file=file,
            document_type=request.data.get("documentType", "other"),
            purchase_order=po,
            notes=request.data.get("notes", ""),
        )
        return Response(serialize_supplier_document(doc), status=status.HTTP_201_CREATED)


class SupplierPortalDocumentListView(SupplierPortalMixin, APIView):
    permission_classes = [CanAccessSupplierPortal]

    def get(self, request):
        from apps.procurement.models import SupplierDocument

        supplier = self.get_supplier(request)
        docs = SupplierDocument.objects.filter(supplier=supplier).order_by("-created_at")[:50]
        return Response({"data": [serialize_supplier_document(d) for d in docs]})
