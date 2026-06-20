"""B2B trade account and quote models."""
from django.db import models

from apps.core.models import PublicIdModel


class TradeAccount(PublicIdModel):
    class Tier(models.TextChoices):
        BRONZE = "bronze", "Bronze"
        SILVER = "silver", "Silver"
        GOLD = "gold", "Gold"
        PLATINUM = "platinum", "Platinum"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        SUSPENDED = "suspended", "Suspended"
        REJECTED = "rejected", "Rejected"

    organization = models.OneToOneField(
        "customers.Organization",
        on_delete=models.RESTRICT,
        related_name="trade_account",
    )
    account_number = models.CharField(max_length=20, unique=True)
    tier = models.CharField(max_length=20, choices=Tier.choices, default=Tier.BRONZE)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    credit_limit_cents = models.BigIntegerField(default=0)
    credit_used_cents = models.BigIntegerField(default=0)
    payment_terms_days = models.PositiveIntegerField(default=30)

    class Meta:
        db_table = "trade_accounts"

    @property
    def credit_available_cents(self) -> int:
        return max(self.credit_limit_cents - self.credit_used_cents, 0)


class TradeCreditAuditLog(PublicIdModel):
    class Action(models.TextChoices):
        AUTHORIZE = "authorize", "Authorize"
        CHARGE = "charge", "Charge"
        RELEASE = "release", "Release"

    trade_account = models.ForeignKey(
        TradeAccount,
        on_delete=models.RESTRICT,
        related_name="credit_audit_logs",
    )
    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="trade_credit_audit_logs",
    )
    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="trade_credit_audit_logs",
    )
    action = models.CharField(max_length=20, choices=Action.choices)
    amount_cents = models.BigIntegerField()
    credit_limit_cents = models.BigIntegerField()
    credit_used_before = models.BigIntegerField()
    credit_used_after = models.BigIntegerField()
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "trade_credit_audit_logs"
        ordering = ["-created_at"]


class TradeApplication(PublicIdModel):
    organization = models.ForeignKey(
        "customers.Organization",
        on_delete=models.CASCADE,
        related_name="trade_applications",
    )
    status = models.CharField(max_length=20, default="pending")
    notes = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_trade_applications",
    )


class Quote(PublicIdModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PENDING_APPROVAL = "pending_approval", "Pending Approval"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        SENT = "sent", "Sent"
        ACCEPTED = "accepted", "Accepted"
        EXPIRED = "expired", "Expired"
        CONVERTED = "converted", "Converted"
        # Legacy alias kept for migration compatibility
        DECLINED = "declined", "Declined"

    trade_account = models.ForeignKey(
        TradeAccount,
        on_delete=models.CASCADE,
        related_name="quotes",
        null=True,
        blank=True,
    )
    crm_opportunity = models.OneToOneField(
        "crm.CrmOpportunity",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="quote_draft",
    )
    party = models.ForeignKey(
        "erp.Party",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="quotes",
    )
    customer = models.ForeignKey(
        "customers.Customer",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="quotes",
    )
    created_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="quotes_created",
    )
    quote_number = models.CharField(max_length=20, unique=True)
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.DRAFT, db_index=True)
    valid_until = models.DateTimeField()
    subtotal_ex_gst_cents = models.BigIntegerField(default=0)
    gst_total_cents = models.BigIntegerField(default=0)
    discount_cents = models.BigIntegerField(default=0)
    total_inc_gst_cents = models.BigIntegerField(default=0)
    currency_code = models.CharField(max_length=3, default="AUD")
    notes = models.TextField(blank=True)
    terms_and_conditions = models.TextField(blank=True)
    converted_order = models.OneToOneField(
        "orders.Order",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="source_quote",
    )
    sent_at = models.DateTimeField(null=True, blank=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    rejected_at = models.DateTimeField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "trade_accounts_quote"
        ordering = ["-created_at"]


class QuoteLine(PublicIdModel):
    quote = models.ForeignKey(Quote, on_delete=models.CASCADE, related_name="lines")
    variant = models.ForeignKey("catalog.ProductVariant", on_delete=models.RESTRICT)
    sku = models.CharField(max_length=50)
    product_name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()
    unit_price_ex_gst_cents = models.BigIntegerField()
    discount_cents = models.BigIntegerField(default=0)
    line_gst_cents = models.BigIntegerField(default=0)
    line_subtotal_ex_gst_cents = models.BigIntegerField(default=0)
    line_total_inc_gst_cents = models.BigIntegerField()
    gst_rate = models.DecimalField(max_digits=5, decimal_places=4, default="0.1000")

    class Meta:
        db_table = "quote_lines"
