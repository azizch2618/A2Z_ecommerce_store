"""WMS URL routing."""
from django.urls import path

from apps.wms import views

urlpatterns = [
    path("admin/dashboard/", views.WmsDashboardView.as_view(), name="wms-dashboard"),
    path("admin/zones/", views.ZoneListCreateView.as_view(), name="wms-zones"),
    path("admin/bins/", views.BinListCreateView.as_view(), name="wms-bins"),
    path("admin/bin-inventory/", views.BinInventoryListView.as_view(), name="wms-bin-inventory"),
    path("admin/transfers/", views.StockTransferListCreateView.as_view(), name="wms-transfers"),
    path("admin/transfers/<uuid:transfer_id>/", views.StockTransferDetailView.as_view(), name="wms-transfer-detail"),
    path("admin/transfers/<uuid:transfer_id>/lines/", views.StockTransferLineCreateView.as_view(), name="wms-transfer-lines"),
    path("admin/transfers/<uuid:transfer_id>/submit/", views.StockTransferSubmitView.as_view(), name="wms-transfer-submit"),
    path("admin/transfers/<uuid:transfer_id>/approve/", views.StockTransferApproveView.as_view(), name="wms-transfer-approve"),
    path("admin/picks/", views.PickListListCreateView.as_view(), name="wms-picks"),
    path("admin/picks/<uuid:pick_id>/", views.PickListDetailView.as_view(), name="wms-pick-detail"),
    path("admin/picks/<uuid:pick_id>/assign/", views.PickListAssignView.as_view(), name="wms-pick-assign"),
    path("admin/picks/<uuid:pick_id>/start/", views.PickListStartView.as_view(), name="wms-pick-start"),
    path("admin/picks/<uuid:pick_id>/record/", views.PickListRecordView.as_view(), name="wms-pick-record"),
    path("admin/picks/<uuid:pick_id>/complete/", views.PickListCompleteView.as_view(), name="wms-pick-complete"),
    path("admin/putaway/", views.PutawayTaskListView.as_view(), name="wms-putaway-list"),
    path("admin/putaway/<uuid:task_id>/", views.PutawayTaskDetailView.as_view(), name="wms-putaway-detail"),
    path("admin/putaway/<uuid:task_id>/assign-bin/", views.PutawayAssignBinView.as_view(), name="wms-putaway-assign"),
    path("admin/cycle-counts/", views.CycleCountListCreateView.as_view(), name="wms-cycle-counts"),
    path("admin/cycle-counts/<uuid:count_id>/", views.CycleCountDetailView.as_view(), name="wms-cycle-count-detail"),
    path("admin/cycle-counts/<uuid:count_id>/lines/", views.CycleCountLineCreateView.as_view(), name="wms-cycle-count-lines"),
    path("admin/cycle-counts/<uuid:count_id>/record/", views.CycleCountRecordView.as_view(), name="wms-cycle-count-record"),
    path("admin/cycle-counts/<uuid:count_id>/complete/", views.CycleCountCompleteView.as_view(), name="wms-cycle-count-complete"),
    path("admin/adjustments/", views.AdjustmentListCreateView.as_view(), name="wms-adjustments"),
    path("admin/adjustments/<uuid:adjustment_id>/", views.AdjustmentDetailView.as_view(), name="wms-adjustment-detail"),
    path("admin/adjustments/<uuid:adjustment_id>/lines/", views.AdjustmentLineCreateView.as_view(), name="wms-adjustment-lines"),
    path("admin/adjustments/<uuid:adjustment_id>/submit/", views.AdjustmentSubmitView.as_view(), name="wms-adjustment-submit"),
    path("admin/adjustments/<uuid:adjustment_id>/approve/", views.AdjustmentApproveView.as_view(), name="wms-adjustment-approve"),
    path("admin/adjustments/<uuid:adjustment_id>/reject/", views.AdjustmentRejectView.as_view(), name="wms-adjustment-reject"),
]
