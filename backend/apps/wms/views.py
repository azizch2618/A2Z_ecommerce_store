"""WMS API views."""
from __future__ import annotations

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.exceptions import NotFoundError
from apps.orders.models import Order
from apps.wms.permissions import CanApproveWms, CanExecuteWms, CanManageWms, CanViewWms
from apps.wms.serializers import (
    serialize_adjustment,
    serialize_bin,
    serialize_bin_inventory,
    serialize_cycle_count,
    serialize_pick_list,
    serialize_putaway_task,
    serialize_transfer,
    serialize_zone,
)
from apps.wms.services import (
    AdjustmentService,
    BinInventoryService,
    BinLocationService,
    CycleCountService,
    PickListService,
    PutawayService,
    StockTransferService,
    WmsDashboardService,
)


class WmsDashboardView(APIView):
    permission_classes = [CanViewWms]

    def get(self, request):
        kpis = WmsDashboardService.get_kpis()
        return Response(
            {
                "inventoryValueCents": kpis["inventory_value_cents"],
                "openTransfers": kpis["open_transfers"],
                "openPicks": kpis["open_picks"],
                "cycleCountAccuracyPct": kpis["cycle_count_accuracy_pct"],
            }
        )


class ZoneListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == "POST":
            return [CanManageWms()]
        return [CanViewWms()]

    def get(self, request):
        qs = BinLocationService.list_zones(
            warehouse_code=request.query_params.get("warehouseCode")
        )
        return Response({"data": [serialize_zone(z) for z in qs]})

    def post(self, request):
        zone = BinLocationService.create_zone(
            warehouse_code=request.data.get("warehouseCode", "SYD1"),
            code=request.data.get("code", ""),
            name=request.data.get("name", ""),
        )
        return Response(serialize_zone(zone), status=status.HTTP_201_CREATED)


class BinListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == "POST":
            return [CanManageWms()]
        return [CanViewWms()]

    def get(self, request):
        qs = BinLocationService.list_bins(
            warehouse_code=request.query_params.get("warehouseCode"),
            search=request.query_params.get("search"),
        )
        return Response({"data": [serialize_bin(b) for b in qs[:500]]})

    def post(self, request):
        data = request.data
        bin_obj = BinLocationService.create_bin_hierarchy(
            warehouse_code=data.get("warehouseCode", "SYD1"),
            zone_code=data.get("zoneCode", "Z1"),
            zone_name=data.get("zoneName", "Zone 1"),
            aisle_code=data.get("aisleCode", "A1"),
            aisle_name=data.get("aisleName", "Aisle 1"),
            bin_code=data.get("binCode", ""),
            bin_name=data.get("binName", ""),
            bin_type=data.get("binType", "pick"),
        )
        return Response(serialize_bin(bin_obj), status=status.HTTP_201_CREATED)


class BinInventoryListView(APIView):
    permission_classes = [CanViewWms]

    def get(self, request):
        qs = BinInventoryService.list_bin_inventory(
            warehouse_code=request.query_params.get("warehouseCode"),
            sku=request.query_params.get("sku"),
        )
        return Response({"data": [serialize_bin_inventory(r) for r in qs[:500]]})


class StockTransferListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == "POST":
            return [CanManageWms()]
        return [CanViewWms()]

    def get(self, request):
        qs = StockTransferService.list_transfers(status=request.query_params.get("status"))
        return Response({"data": [serialize_transfer(t) for t in qs[:200]]})

    def post(self, request):
        data = request.data
        tr = StockTransferService.create(
            actor=request.user,
            transfer_type=data.get("transferType", "warehouse"),
            from_warehouse_code=data.get("fromWarehouseCode", "SYD1"),
            to_warehouse_code=data.get("toWarehouseCode", "SYD1"),
            from_bin_id=data.get("fromBinId"),
            to_bin_id=data.get("toBinId"),
            requires_approval=data.get("requiresApproval", False),
            notes=data.get("notes", ""),
        )
        return Response(serialize_transfer(tr), status=status.HTTP_201_CREATED)


class StockTransferDetailView(APIView):
    permission_classes = [CanViewWms]

    def get(self, request, transfer_id):
        return Response(serialize_transfer(StockTransferService.get_transfer(transfer_id)))


