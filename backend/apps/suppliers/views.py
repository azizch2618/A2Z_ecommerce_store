from rest_framework import generics, status

from rest_framework.response import Response

from rest_framework.views import APIView



from apps.accounts.permissions import (
    CanManageInventory,
    CanManageSuppliers,
    CanManageWarehouse,
    CanViewInventory,
    CanViewSuppliers,
    require_permissions,
)

from apps.accounts.rbac import PermissionCodename

from apps.core.pagination import A2ZCursorPagination

from apps.suppliers.serializers import (

    CreatePurchaseOrderSerializer,

    PurchaseOrderSerializer,

    ReceivePurchaseOrderSerializer,

    SupplierSerializer,

)

from apps.suppliers.services import PurchaseOrderService, SupplierService





class SupplierPagination(A2ZCursorPagination):

    ordering = "name"





class SupplierListView(generics.ListAPIView):

    """GET /suppliers/"""



    serializer_class = SupplierSerializer

    permission_classes = [CanViewSuppliers]

    pagination_class = SupplierPagination



    def get_queryset(self):

        return SupplierService.list_active()





class PurchaseOrderPagination(A2ZCursorPagination):

    ordering = "-created_at"





class PurchaseOrderListCreateView(generics.ListCreateAPIView):

    """GET/POST /suppliers/purchase-orders/"""



    pagination_class = PurchaseOrderPagination



    def get_permissions(self):

        if self.request.method == "POST":

            return [require_permissions(PermissionCodename.SUPPLIERS_MANAGE)()]

        return [CanViewSuppliers()]



    def get_serializer_class(self):

        if self.request.method == "POST":

            return CreatePurchaseOrderSerializer

        return PurchaseOrderSerializer



    def get_queryset(self):

        status_filter = self.request.query_params.get("status")

        return PurchaseOrderService.get_queryset(status=status_filter)



    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        po = serializer.save()

        return Response(

            PurchaseOrderSerializer(po).data,

            status=status.HTTP_201_CREATED,

        )





class PurchaseOrderDetailView(generics.RetrieveAPIView):

    """GET /suppliers/purchase-orders/{id}/"""



    serializer_class = PurchaseOrderSerializer

    permission_classes = [CanViewSuppliers]

    lookup_field = "public_id"

    lookup_url_kwarg = "po_id"



    def get_queryset(self):

        return PurchaseOrderService.get_queryset()





class PurchaseOrderSubmitView(APIView):

    """POST /suppliers/purchase-orders/{id}/submit/"""



    permission_classes = [CanManageSuppliers]



    def post(self, request, po_id):
        from apps.core.audit import log_operation
        from apps.core.models import OperationalAuditLog

        po = PurchaseOrderService.get_by_public_id(po_id)
        po = PurchaseOrderService.submit(po=po)
        log_operation(
            user=request.user,
            module=OperationalAuditLog.Module.SUPPLIERS,
            action="po_submit",
            resource_type="purchase_order",
            resource_id=po.public_id,
        )
        return Response(PurchaseOrderSerializer(po).data)





class PurchaseOrderConfirmView(APIView):

    """POST /suppliers/purchase-orders/{id}/confirm/"""



    permission_classes = [CanManageSuppliers]



    def post(self, request, po_id):
        from apps.core.audit import log_operation
        from apps.core.models import OperationalAuditLog

        po = PurchaseOrderService.get_by_public_id(po_id)
        po = PurchaseOrderService.confirm(po=po)
        log_operation(
            user=request.user,
            module=OperationalAuditLog.Module.SUPPLIERS,
            action="po_confirm",
            resource_type="purchase_order",
            resource_id=po.public_id,
        )
        return Response(PurchaseOrderSerializer(po).data)





class PurchaseOrderReceiveView(APIView):

    """POST /suppliers/purchase-orders/{id}/receive/ — goods receipt → stock in."""



    permission_classes = [CanManageInventory]



    def post(self, request, po_id):
        from apps.core.audit import log_operation
        from apps.core.models import OperationalAuditLog

        po = PurchaseOrderService.get_by_public_id(po_id)
        serializer = ReceivePurchaseOrderSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        po = serializer.save(po)
        log_operation(
            user=request.user,
            module=OperationalAuditLog.Module.SUPPLIERS,
            action="po_receive",
            resource_type="purchase_order",
            resource_id=po.public_id,
            details={"status": po.status},
        )
        return Response(PurchaseOrderSerializer(po).data)





class PurchaseOrderCancelView(APIView):

    """POST /suppliers/purchase-orders/{id}/cancel/"""



    permission_classes = [CanManageSuppliers]



    def post(self, request, po_id):
        from apps.core.audit import log_operation
        from apps.core.models import OperationalAuditLog

        po = PurchaseOrderService.get_by_public_id(po_id)
        po = PurchaseOrderService.cancel(po=po)
        log_operation(
            user=request.user,
            module=OperationalAuditLog.Module.SUPPLIERS,
            action="po_cancel",
            resource_type="purchase_order",
            resource_id=po.public_id,
        )
        return Response(PurchaseOrderSerializer(po).data)

