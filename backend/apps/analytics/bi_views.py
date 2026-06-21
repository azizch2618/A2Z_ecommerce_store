"""Executive BI API views."""
from __future__ import annotations

from uuid import UUID

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.analytics.executive import (
    ExecutiveBiService,
    FinanceAnalyticsService,
    HrAnalyticsService,
    InventoryAnalyticsService,
    ProcurementAnalyticsService,
    SalesAnalyticsService,
)
from apps.analytics.export import export_report
from apps.analytics.kpi_engine import KpiEngineService
from apps.analytics.permissions import (
    CanExportReports,
    CanManageAnalytics,
    CanViewAnalytics,
    CanViewReports,
)
from apps.analytics.reports import REPORT_CATALOG, list_reports
from apps.analytics.scheduled_reports import ScheduledReportService
from apps.core.exceptions import NotFoundError


class ExecutiveDashboardView(APIView):
    permission_classes = [CanViewAnalytics]

    def get(self, request):
        return Response(ExecutiveBiService.get_snapshot())


class SalesAnalyticsView(APIView):
    permission_classes = [CanViewAnalytics]

    def get(self, request):
        return Response(SalesAnalyticsService.get_analytics())


class InventoryAnalyticsView(APIView):
    permission_classes = [CanViewAnalytics]

    def get(self, request):
        return Response(InventoryAnalyticsService.get_analytics())


class ProcurementAnalyticsView(APIView):
    permission_classes = [CanViewAnalytics]

    def get(self, request):
        return Response(ProcurementAnalyticsService.get_analytics())


class FinanceAnalyticsView(APIView):
    permission_classes = [CanViewAnalytics]

    def get(self, request):
        return Response(FinanceAnalyticsService.get_analytics())


class HrAnalyticsView(APIView):
    permission_classes = [CanViewAnalytics]

    def get(self, request):
        return Response(HrAnalyticsService.get_analytics())


class KpiDefinitionListView(APIView):
    permission_classes = [CanViewAnalytics]

    def get(self, request):
        KpiEngineService.ensure_defaults()
        category = request.query_params.get("category")
        defs = KpiEngineService.list_definitions(category=category)
        return Response(
            {
                "data": [
                    {
                        "id": str(d.public_id),
                        "code": d.code,
                        "name": d.name,
                        "description": d.description,
                        "category": d.category,
                        "metricKey": d.metric_key,
                        "unit": d.unit,
                        "targetValue": float(d.target_value) if d.target_value is not None else None,
                        "isActive": d.is_active,
                        "displayOrder": d.display_order,
                    }
                    for d in defs
                ]
            }
        )


class KpiEvaluateView(APIView):
    permission_classes = [CanViewAnalytics]

    def get(self, request):
        return Response({"data": KpiEngineService.evaluate_all()})


class KpiDefinitionUpdateView(APIView):
    permission_classes = [CanManageAnalytics]

    def patch(self, request, kpi_id: UUID):
        kpi = KpiEngineService.get_definition(kpi_id)
        kpi = KpiEngineService.update_definition(kpi=kpi, data=request.data)
        return Response(
            {
                "id": str(kpi.public_id),
                "code": kpi.code,
                "name": kpi.name,
                "targetValue": float(kpi.target_value) if kpi.target_value is not None else None,
                "isActive": kpi.is_active,
            }
        )


class BiReportCatalogView(APIView):
    permission_classes = [CanViewReports]

    def get(self, request):
        catalog = list_reports()
        for item in catalog:
            item["formats"] = ["csv", "excel", "pdf"]
        return Response({"data": catalog})


class BiReportExportView(APIView):
    permission_classes = [CanExportReports]

    def post(self, request):
        report_id = request.data.get("reportId", request.data.get("report_id", ""))
        export_format = request.data.get("format", "csv")
        try:
            payload = export_report(
                report_id=report_id,
                export_format=export_format,
                user=request.user,
            )
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        return Response(payload)


class ScheduledReportListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == "POST":
            return [CanManageAnalytics()]
        return [CanViewAnalytics()]

    def get(self, request):
        schedules = ScheduledReportService.list_schedules(user=request.user)
        return Response(
            {
                "data": [
                    {
                        "id": str(s.public_id),
                        "name": s.name,
                        "reportId": s.report_id,
                        "format": s.export_format,
                        "frequency": s.frequency,
                        "recipientEmails": s.recipient_emails,
                        "isActive": s.is_active,
                        "lastRunAt": s.last_run_at.isoformat() if s.last_run_at else None,
                        "nextRunAt": s.next_run_at.isoformat() if s.next_run_at else None,
                    }
                    for s in schedules
                ]
            }
        )

    def post(self, request):
        data = request.data
        schedule = ScheduledReportService.create(
            actor=request.user,
            name=data["name"],
            report_id=data["reportId"],
            export_format=data.get("format", "csv"),
            frequency=data.get("frequency", "weekly"),
            recipient_emails=data.get("recipientEmails", []),
        )
        return Response(
            {
                "id": str(schedule.public_id),
                "name": schedule.name,
                "nextRunAt": schedule.next_run_at.isoformat() if schedule.next_run_at else None,
            },
            status=status.HTTP_201_CREATED,
        )


class BiFullSnapshotView(APIView):
    """Single endpoint returning all analytics sections."""

    permission_classes = [CanViewAnalytics]

    def get(self, request):
        return Response(
            {
                "executive": ExecutiveBiService.get_snapshot(),
                "sales": SalesAnalyticsService.get_analytics(),
                "inventory": InventoryAnalyticsService.get_analytics(),
                "procurement": ProcurementAnalyticsService.get_analytics(),
                "finance": FinanceAnalyticsService.get_analytics(),
                "hr": HrAnalyticsService.get_analytics(),
                "kpis": KpiEngineService.evaluate_all(),
            }
        )
