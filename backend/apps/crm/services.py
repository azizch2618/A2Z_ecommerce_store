"""CRM business logic."""
from __future__ import annotations

from datetime import date
from typing import Any
from uuid import UUID

from django.db import transaction
from django.db.models import Count, Q, QuerySet, Sum
from django.utils import timezone

from apps.core.exceptions import BusinessRuleError, NotFoundError
from apps.crm.constants import (
    ActivityType,
    LeadStatus,
    OpportunityStatus,
    TimelineEntryType,
)
from apps.crm.models import CrmActivity, CrmLead, CrmNote, CrmOpportunity
from apps.customers.models import Customer
from apps.erp.constants import AuditModule, DomainEventType
from apps.erp.constants import WorkflowCode as ErpWorkflowCode
from apps.erp.constants import PartyType
from apps.erp.services.audit import AuditService
from apps.erp.services.events import DomainEventPublisher
from apps.erp.services.notifications import NotificationService
from apps.erp.services.party import PartyService
from apps.erp.services.workflow import WorkflowEngine
from apps.accounts.models import User
from apps.trade_accounts.models import TradeAccount


def _resolve_user_id(public_id: UUID | str | None) -> int | None:
    if not public_id:
        return None
    user = User.objects.filter(public_id=public_id).first()
    if not user:
        raise NotFoundError("User not found.")
    return user.id


class CrmLeadService:
    @staticmethod
    def list_leads(
        *,
        status: str | None = None,
        assigned_to_id: UUID | None = None,
        search: str | None = None,
    ) -> QuerySet[CrmLead]:
        qs = CrmLead.objects.filter(deleted_at__isnull=True).select_related(
            "party", "assigned_to", "customer"
        )
        if status:
            qs = qs.filter(status=status)
        if assigned_to_id:
            qs = qs.filter(assigned_to__public_id=assigned_to_id)
        if search:
            qs = qs.filter(
                Q(title__icontains=search)
                | Q(company_name__icontains=search)
                | Q(contact_name__icontains=search)
                | Q(contact_email__icontains=search)
            )
        return qs.order_by("-created_at")

    @staticmethod
    def get_lead(public_id: UUID) -> CrmLead:
        lead = (
            CrmLead.objects.filter(deleted_at__isnull=True, public_id=public_id)
            .select_related("party", "assigned_to", "customer")
            .first()
        )
        if not lead:
            raise NotFoundError("Lead not found.")
        return lead

    @staticmethod
    def get_lead_detail(public_id: UUID) -> dict:
        lead = CrmLeadService.get_lead(public_id)
        opportunities = CrmOpportunity.objects.filter(
            lead=lead, deleted_at__isnull=True
        ).select_related("party", "assigned_to", "customer", "trade_account")
        activities = CrmActivity.objects.filter(lead=lead).select_related(
            "assigned_to", "created_by"
        ).order_by("-created_at")[:50]
        notes = CrmNote.objects.filter(lead=lead).select_related("created_by").order_by("-created_at")[:50]
        from apps.crm.serializers import serialize_lead_detail

        return serialize_lead_detail(
            lead,
            opportunities=opportunities,
            activities=activities,
            notes=notes,
        )

    @classmethod
    @transaction.atomic
    def create_lead(cls, *, actor, data: dict[str, Any]) -> CrmLead:
        party = cls._ensure_party_for_lead(data)
        lead = CrmLead.objects.create(
            party=party,
            title=data["title"],
            company_name=data.get("company_name", ""),
            contact_name=data.get("contact_name", ""),
            contact_email=data.get("contact_email", ""),
            contact_phone=data.get("contact_phone", ""),
            source=data.get("source", "website"),
            status=data.get("status", LeadStatus.NEW),
            assigned_to_id=_resolve_user_id(data.get("assigned_to_id")),
            notes_summary=data.get("notes_summary", ""),
            metadata=data.get("metadata") or {},
        )
        if lead.assigned_to_id:
            cls._notify_assignment(lead, actor)
        AuditService.log(
            user=actor,
            module=AuditModule.CRM,
            action="create",
            resource_type="crm_lead",
            resource_id=str(lead.public_id),
            summary=f"Lead created: {lead.title}",
        )
        return lead

    @classmethod
    @transaction.atomic
    def update_lead(cls, *, lead: CrmLead, actor, data: dict[str, Any]) -> CrmLead:
        old_status = lead.status
        old_assignee = lead.assigned_to_id

        for field in (
            "title",
            "company_name",
            "contact_name",
            "contact_email",
            "contact_phone",
            "source",
            "status",
            "notes_summary",
        ):
            if field in data:
                setattr(lead, field, data[field])
        if "assigned_to_id" in data:
            lead.assigned_to_id = _resolve_user_id(data["assigned_to_id"])
        if "metadata" in data:
            lead.metadata = data["metadata"]
        lead.save()

        if lead.status != old_status:
            CrmTimelineService.record_status_change(
                lead=lead,
                actor=actor,
                from_status=old_status,
                to_status=lead.status,
            )
        if lead.assigned_to_id and lead.assigned_to_id != old_assignee:
            cls._notify_assignment(lead, actor)

        AuditService.log(
            user=actor,
            module=AuditModule.CRM,
            action="update",
            resource_type="crm_lead",
            resource_id=str(lead.public_id),
            changes={"status": lead.status},
        )
        return lead

    @staticmethod
    def _ensure_party_for_lead(data: dict[str, Any]):
        if data.get("party_id"):
            from apps.erp.models import Party

            party = Party.objects.filter(public_id=data["party_id"]).first()
            if party:
                return party

        display = data.get("company_name") or data.get("title", "Lead")
        party = PartyService.create_party(
            party_type=PartyType.ORGANIZATION if data.get("company_name") else PartyType.PERSON,
            display_name=display,
            legal_name=data.get("company_name", display),
            email=data.get("contact_email", ""),
            phone=data.get("contact_phone", ""),
        )
        if data.get("contact_name"):
            parts = data["contact_name"].split(" ", 1)
            PartyService.add_contact(
                party=party,
                first_name=parts[0],
                last_name=parts[1] if len(parts) > 1 else "",
                email=data.get("contact_email", ""),
                phone=data.get("contact_phone", ""),
                is_primary=True,
            )
        return party

    @staticmethod
    def _notify_assignment(lead: CrmLead, actor) -> None:
        if not lead.assigned_to:
            return
        NotificationService.send(
            recipient=lead.assigned_to,
            channel="in_app",
            subject=f"Lead assigned: {lead.title}",
            body=f"You have been assigned lead '{lead.title}' ({lead.company_name or '—'}).",
            resource_type="crm_lead",
            resource_id=str(lead.public_id),
        )