class StockTransferLineCreateView(APIView):
    permission_classes = [CanManageWms]

    def post(self, request, transfer_id):
        tr = StockTransferService.get_transfer(transfer_id)
        StockTransferService.add_line(
            transfer=tr,
            sku=request.data.get("sku"),
            quantity=int(request.data.get("quantity", 1)),
        )
        tr.refresh_from_db()
        return Response(serialize_transfer(tr), status=status.HTTP_201_CREATED)


class StockTransferSubmitView(APIView):
    permission_classes = [CanManageWms]

    def post(self, request, transfer_id):
        tr = StockTransferService.submit(
            transfer=StockTransferService.get_transfer(transfer_id), actor=request.user
        )
        return Response(serialize_transfer(tr))


class StockTransferApproveView(APIView):
    permission_classes = [CanApproveWms]

    def post(self, request, transfer_id):
        tr = StockTransferService.approve(
            transfer=StockTransferService.get_transfer(transfer_id),
            actor=request.user,
            comment=request.data.get("comment", ""),
        )
        return Response(serialize_transfer(tr))


class PickListListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == "POST":
            return [CanManageWms()]
        return [CanViewWms()]

    def get(self, request):
        qs = PickListService.list_picks(status=request.query_params.get("status"))
        return Response({"data": [serialize_pick_list(p) for p in qs[:200]]})

    def post(self, request):
        order_id = request.data.get("orderId")
        order = Order.objects.filter(public_id=order_id).first()
        if not order:
            raise NotFoundError("Order not found.")
        pick = PickListService.create_for_order(
            order=order,
            warehouse_code=request.data.get("warehouseCode", "SYD1"),
            actor=request.user,
        )
        return Response(serialize_pick_list(pick), status=status.HTTP_201_CREATED)


class PickListDetailView(APIView):
    permission_classes = [CanViewWms]

    def get(self, request, pick_id):
        return Response(serialize_pick_list(PickListService.get_pick(pick_id)))


class PickListAssignView(APIView):
    permission_classes = [CanManageWms]

    def post(self, request, pick_id):
        from apps.accounts.models import User

        user_id = request.data.get("userId")
        user = User.objects.filter(public_id=user_id).first()
        if not user:
            raise NotFoundError("User not found.")
        pick = PickListService.assign(
            pick=PickListService.get_pick(pick_id), user=user, actor=request.user
        )
        return Response(serialize_pick_list(pick))


class PickListStartView(APIView):
    permission_classes = [CanExecuteWms]

    def post(self, request, pick_id):
        pick = PickListService.start_picking(
            pick=PickListService.get_pick(pick_id), actor=request.user
        )
        return Response(serialize_pick_list(pick))


class PickListRecordView(APIView):
    permission_classes = [CanExecuteWms]

    def post(self, request, pick_id):
        pick = PickListService.get_pick(pick_id)
        PickListService.record_pick(
            pick=pick,
            line_id=request.data.get("lineId"),
            quantity=int(request.data.get("quantity", 1)),
            from_bin_id=request.data.get("fromBinId"),
            actor=request.user,
        )
        pick.refresh_from_db()
        return Response(serialize_pick_list(pick))


class PickListCompleteView(APIView):
    permission_classes = [CanExecuteWms]

    def post(self, request, pick_id):
        pick = PickListService.complete(
            pick=PickListService.get_pick(pick_id), actor=request.user
        )
        return Response(serialize_pick_list(pick))


class PutawayTaskListView(APIView):
    permission_classes = [CanViewWms]

    def get(self, request):
        qs = PutawayService.list_tasks(status=request.query_params.get("status"))
        return Response({"data": [serialize_putaway_task(t) for t in qs[:200]]})


class PutawayTaskDetailView(APIView):
    permission_classes = [CanViewWms]

    def get(self, request, task_id):
        return Response(serialize_putaway_task(PutawayService.get_task(task_id)))


class PutawayAssignBinView(APIView):
    permission_classes = [CanExecuteWms]

    def post(self, request, task_id):
        task = PutawayService.get_task(task_id)
        PutawayService.assign_bin(
            task=task,
            line_id=request.data.get("lineId"),
            target_bin_id=request.data.get("targetBinId"),
            quantity=int(request.data.get("quantity", 1)),
            actor=request.user,
        )
        task.refresh_from_db()
        return Response(serialize_putaway_task(task))


class CycleCountListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == "POST":
            return [CanManageWms()]
        return [CanViewWms()]

    def get(self, request):
        qs = CycleCountService.list_counts(status=request.query_params.get("status"))
        return Response({"data": [serialize_cycle_count(c) for c in qs[:200]]})

    def post(self, request):
        cc = CycleCountService.create(
            warehouse_code=request.data.get("warehouseCode", "SYD1"),
            actor=request.user,
        )
        return Response(serialize_cycle_count(cc), status=status.HTTP_201_CREATED)


class CycleCountDetailView(APIView):
    permission_classes = [CanViewWms]

    def get(self, request, count_id):
        return Response(serialize_cycle_count(CycleCountService.get_count(count_id)))


class CycleCountLineCreateView(APIView):
    permission_classes = [CanManageWms]

    def post(self, request, count_id):
        cc = CycleCountService.get_count(count_id)
        CycleCountService.add_line(
            cc=cc,
            sku=request.data.get("sku"),
            bin_id=request.data.get("binId"),
        )
        cc.refresh_from_db()
        return Response(serialize_cycle_count(cc), status=status.HTTP_201_CREATED)


class CycleCountRecordView(APIView):
    permission_classes = [CanExecuteWms]

    def post(self, request, count_id):
        cc = CycleCountService.get_count(count_id)
        CycleCountService.record_count(
            cc=cc,
            line_id=request.data.get("lineId"),
            counted_qty=int(request.data.get("countedQty", 0)),
            actor=request.user,
        )
        cc.refresh_from_db()
        return Response(serialize_cycle_count(cc))


class CycleCountCompleteView(APIView):
    permission_classes = [CanApproveWms]

    def post(self, request, count_id):
        cc = CycleCountService.complete(
            cc=CycleCountService.get_count(count_id), actor=request.user
        )
        return Response(serialize_cycle_count(cc))


class AdjustmentListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == "POST":
            return [CanManageWms()]
        return [CanViewWms()]

    def get(self, request):
        qs = AdjustmentService.list_requests(status=request.query_params.get("status"))
        return Response({"data": [serialize_adjustment(r) for r in qs[:200]]})

    def post(self, request):
        req = AdjustmentService.create(
            warehouse_code=request.data.get("warehouseCode", "SYD1"),
            reason=request.data.get("reason", ""),
            actor=request.user,
        )
        return Response(serialize_adjustment(req), status=status.HTTP_201_CREATED)


class AdjustmentDetailView(APIView):
    permission_classes = [CanViewWms]

    def get(self, request, adjustment_id):
        return Response(serialize_adjustment(AdjustmentService.get_request(adjustment_id)))


class AdjustmentLineCreateView(APIView):
    permission_classes = [CanManageWms]

    def post(self, request, adjustment_id):
        req = AdjustmentService.get_request(adjustment_id)
        AdjustmentService.add_line(
            req=req,
            sku=request.data.get("sku"),
            quantity_change=int(request.data.get("quantityChange", 0)),
            unit_cost_cents=int(request.data.get("unitCostCents", 0)),
            bin_id=request.data.get("binId"),
        )
        req.refresh_from_db()
        return Response(serialize_adjustment(req), status=status.HTTP_201_CREATED)


class AdjustmentSubmitView(APIView):
    permission_classes = [CanManageWms]

    def post(self, request, adjustment_id):
        req = AdjustmentService.submit(
            req=AdjustmentService.get_request(adjustment_id), actor=request.user
        )
        return Response(serialize_adjustment(req))


class AdjustmentApproveView(APIView):
    permission_classes = [CanApproveWms]

    def post(self, request, adjustment_id):
        req = AdjustmentService.approve(
            req=AdjustmentService.get_request(adjustment_id),
            actor=request.user,
            comment=request.data.get("comment", ""),
        )
        return Response(serialize_adjustment(req))


class AdjustmentRejectView(APIView):
    permission_classes = [CanApproveWms]

    def post(self, request, adjustment_id):
        req = AdjustmentService.reject(
            req=AdjustmentService.get_request(adjustment_id),
            actor=request.user,
            comment=request.data.get("comment", ""),
        )
        return Response(serialize_adjustment(req))
