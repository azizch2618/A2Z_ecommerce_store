"""Accounting foundation API views."""
from __future__ import annotations

from uuid import UUID

from django.utils.dateparse import parse_date
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounting.models import AccountingAuditLog, AccountingPeriod
from apps.accounting.permissions import CanManageAccounting, CanPostAccounting, CanViewAccounting
from apps.accounting.serializers import (
    serialize_account,
    serialize_audit_log,
    serialize_event_mapping,
    serialize_fiscal_year,
    serialize_journal_entry,
    serialize_period,
)
from apps.accounting.services import (
    ChartOfAccountService,
    FiscalPeriodService,
    JournalEngine,
    ReportingService,
)
from apps.accounting.tax import TaxEngine
from apps.core.exceptions import NotFoundError
from apps.erp.models import CostCenter, Department


class ChartOfAccountListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == "POST":
            return [CanManageAccounting()]
        return [CanViewAccounting()]

    def get(self, request):
        account_type = request.query_params.get("accountType")
        qs = ChartOfAccountService.list_accounts(account_type=account_type)
        return Response({"data": [serialize_account(a) for a in qs]})

    def post(self, request):
        data = request.data
        account = ChartOfAccountService.create(
            company=None,
            code=data["code"],
            name=data["name"],
            account_type=data["accountType"],
            parent_code=data.get("parentCode"),
            actor=request.user,
        )
        return Response(serialize_account(account), status=status.HTTP_201_CREATED)


class ChartOfAccountDetailView(APIView):
    permission_classes = [CanViewAccounting]

    def get(self, request, account_id: UUID):
        account = ChartOfAccountService.get_account(account_id)
        return Response(serialize_account(account))


class FiscalYearListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == "POST":
            return [CanPostAccounting()]
        return [CanViewAccounting()]

    def get(self, request):
        qs = FiscalPeriodService.list_fiscal_years()
        return Response({"data": [serialize_fiscal_year(fy) for fy in qs]})

    def post(self, request):
        data = request.data
        start = parse_date(data.get("startDate", ""))
        if not start:
            return Response({"detail": "startDate is required."}, status=status.HTTP_400_BAD_REQUEST)
        fy = FiscalPeriodService.create_fiscal_year(
            year_label=data.get("label", str(start.year)),
            start_date=start,
            actor=request.user,
        )
        return Response(serialize_fiscal_year(fy), status=status.HTTP_201_CREATED)


class AccountingPeriodCloseView(APIView):
    permission_classes = [CanPostAccounting]

    def post(self, request, period_id: UUID):
        period = AccountingPeriod.objects.filter(public_id=period_id).select_related("fiscal_year").first()
        if not period:
            raise NotFoundError("Period not found.")
        period = FiscalPeriodService.close_period(period=period, actor=request.user)
        return Response(serialize_period(period))


class AccountingPeriodReopenView(APIView):
    permission_classes = [CanPostAccounting]

    def post(self, request, period_id: UUID):
        period = AccountingPeriod.objects.filter(public_id=period_id).select_related("fiscal_year").first()
        if not period:
            raise NotFoundError("Period not found.")
        period = FiscalPeriodService.reopen_period(period=period, actor=request.user)
        return Response(serialize_period(period))


class JournalEntryListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == "POST":
            return [CanManageAccounting()]
        return [CanViewAccounting()]

    def get(self, request):
        qs = JournalEngine.list_entries(status=request.query_params.get("status"))
        return Response({"data": [serialize_journal_entry(e) for e in qs[:200]]})

    def post(self, request):
        data = request.data
        entry_date = parse_date(data.get("entryDate", "")) if data.get("entryDate") else None
        department = None
        cost_center = None
        if data.get("departmentId"):
            department = Department.objects.filter(public_id=data["departmentId"]).first()
        if data.get("costCenterId"):
            cost_center = CostCenter.objects.filter(public_id=data["costCenterId"]).first()

        entry = JournalEngine.create_draft(
            entry_date=entry_date,
            description=data.get("description", ""),
            department=department,
            cost_center=cost_center,
            actor=request.user,
        )
        return Response(serialize_journal_entry(entry), status=status.HTTP_201_CREATED)


class JournalEntryDetailView(APIView):
    permission_classes = [CanViewAccounting]

    def get(self, request, entry_id: UUID):
        entry = JournalEngine.get_entry(entry_id)
        return Response(serialize_journal_entry(entry))


class JournalLineCreateView(APIView):
    permission_classes = [CanManageAccounting]

    def post(self, request, entry_id: UUID):
        entry = JournalEngine.get_entry(entry_id)
        data = request.data
        account = ChartOfAccountService.get_account(data["accountId"])
        line = JournalEngine.add_line(
            entry=entry,
            account=account,
            side=data["side"],
            amount_cents=int(data["amountCents"]),
            gst_cents=int(data.get("gstCents", 0)),
            description=data.get("description", ""),
        )
        entry = JournalEngine.get_entry(entry_id)
        return Response(serialize_journal_entry(entry), status=status.HTTP_201_CREATED)


class JournalEntryPostView(APIView):
    permission_classes = [CanPostAccounting]

    def post(self, request, entry_id: UUID):
        entry = JournalEngine.get_entry(entry_id)
        entry = JournalEngine.post(entry=entry, actor=request.user)
        return Response(serialize_journal_entry(entry))


class EventMappingListView(APIView):
    permission_classes = [CanViewAccounting]

    def get(self, request):
        from apps.accounting.models import AccountingEventMapping

        qs = AccountingEventMapping.objects.prefetch_related("lines").order_by("event_type")
        return Response({"data": [serialize_event_mapping(m) for m in qs]})


class TaxCalculateView(APIView):
    permission_classes = [CanViewAccounting]

    def post(self, request):
        data = request.data
        amount = int(data.get("amountCents", 0))
        treatment = data.get("taxTreatment", "gst_exclusive")
        result = TaxEngine.normalize(amount_cents=amount, treatment=treatment)
        return Response(
            {
                "amountExGstCents": result["amount_ex_gst_cents"],
                "gstCents": result["gst_cents"],
                "amountIncGstCents": result["amount_inc_gst_cents"],
                "gstRate": TaxEngine.gst_rate_display(),
                "currencyCode": TaxEngine.currency_code(),
            }
        )


class TrialBalanceReportView(APIView):
    permission_classes = [CanViewAccounting]

    def get(self, request):
        period_id = request.query_params.get("periodId")
        pid = UUID(period_id) if period_id else None
        rows = ReportingService.trial_balance(period_id=pid)
        return Response({"data": rows})


class GeneralLedgerReportView(APIView):
    permission_classes = [CanViewAccounting]

    def get(self, request):
        account_code = request.query_params.get("accountCode")
        rows = ReportingService.general_ledger(account_code=account_code)
        return Response({"data": rows})


class GstSummaryReportView(APIView):
    permission_classes = [CanViewAccounting]

    def get(self, request):
        period_id = request.query_params.get("periodId")
        pid = UUID(period_id) if period_id else None
        return Response(ReportingService.gst_summary(period_id=pid))


class AccountingAuditLogListView(APIView):
    permission_classes = [CanViewAccounting]

    def get(self, request):
        qs = AccountingAuditLog.objects.select_related("user").order_by("-created_at")[:200]
        return Response({"data": [serialize_audit_log(log) for log in qs]})