class CrmOpportunityService:
    @staticmethod
    def list_opportunities(
        *,
        status: str | None = None,
        assigned_to_id: UUID | None = None,
        search: str | None = None,
    ) -> QuerySet[CrmOpportunity]:
        qs = CrmOpportunity.objects.filter(deleted_at__isnull=True).select_related(
            "party", "lead", "customer", "trade_account", "assigned_to"
        )
        if status:
            qs = qs.filter(status=status)
        if assigned_to_id:
            qs = qs.filter(assigned_to__public_id=assigned_to_id)
        if search:
            qs = qs.filter(Q(name__icontains=search) | Q(party__display_name__icontains=search))
        return qs.order_by("-created_at")

    @staticmethod
    def get_opportunity(public_id: UUID) -> CrmOpportunity:
        opp = (
            CrmOpportunity.objects.filter(deleted_at__isnull=True, public_id=public_id)
            .select_related(
                "party", "lead", "customer", "trade_account", "assigned_to", "quote_draft"
            )
            .first()
        )
        if not opp:
            raise NotFoundError("Opportunity not found.")
        return opp

    @staticmethod
    def get_opportunity_detail(public_id: UUID) -> dict:
        opp = CrmOpportunityService.get_opportunity(public_id)
        quote_draft = getattr(opp, "quote_draft", None)
        if quote_draft is None:
            from apps.trade_accounts.models import Quote

            quote_draft = Quote.objects.filter(
                crm_opportunity=opp, status=Quote.Status.DRAFT
            ).first()
        from apps.crm.serializers import serialize_opportunity_detail

        return serialize_opportunity_detail(opp, quote_draft=quote_draft)

    @classmethod
    @transaction.atomic
    def create_opportunity(cls, *, actor, data: dict[str, Any]) -> CrmOpportunity:
        party = cls._resolve_party(data)
        lead = None
        if data.get("lead_id"):
            lead = CrmLeadService.get_lead(data["lead_id"])

        customer = cls._resolve_customer(data)
        trade_account = cls._resolve_trade_account(data, customer)

        opp = CrmOpportunity.objects.create(
            party=party,
            lead=lead,
            customer=customer,
            trade_account=trade_account,
            name=data["name"],
            stage=data.get("stage", LeadStatus.QUALIFIED),
            expected_revenue_cents=int(data.get("expected_revenue_cents", 0)),
            probability=min(100, max(0, int(data.get("probability", 0)))),
            expected_close_date=data.get("expected_close_date"),
            assigned_to_id=_resolve_user_id(data.get("assigned_to_id")),
            metadata=data.get("metadata") or {},
        )

        WorkflowEngine.start(
            definition_code=ErpWorkflowCode.CRM_OPPORTUNITY,
            resource_type="crm_opportunity",
            resource_id=str(opp.public_id),
            actor=actor,
        )

        if opp.assigned_to:
            NotificationService.send(
                recipient=opp.assigned_to,
                channel="in_app",
                subject=f"Opportunity assigned: {opp.name}",
                body=f"New opportunity '{opp.name}' assigned to you.",
                resource_type="crm_opportunity",
                resource_id=str(opp.public_id),
            )

        AuditService.log(
            user=actor,
            module=AuditModule.CRM,
            action="create",
            resource_type="crm_opportunity",
            resource_id=str(opp.public_id),
            summary=f"Opportunity created: {opp.name}",
        )
        return opp

    @classmethod
    @transaction.atomic
    def update_opportunity(cls, *, opportunity: CrmOpportunity, actor, data: dict[str, Any]) -> CrmOpportunity:
        old_status = opportunity.status
        for field in (
            "name",
            "stage",
            "expected_revenue_cents",
            "probability",
            "expected_close_date",
            "lost_reason",
        ):
            if field in data:
                setattr(opportunity, field, data[field])
        if "assigned_to_id" in data:
            opportunity.assigned_to_id = _resolve_user_id(data["assigned_to_id"])
        if "status" in data:
            opportunity.status = data["status"]
            if data["status"] == OpportunityStatus.WON:
                opportunity.won_at = timezone.now()
                opportunity.stage = LeadStatus.WON
            elif data["status"] == OpportunityStatus.LOST:
                opportunity.lost_at = timezone.now()
                opportunity.stage = LeadStatus.LOST
        opportunity.save()

        if opportunity.status != old_status:
            instance = WorkflowEngine.get_for_resource(
                resource_type="crm_opportunity",
                resource_id=str(opportunity.public_id),
            )
            if instance and opportunity.status == OpportunityStatus.WON:
                try:
                    if instance.current_state != "proposal_sent":
                        WorkflowEngine.transition(
                            instance=instance,
                            action="send_proposal",
                            actor=actor,
                        )
                        instance.refresh_from_db()
                    WorkflowEngine.transition(
                        instance=instance,
                        action="win",
                        actor=actor,
                    )
                except BusinessRuleError:
                    pass
            elif instance and opportunity.status == OpportunityStatus.LOST:
                try:
                    WorkflowEngine.transition(
                        instance=instance,
                        action="lose",
                        actor=actor,
                    )
                except BusinessRuleError:
                    pass
            if opportunity.status == OpportunityStatus.WON:
                DomainEventPublisher.publish(
                    event_type=DomainEventType.CRM_OPPORTUNITY_WON,
                    aggregate_type="crm_opportunity",
                    aggregate_id=str(opportunity.public_id),
                    payload={
                        "name": opportunity.name,
                        "status": opportunity.status,
                        "expected_revenue_cents": opportunity.expected_revenue_cents,
                        "party_id": str(opportunity.party.public_id),
                    },
                    idempotency_key=f"crm.opp.won:{opportunity.public_id}",
                )
            elif opportunity.status == OpportunityStatus.LOST:
                DomainEventPublisher.publish(
                    event_type=DomainEventType.CRM_OPPORTUNITY_LOST,
                    aggregate_type="crm_opportunity",
                    aggregate_id=str(opportunity.public_id),
                    payload={"name": opportunity.name, "status": opportunity.status},
                    idempotency_key=f"crm.opp.lost:{opportunity.public_id}",
                )

        AuditService.log(
            user=actor,
            module=AuditModule.CRM,
            action="update",
            resource_type="crm_opportunity",
            resource_id=str(opportunity.public_id),
        )
        return opportunity

    @classmethod
    @transaction.atomic
    def convert_lead(cls, *, lead: CrmLead, actor, data: dict[str, Any]) -> CrmOpportunity:
        if lead.status == LeadStatus.WON:
            raise BusinessRuleError("Lead is already won.")
        opp_data = {
            "party_id": lead.party.public_id if lead.party else None,
            "lead_id": lead.public_id,
            "customer_id": lead.customer.public_id if lead.customer else data.get("customer_id"),
            "trade_account_id": data.get("trade_account_id"),
            "name": data.get("name", lead.title),
            "expected_revenue_cents": data.get("expected_revenue_cents", 0),
            "probability": data.get("probability", 25),
            "expected_close_date": data.get("expected_close_date"),
            "assigned_to_id": (
                lead.assigned_to.public_id if lead.assigned_to else data.get("assigned_to_id")
            ),
            "stage": LeadStatus.QUALIFIED,
        }
        opportunity = cls.create_opportunity(actor=actor, data=opp_data)
        lead.status = LeadStatus.QUALIFIED
        lead.save(update_fields=["status", "updated_at"])
        return opportunity

    @staticmethod
    def _resolve_party(data: dict[str, Any]):
        if data.get("party_id"):
            from apps.erp.models import Party

            party = Party.objects.filter(public_id=data["party_id"]).first()
            if party:
                return party
        if data.get("lead_id"):
            lead = CrmLeadService.get_lead(data["lead_id"])
            if lead.party:
                return lead.party
        raise BusinessRuleError("party_id or lead_id with party is required.")

    @staticmethod
    def _resolve_customer(data: dict[str, Any]) -> Customer | None:
        if not data.get("customer_id"):
            return None
        customer = Customer.objects.filter(public_id=data["customer_id"]).first()
        if not customer:
            raise NotFoundError("Customer not found.")
        PartyService.ensure_for_customer(customer)
        return customer

    @staticmethod
    def _resolve_trade_account(data: dict[str, Any], customer: Customer | None) -> TradeAccount | None:
        if data.get("trade_account_id"):
            account = TradeAccount.objects.filter(public_id=data["trade_account_id"]).first()
            if not account:
                raise NotFoundError("Trade account not found.")
            return account
        if customer and customer.organization_id:
            return TradeAccount.objects.filter(organization=customer.organization).first()
        return None


