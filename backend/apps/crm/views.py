"""CRM admin API views."""
from __future__ import annotations

from uuid import UUID

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import CanManageCrm, CanViewCrm
from apps.crm.constants import LeadStatus, OpportunityStatus
from apps.crm.serializers import (
    serialize_activity,
    serialize_lead,
    serialize_note,
    serialize_opportunity,
)
from apps.crm.services import (
    CrmActivityService,
    CrmDashboardService,
    CrmLeadService,
    CrmNoteService,
    CrmOpportunityService,
    CrmPipelineService,
    CrmTimelineService,
)


def _parse_uuid(value: str | None) -> UUID | None:
    if not value:
        return None
    return UUID(str(value))


class CrmDashboardView(APIView):
    permission_classes = [CanViewCrm]

    def get(self, request):
        assigned = request.query_params.get("assignedTo")
        assigned_uuid = _parse_uuid(assigned)
        kpis = CrmDashboardService.get_kpis(assigned_to_id=assigned_uuid)
        charts = CrmDashboardService.get_charts(assigned_to_id=assigned_uuid)
        return Response(
            {
                "totalLeads": kpis["total_leads"],
                "openOpportunities": kpis["open_opportunities"],
                "conversionRate": kpis["conversion_rate"],
                "revenueForecastCents": kpis["revenue_forecast_cents"],
                "leadsByStatus": kpis["leads_by_status"],
                "wonOpportunities": kpis["won_opportunities"],
                "lostOpportunities": kpis["lost_opportunities"],
                "charts": {
                    "pipelineValue": charts["pipeline_value"],
                    "forecastRevenue": charts["forecast_revenue"],
                    "winRate": charts["win_rate"],
                    "conversionRate": charts["conversion_rate"],
                },
            }
        )


class CrmLeadListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == "POST":
            return [CanManageCrm()]
        return [CanViewCrm()]

    def get(self, request):
        qs = CrmLeadService.list_leads(
            status=request.query_params.get("status"),
            assigned_to_id=_parse_uuid(request.query_params.get("assignedTo")),
            search=request.query_params.get("search"),
        )
        return Response({"data": [serialize_lead(lead) for lead in qs[:200]]})

    def post(self, request):
        data = request.data
        lead = CrmLeadService.create_lead(
            actor=request.user,
            data={
                "title": data.get("title", ""),
                "company_name": data.get("companyName", ""),
                "contact_name": data.get("contactName", ""),
                "contact_email": data.get("contactEmail", ""),
                "contact_phone": data.get("contactPhone", ""),
                "source": data.get("source", "website"),
                "status": data.get("status", LeadStatus.NEW),
                "assigned_to_id": data.get("assignedToId"),
                "party_id": data.get("partyId"),
                "notes_summary": data.get("notesSummary", ""),
            },
        )
        return Response(serialize_lead(lead), status=status.HTTP_201_CREATED)


class CrmLeadDetailView(APIView):
    def get_permissions(self):
        if self.request.method in ("PATCH", "PUT", "DELETE"):
            return [CanManageCrm()]
        return [CanViewCrm()]

    def get(self, request, lead_id):
        return Response(CrmLeadService.get_lead_detail(lead_id))

    def patch(self, request, lead_id):
        lead = CrmLeadService.get_lead(lead_id)
        data = request.data
        lead = CrmLeadService.update_lead(
            lead=lead,
            actor=request.user,
            data={
                k: v
                for k, v in {
                    "title": data.get("title"),
                    "company_name": data.get("companyName"),
                    "contact_name": data.get("contactName"),
                    "contact_email": data.get("contactEmail"),
                    "contact_phone": data.get("contactPhone"),
                    "source": data.get("source"),
                    "status": data.get("status"),
                    "assigned_to_id": data.get("assignedToId"),
                    "notes_summary": data.get("notesSummary"),
                }.items()
                if v is not None
            },
        )
        return Response(serialize_lead(lead))


class CrmLeadConvertView(APIView):
    permission_classes = [CanManageCrm]

    def post(self, request, lead_id):
        lead = CrmLeadService.get_lead(lead_id)
        opp = CrmOpportunityService.convert_lead(
            lead=lead,
            actor=request.user,
            data={
                "name": request.data.get("name"),
                "customer_id": request.data.get("customerId"),
                "trade_account_id": request.data.get("tradeAccountId"),
                "expected_revenue_cents": request.data.get("expectedRevenueCents", 0),
                "probability": request.data.get("probability", 25),
                "expected_close_date": request.data.get("expectedCloseDate"),
                "assigned_to_id": request.data.get("assignedToId"),
            },
        )
        return Response(serialize_opportunity(opp), status=status.HTTP_201_CREATED)


class CrmOpportunityListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == "POST":
            return [CanManageCrm()]
        return [CanViewCrm()]

    def get(self, request):
        qs = CrmOpportunityService.list_opportunities(
            status=request.query_params.get("status"),
            assigned_to_id=_parse_uuid(request.query_params.get("assignedTo")),
            search=request.query_params.get("search"),
        )
        return Response({"data": [serialize_opportunity(o) for o in qs[:200]]})

    def post(self, request):
        data = request.data
        opp = CrmOpportunityService.create_opportunity(
            actor=request.user,
            data={
                "name": data.get("name", ""),
                "party_id": data.get("partyId"),
                "lead_id": data.get("leadId"),
                "customer_id": data.get("customerId"),
                "trade_account_id": data.get("tradeAccountId"),
                "stage": data.get("stage", LeadStatus.QUALIFIED),
                "expected_revenue_cents": data.get("expectedRevenueCents", 0),
                "probability": data.get("probability", 0),
                "expected_close_date": data.get("expectedCloseDate"),
                "assigned_to_id": data.get("assignedToId"),
            },
        )
        return Response(serialize_opportunity(opp), status=status.HTTP_201_CREATED)


