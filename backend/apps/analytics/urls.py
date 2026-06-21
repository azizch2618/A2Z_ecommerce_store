from django.urls import path
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import CanExportReports, CanViewReports
from apps.analytics.admin_views import (
    AdminCustomerListView,
    AdminProductListView,
    DashboardView,
)
from apps.analytics.bi_views import (
    BiFullSnapshotView,
    BiReportCatalogView,
    BiReportExportView,
    ExecutiveDashboardView,
    FinanceAnalyticsView,
    HrAnalyticsView,
    InventoryAnalyticsView,
    KpiDefinitionListView,
    KpiDefinitionUpdateView,
    KpiEvaluateView,
    ProcurementAnalyticsView,
    SalesAnalyticsView,
    ScheduledReportListCreateView,
)
from apps.analytics.export import export_report
from apps.analytics.reports import list_reports
from apps.analytics.views import EventCreateView

app_name = "analytics"


class ReportCatalogView(APIView):
    permission_classes = [CanViewReports]

    def get(self, request):
        return Response({"data": list_reports()})


class ReportExportView(APIView):
    permission_classes = [CanExportReports]

    def post(self, request):
        report_id = request.data.get("report_id", request.data.get("reportId", ""))
        export_format = request.data.get("format", "csv")
        try:
            payload = export_report(
                report_id=report_id,
                export_format=export_format,
                user=request.user,
            )
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=400)
        return Response(payload)


urlpatterns = [
    path("events/", EventCreateView.as_view(), name="event-create"),
    path("admin/dashboard/", DashboardView.as_view(), name="admin-dashboard"),
    path("admin/customers/", AdminCustomerListView.as_view(), name="admin-customers"),
    path("admin/products/", AdminProductListView.as_view(), name="admin-products"),
    path("admin/reports/", ReportCatalogView.as_view(), name="admin-reports"),
    path("admin/reports/export/", ReportExportView.as_view(), name="admin-reports-export"),
    path("admin/bi/executive/", ExecutiveDashboardView.as_view(), name="bi-executive"),
    path("admin/bi/sales/", SalesAnalyticsView.as_view(), name="bi-sales"),
    path("admin/bi/inventory/", InventoryAnalyticsView.as_view(), name="bi-inventory"),
    path("admin/bi/procurement/", ProcurementAnalyticsView.as_view(), name="bi-procurement"),
    path("admin/bi/finance/", FinanceAnalyticsView.as_view(), name="bi-finance"),
    path("admin/bi/hr/", HrAnalyticsView.as_view(), name="bi-hr"),
    path("admin/bi/snapshot/", BiFullSnapshotView.as_view(), name="bi-snapshot"),
    path("admin/bi/kpis/", KpiDefinitionListView.as_view(), name="bi-kpis"),
    path("admin/bi/kpis/evaluate/", KpiEvaluateView.as_view(), name="bi-kpis-evaluate"),
    path("admin/bi/kpis/<uuid:kpi_id>/", KpiDefinitionUpdateView.as_view(), name="bi-kpi-update"),
    path("admin/bi/reports/", BiReportCatalogView.as_view(), name="bi-reports"),
    path("admin/bi/reports/export/", BiReportExportView.as_view(), name="bi-reports-export"),
    path("admin/bi/schedules/", ScheduledReportListCreateView.as_view(), name="bi-schedules"),
]