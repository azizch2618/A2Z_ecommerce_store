from django.urls import path
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import CanExportReports, CanViewReports
from apps.analytics.admin_views import (
    AdminCustomerListView,
    AdminProductListView,
    DashboardView,
)
from apps.analytics.reports import export_report_csv, list_reports
from apps.analytics.views import EventCreateView

app_name = "analytics"


class ReportCatalogView(APIView):
    permission_classes = [CanViewReports]

    def get(self, request):
        return Response({"data": list_reports()})


class ReportExportView(APIView):
    permission_classes = [CanExportReports]

    def post(self, request):
        report_id = request.data.get("report_id", "")
        export_format = request.data.get("format", "csv")
        if export_format not in {"csv", "excel", "pdf"}:
            return Response({"format": ["Unsupported format."]}, status=400)
        try:
            filename, content = export_report_csv(report_id=report_id, user=request.user)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=404)
        return Response(
            {
                "filename": filename,
                "content": content,
                "mime_type": "text/csv",
            }
        )


urlpatterns = [
    path("events/", EventCreateView.as_view(), name="event-create"),
    path("admin/dashboard/", DashboardView.as_view(), name="admin-dashboard"),
    path("admin/customers/", AdminCustomerListView.as_view(), name="admin-customers"),
    path("admin/products/", AdminProductListView.as_view(), name="admin-products"),
    path("admin/reports/", ReportCatalogView.as_view(), name="admin-reports"),
    path("admin/reports/export/", ReportExportView.as_view(), name="admin-reports-export"),
]