class CrmOpportunityDetailView(APIView):
    def get_permissions(self):
        if self.request.method in ("PATCH", "PUT"):
            return [CanManageCrm()]
        return [CanViewCrm()]

    def get(self, request, opportunity_id):
        return Response(CrmOpportunityService.get_opportunity_detail(opportunity_id))

    def patch(self, request, opportunity_id):
        opp = CrmOpportunityService.get_opportunity(opportunity_id)
        data = request.data
        payload = {}
        field_map = {
            "name": "name",
            "stage": "stage",
            "status": "status",
            "expectedRevenueCents": "expected_revenue_cents",
            "probability": "probability",
            "expectedCloseDate": "expected_close_date",
            "lostReason": "lost_reason",
            "assignedToId": "assigned_to_id",
        }
        for api_key, svc_key in field_map.items():
            if api_key in data:
                payload[svc_key] = data[api_key]
        opp = CrmOpportunityService.update_opportunity(
            opportunity=opp,
            actor=request.user,
            data=payload,
        )
        return Response(serialize_opportunity(opp))


class CrmActivityListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == "POST":
            return [CanManageCrm()]
        return [CanViewCrm()]

    def get(self, request):
        qs = CrmActivityService.list_activities(
            lead_id=_parse_uuid(request.query_params.get("leadId")),
            opportunity_id=_parse_uuid(request.query_params.get("opportunityId")),
            party_id=_parse_uuid(request.query_params.get("partyId")),
        )
        return Response({"data": [serialize_activity(a) for a in qs[:100]]})

    def post(self, request):
        data = request.data
        activity = CrmActivityService.create_activity(
            actor=request.user,
            data={
                "activity_type": data.get("activityType"),
                "subject": data.get("subject", ""),
                "description": data.get("description", ""),
                "scheduled_at": data.get("scheduledAt"),
                "completed_at": data.get("completedAt"),
                "lead_id": data.get("leadId"),
                "opportunity_id": data.get("opportunityId"),
                "party_id": data.get("partyId"),
                "assigned_to_id": data.get("assignedToId"),
            },
        )
        return Response(serialize_activity(activity), status=status.HTTP_201_CREATED)


class CrmNoteListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == "POST":
            return [CanManageCrm()]
        return [CanViewCrm()]

    def get(self, request):
        from apps.crm.models import CrmNote

        qs = CrmNote.objects.select_related("created_by", "lead", "opportunity")
        if request.query_params.get("leadId"):
            qs = qs.filter(lead__public_id=request.query_params["leadId"])
        if request.query_params.get("opportunityId"):
            qs = qs.filter(opportunity__public_id=request.query_params["opportunityId"])
        return Response({"data": [serialize_note(n) for n in qs.order_by("-created_at")[:100]]})

    def post(self, request):
        note = CrmNoteService.create_note(
            actor=request.user,
            data={
                "body": request.data.get("body", ""),
                "lead_id": request.data.get("leadId"),
                "opportunity_id": request.data.get("opportunityId"),
            },
        )
        return Response(serialize_note(note), status=status.HTTP_201_CREATED)


class CrmTimelineView(APIView):
    permission_classes = [CanViewCrm]

    def get(self, request):
        entries = CrmTimelineService.get_feed(
            lead_id=_parse_uuid(request.query_params.get("leadId")),
            opportunity_id=_parse_uuid(request.query_params.get("opportunityId")),
            party_id=_parse_uuid(request.query_params.get("partyId")),
            customer_id=_parse_uuid(request.query_params.get("customerId")),
            limit=int(request.query_params.get("limit", 50)),
        )
        return Response({"data": entries})


class CrmMetaView(APIView):
    permission_classes = [CanViewCrm]

    def get(self, request):
        from apps.crm.constants import ActivityType, LeadSource, LeadStatus

        return Response(
            {
                "leadStatuses": [{"value": c.value, "label": c.label} for c in LeadStatus],
                "leadSources": [{"value": c.value, "label": c.label} for c in LeadSource],
                "opportunityStatuses": [
                    {"value": c.value, "label": c.label} for c in OpportunityStatus
                ],
                "activityTypes": [{"value": c.value, "label": c.label} for c in ActivityType],
            }
        )


class CrmPipelineView(APIView):
    def get_permissions(self):
        if self.request.method == "PATCH":
            return [CanManageCrm()]
        return [CanViewCrm()]

    def get(self, request):
        columns = CrmPipelineService.get_pipeline(
            assigned_to_id=_parse_uuid(request.query_params.get("assignedTo")),
        )
        return Response({"columns": columns})

    def patch(self, request):
        lead_id = request.data.get("leadId")
        new_status = request.data.get("status")
        if not lead_id or not new_status:
            return Response(
                {"detail": "leadId and status are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        lead = CrmLeadService.get_lead(lead_id)
        lead = CrmPipelineService.move_lead(
            lead=lead,
            new_status=new_status,
            actor=request.user,
        )
        return Response(serialize_lead(lead))
