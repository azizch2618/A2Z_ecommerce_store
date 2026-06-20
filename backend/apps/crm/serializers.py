"""CRM API serializers — camelCase output helpers."""
from __future__ import annotations

from apps.crm.models import CrmActivity, CrmLead, CrmNote, CrmOpportunity
from apps.trade_accounts.models import Quote


def _user_ref(user) -> dict | None:
    if not user:
        return None
    name = user.email
    profile = getattr(user, "profile", None)
    if profile is not None:
        name = profile.full_name or user.email
    return {
        "id": str(user.public_id),
        "email": user.email,
        "name": name,
    }


def serialize_lead(lead: CrmLead) -> dict:
    return {
        "id": str(lead.public_id),
        "title": lead.title,
        "companyName": lead.company_name,
        "contactName": lead.contact_name,
        "contactEmail": lead.contact_email,
        "contactPhone": lead.contact_phone,
        "source": lead.source,
        "status": lead.status,
        "assignedTo": _user_ref(lead.assigned_to),
        "partyId": str(lead.party.public_id) if lead.party else None,
        "customerId": str(lead.customer.public_id) if lead.customer else None,
        "notesSummary": lead.notes_summary,
        "createdAt": lead.created_at.isoformat(),
        "updatedAt": lead.updated_at.isoformat(),
    }


def serialize_opportunity(opp: CrmOpportunity) -> dict:
    return {
        "id": str(opp.public_id),
        "name": opp.name,
        "status": opp.status,
        "stage": opp.stage,
        "expectedRevenueCents": opp.expected_revenue_cents,
        "probability": opp.probability,
        "weightedRevenueCents": opp.weighted_revenue_cents,
        "expectedCloseDate": opp.expected_close_date.isoformat() if opp.expected_close_date else None,
        "assignedTo": _user_ref(opp.assigned_to),
        "partyId": str(opp.party.public_id),
        "partyName": opp.party.display_name,
        "leadId": str(opp.lead.public_id) if opp.lead else None,
        "customerId": str(opp.customer.public_id) if opp.customer else None,
        "tradeAccountId": str(opp.trade_account.public_id) if opp.trade_account else None,
        "wonAt": opp.won_at.isoformat() if opp.won_at else None,
        "lostAt": opp.lost_at.isoformat() if opp.lost_at else None,
        "lostReason": opp.lost_reason,
        "createdAt": opp.created_at.isoformat(),
        "updatedAt": opp.updated_at.isoformat(),
    }


def serialize_activity(activity: CrmActivity) -> dict:
    return {
        "id": str(activity.public_id),
        "activityType": activity.activity_type,
        "subject": activity.subject,
        "description": activity.description,
        "scheduledAt": activity.scheduled_at.isoformat() if activity.scheduled_at else None,
        "completedAt": activity.completed_at.isoformat() if activity.completed_at else None,
        "assignedTo": _user_ref(activity.assigned_to),
        "leadId": str(activity.lead.public_id) if activity.lead else None,
        "opportunityId": str(activity.opportunity.public_id) if activity.opportunity else None,
        "partyId": str(activity.party.public_id) if activity.party else None,
        "createdAt": activity.created_at.isoformat(),
    }


def serialize_note(note: CrmNote) -> dict:
    return {
        "id": str(note.public_id),
        "body": note.body,
        "createdBy": _user_ref(note.created_by),
        "leadId": str(note.lead.public_id) if note.lead else None,
        "opportunityId": str(note.opportunity.public_id) if note.opportunity else None,
        "createdAt": note.created_at.isoformat(),
    }


def serialize_party(party) -> dict | None:
    if not party:
        return None
    return {
        "id": str(party.public_id),
        "displayName": party.display_name,
        "legalName": party.legal_name,
        "email": party.email,
        "phone": party.phone,
        "partyType": party.party_type,
    }


def serialize_customer_ref(customer) -> dict | None:
    if not customer:
        return None
    org = customer.organization
    email = customer.user.email if customer.user_id else ""
    if org and org.email:
        email = org.email
    return {
        "id": str(customer.public_id),
        "email": email,
        "organizationName": org.trading_name if org else None,
        "customerType": customer.customer_type,
    }


def serialize_trade_account_ref(account) -> dict | None:
    if not account:
        return None
    org = account.organization
    return {
        "id": str(account.public_id),
        "accountNumber": account.account_number,
        "status": account.status,
        "organizationName": org.trading_name if org else org.legal_name if org else "",
        "tier": account.tier,
    }


def serialize_quote_draft(quote: Quote | None) -> dict | None:
    if not quote:
        return None
    return {
        "id": str(quote.public_id),
        "quoteNumber": quote.quote_number,
        "status": quote.status,
        "totalIncGstCents": quote.total_inc_gst_cents,
        "validUntil": quote.valid_until.isoformat(),
        "createdAt": quote.created_at.isoformat(),
    }


def serialize_lead_detail(lead: CrmLead, *, opportunities, activities, notes) -> dict:
    base = serialize_lead(lead)
    base["party"] = serialize_party(lead.party)
    base["customer"] = serialize_customer_ref(lead.customer)
    base["opportunities"] = [serialize_opportunity(o) for o in opportunities]
    base["activities"] = [serialize_activity(a) for a in activities]
    base["notes"] = [serialize_note(n) for n in notes]
    return base


def serialize_opportunity_detail(opp: CrmOpportunity, *, quote_draft=None) -> dict:
    base = serialize_opportunity(opp)
    base["party"] = serialize_party(opp.party)
    base["customer"] = serialize_customer_ref(opp.customer)
    base["tradeAccount"] = serialize_trade_account_ref(opp.trade_account)
    base["quoteDraft"] = serialize_quote_draft(quote_draft)
    return base