class CrmActivityService:
    @staticmethod
    def list_activities(
        *,
        lead_id: UUID | None = None,
        opportunity_id: UUID | None = None,
        party_id: UUID | None = None,
    ) -> QuerySet[CrmActivity]:
        qs = CrmActivity.objects.select_related("assigned_to", "created_by", "lead", "opportunity")
        if lead_id:
            qs = qs.filter(lead__public_id=lead_id)
        if opportunity_id:
            qs = qs.filter(opportunity__public_id=opportunity_id)
        if party_id:
            qs = qs.filter(party__public_id=party_id)
        return qs.order_by("-created_at")

    @classmethod
    @transaction.atomic
    def create_activity(cls, *, actor, data: dict[str, Any]) -> CrmActivity:
        lead = opportunity = party = None
        if data.get("lead_id"):
            lead = CrmLeadService.get_lead(data["lead_id"])
            party = lead.party
        if data.get("opportunity_id"):
            opportunity = CrmOpportunityService.get_opportunity(data["opportunity_id"])
            party = party or opportunity.party
        if data.get("party_id"):
            from apps.erp.models import Party

            party = Party.objects.filter(public_id=data["party_id"]).first()

        activity = CrmActivity.objects.create(
            party=party,
            lead=lead,
            opportunity=opportunity,
            activity_type=data["activity_type"],
            subject=data["subject"],
            description=data.get("description", ""),
            scheduled_at=data.get("scheduled_at"),
            completed_at=data.get("completed_at"),
            assigned_to_id=_resolve_user_id(data.get("assigned_to_id")) or getattr(actor, "id", None),
            created_by=actor if getattr(actor, "is_authenticated", False) else None,
        )
        if activity.assigned_to and activity.scheduled_at:
            NotificationService.send(
                recipient=activity.assigned_to,
                channel="in_app",
                subject=f"Activity scheduled: {activity.subject}",
                body=activity.description or activity.subject,
                resource_type="crm_activity",
                resource_id=str(activity.public_id),
            )
        return activity


