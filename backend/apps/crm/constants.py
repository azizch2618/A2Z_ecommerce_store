"""CRM module constants."""
from django.db import models


class LeadStatus(models.TextChoices):
    NEW = "new", "New"
    CONTACTED = "contacted", "Contacted"
    QUALIFIED = "qualified", "Qualified"
    PROPOSAL_SENT = "proposal_sent", "Proposal Sent"
    WON = "won", "Won"
    LOST = "lost", "Lost"


class LeadSource(models.TextChoices):
    WEBSITE = "website", "Website"
    REFERRAL = "referral", "Referral"
    TRADE_SHOW = "trade_show", "Trade Show"
    COLD_CALL = "cold_call", "Cold Call"
    PARTNER = "partner", "Partner"
    OTHER = "other", "Other"


class OpportunityStatus(models.TextChoices):
    OPEN = "open", "Open"
    WON = "won", "Won"
    LOST = "lost", "Lost"


class ActivityType(models.TextChoices):
    CALL = "call", "Call"
    MEETING = "meeting", "Meeting"
    EMAIL = "email", "Email"
    FOLLOW_UP = "follow_up", "Follow-up"
    NOTE = "note", "Note"


class TimelineEntryType(models.TextChoices):
    ACTIVITY = "activity", "Activity"
    NOTE = "note", "Note"
    STATUS_CHANGE = "status_change", "Status Change"
