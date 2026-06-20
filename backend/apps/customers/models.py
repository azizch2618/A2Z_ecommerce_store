"""Customer, organization, and address models."""
from django.db import models

from apps.core.models import PublicIdModel
from apps.core.validators import validate_abn, validate_australian_postcode, validate_australian_state


class Organization(PublicIdModel):
    class CustomerSegment(models.TextChoices):
        TRADE = "trade", "Trade"
        CONTRACTOR = "contractor", "Contractor"
        BUSINESS = "business", "Business"

    legal_name = models.CharField(max_length=255)
    trading_name = models.CharField(max_length=255, blank=True)
    abn = models.CharField(max_length=11, unique=True, null=True, blank=True, validators=[validate_abn])
    abn_verified = models.BooleanField(default=False)
    abn_verified_at = models.DateTimeField(null=True, blank=True)
    acn = models.CharField(max_length=9, blank=True)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    customer_segment = models.CharField(max_length=20, choices=CustomerSegment.choices)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "organizations"

    def __str__(self) -> str:
        return self.trading_name or self.legal_name


class Customer(PublicIdModel):
    class CustomerType(models.TextChoices):
        RETAIL = "retail", "Retail"
        TRADE = "trade", "Trade"
        CONTRACTOR = "contractor", "Contractor"
        BUSINESS = "business", "Business"

    class TradeStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        SUSPENDED = "suspended", "Suspended"
        REJECTED = "rejected", "Rejected"

    user = models.OneToOneField(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="customer",
        null=True,
        blank=True,
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="customers",
    )
    customer_type = models.CharField(max_length=20, choices=CustomerType.choices, default=CustomerType.RETAIL)
    trade_account_status = models.CharField(
        max_length=20,
        choices=TradeStatus.choices,
        null=True,
        blank=True,
    )
    credit_limit_cents = models.BigIntegerField(default=0)
    payment_terms_days = models.PositiveIntegerField(null=True, blank=True)
    stripe_customer_id = models.CharField(max_length=100, blank=True)
    total_orders = models.PositiveIntegerField(default=0)
    total_spent_cents = models.BigIntegerField(default=0)

    class Meta:
        db_table = "customers"

    def __str__(self) -> str:
        if self.user_id:
            return str(self.user.email)
        return str(self.public_id)


class OrganizationMember(PublicIdModel):
    class OrgRole(models.TextChoices):
        ADMIN = "admin", "Admin"
        BUYER = "buyer", "Buyer"
        APPROVER = "approver", "Approver"
        VIEWER = "viewer", "Viewer"

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="members")
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="organization_memberships")
    role = models.CharField(max_length=30, choices=OrgRole.choices)
    is_primary_contact = models.BooleanField(default=False)
    invited_at = models.DateTimeField(null=True, blank=True)
    accepted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "organization_members"
        unique_together = [("organization", "user")]


class Address(PublicIdModel):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="addresses")
    label = models.CharField(max_length=50, blank=True)
    line1 = models.CharField(max_length=255)
    line2 = models.CharField(max_length=255, blank=True)
    suburb = models.CharField(max_length=100)
    state = models.CharField(max_length=3, validators=[validate_australian_state])
    postcode = models.CharField(max_length=4, validators=[validate_australian_postcode])
    country = models.CharField(max_length=2, default="AU")
    is_default_billing = models.BooleanField(default=False)
    is_default_shipping = models.BooleanField(default=False)

    class Meta:
        db_table = "addresses"
        verbose_name_plural = "addresses"