class CrmNoteService:
    @classmethod
    @transaction.atomic
    def create_note(cls, *, actor, data: dict[str, Any]) -> CrmNote:
        lead = opportunity = party = None
        if data.get("lead_id"):
            lead = CrmLeadService.get_lead(data["lead_id"])
            party = lead.party
        if data.get("opportunity_id"):
            opportunity = CrmOpportunityService.get_opportunity(data["opportunity_id"])
            party = party or opportunity.party
        return CrmNote.objects.create(
            party=party,
            lead=lead,
            opportunity=opportunity,
            body=data["body"],
            created_by=actor if getattr(actor, "is_authenticated", False) else None,
        )


class CrmTimelineService:
    @staticmethod
    def get_feed(
        *,
        lead_id: UUID | None = None,
        opportunity_id: UUID | None = None,
        party_id: UUID | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        entries: list[dict[str, Any]] = []

        for activity in CrmActivityService.list_activities(
            lead_id=lead_id,
            opportunity_id=opportunity_id,
            party_id=party_id,
        )[:limit]:
            entries.append(
                {
                    "id": str(activity.public_id),
                    "entry_type": TimelineEntryType.ACTIVITY,
                    "activity_type": activity.activity_type,
                    "title": activity.subject,
                    "body": activity.description,
                    "occurred_at": (activity.completed_at or activity.scheduled_at or activity.created_at).isoformat(),
                    "actor_email": activity.created_by.email if activity.created_by else None,
                }
            )

        notes = CrmNote.objects.select_related("created_by")
        if lead_id:
            notes = notes.filter(lead__public_id=lead_id)
        if opportunity_id:
            notes = notes.filter(opportunity__public_id=opportunity_id)
        if party_id:
            notes = notes.filter(party__public_id=party_id)

        for note in notes.order_by("-created_at")[:limit]:
            entries.append(
                {
                    "id": str(note.public_id),
                    "entry_type": TimelineEntryType.NOTE,
                    "activity_type": ActivityType.NOTE,
                    "title": "Note",
                    "body": note.body,
                    "occurred_at": note.created_at.isoformat(),
                    "actor_email": note.created_by.email if note.created_by else None,
                }
            )

        entries.sort(key=lambda e: e["occurred_at"], reverse=True)
        return entries[:limit]

    @staticmethod
    def record_status_change(*, lead: CrmLead, actor, from_status: str, to_status: str) -> None:
        CrmNote.objects.create(
            lead=lead,
            party=lead.party,
            body=f"Status changed from {from_status} to {to_status}",
            created_by=actor if getattr(actor, "is_authenticated", False) else None,
            metadata={"entry_type": TimelineEntryType.STATUS_CHANGE, "from": from_status, "to": to_status},
        )


class CrmDashboardService:
    @staticmethod
    def get_kpis(*, assigned_to_id: UUID | None = None) -> dict[str, Any]:
        leads = CrmLead.objects.filter(deleted_at__isnull=True)
        opps = CrmOpportunity.objects.filter(deleted_at__isnull=True)
        if assigned_to_id:
            leads = leads.filter(assigned_to__public_id=assigned_to_id)
            opps = opps.filter(assigned_to__public_id=assigned_to_id)

        total_leads = leads.count()
        open_opportunities = opps.filter(status=OpportunityStatus.OPEN).count()
        won = opps.filter(status=OpportunityStatus.WON).count()
        lost = opps.filter(status=OpportunityStatus.LOST).count()
        closed = won + lost
        conversion_rate = round((won / closed) * 100, 1) if closed else 0.0

        forecast = sum(
            o.weighted_revenue_cents
            for o in opps.filter(status=OpportunityStatus.OPEN).only(
                "expected_revenue_cents", "probability"
            )
        )

        by_status = {
            row["status"]: row["count"]
            for row in leads.values("status").annotate(count=Count("id"))
        }

        return {
            "total_leads": total_leads,
            "open_opportunities": open_opportunities,
            "conversion_rate": conversion_rate,
            "revenue_forecast_cents": forecast,
            "leads_by_status": by_status,
            "won_opportunities": won,
            "lost_opportunities": lost,
        }

    @staticmethod
    def get_charts(*, assigned_to_id: UUID | None = None) -> dict[str, Any]:
        opps = CrmOpportunity.objects.filter(deleted_at__isnull=True)
        leads = CrmLead.objects.filter(deleted_at__isnull=True)
        if assigned_to_id:
            opps = opps.filter(assigned_to__public_id=assigned_to_id)
            leads = leads.filter(assigned_to__public_id=assigned_to_id)

        pipeline_value = []
        forecast_revenue = []
        for stage in LeadStatus:
            stage_opps = opps.filter(stage=stage.value, status=OpportunityStatus.OPEN)
            total_cents = sum(o.expected_revenue_cents for o in stage_opps.only("expected_revenue_cents", "probability"))
            weighted_cents = sum(o.weighted_revenue_cents for o in stage_opps.only("expected_revenue_cents", "probability"))
            pipeline_value.append(
                {
                    "stage": stage.value,
                    "label": stage.label,
                    "valueCents": total_cents,
                    "count": stage_opps.count(),
                }
            )
            forecast_revenue.append(
                {
                    "stage": stage.value,
                    "label": stage.label,
                    "weightedCents": weighted_cents,
                }
            )

        won = opps.filter(status=OpportunityStatus.WON).count()
        lost = opps.filter(status=OpportunityStatus.LOST).count()
        closed = won + lost
        win_rate = round((won / closed) * 100, 1) if closed else 0.0

        qualified_plus = leads.filter(
            status__in=[
                LeadStatus.QUALIFIED,
                LeadStatus.PROPOSAL_SENT,
                LeadStatus.WON,
            ]
        ).count()
        total_leads = leads.count()
        lead_conversion = round((qualified_plus / total_leads) * 100, 1) if total_leads else 0.0

        return {
            "pipeline_value": pipeline_value,
            "forecast_revenue": forecast_revenue,
            "win_rate": win_rate,
            "conversion_rate": lead_conversion,
        }


class CrmPipelineService:
    @staticmethod
    def get_pipeline(*, assigned_to_id: UUID | None = None) -> dict[str, list[dict[str, Any]]]:
        columns: dict[str, list[dict[str, Any]]] = {}
        for stage in LeadStatus:
            qs = CrmLead.objects.filter(deleted_at__isnull=True, status=stage.value).select_related(
                "assigned_to", "party"
            )
            if assigned_to_id:
                qs = qs.filter(assigned_to__public_id=assigned_to_id)
            from apps.crm.serializers import serialize_lead

            columns[stage.value] = [serialize_lead(lead) for lead in qs.order_by("-updated_at")[:100]]
        return columns

    @classmethod
    @transaction.atomic
    def move_lead(cls, *, lead: CrmLead, new_status: str, actor) -> CrmLead:
        if new_status not in LeadStatus.values:
            raise BusinessRuleError(f"Invalid pipeline stage: {new_status}")
        return CrmLeadService.update_lead(lead=lead, actor=actor, data={"status": new_status})
