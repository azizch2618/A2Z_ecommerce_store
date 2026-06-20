"""Trade account admin operations."""
from __future__ import annotations

import uuid

from django.db import transaction
from django.db.models import Count
from django.utils import timezone

from apps.core.audit import log_operation
from apps.core.exceptions import BusinessRuleError, ConflictError, NotFoundError
from apps.core.models import OperationalAuditLog
from apps.customers.models import Customer
from apps.customers.services import CustomerService
from apps.trade_accounts.models import TradeAccount, TradeApplication


def generate_account_number() -> str:
    return f"TA-{uuid.uuid4().hex[:8].upper()}"


class TradeAccountService:
    @staticmethod
    def get_for_user(user) -> TradeAccount | None:
        customer = CustomerService.get_for_user(user)
        if not customer or not customer.organization_id:
            return None
        account = (
            TradeAccount.objects.select_related("organization")
            .filter(organization_id=customer.organization_id)
            .first()
        )
        if not account or account.status != TradeAccount.Status.APPROVED:
            return None
        return account


class TradeAdminService:
    @staticmethod
    def list_applications(*, status: str | None = None):
        qs = TradeApplication.objects.select_related("organization", "reviewed_by").annotate(
            customer_count=Count("organization__customers")
        )
        if status:
            qs = qs.filter(status=status)
        return qs.order_by("-submitted_at")

    @staticmethod
    def get_application(public_id) -> TradeApplication:
        app = (
            TradeApplication.objects.select_related("organization")
            .filter(public_id=public_id)
            .first()
        )
        if not app:
            raise NotFoundError("Trade application not found.")
        return app

    @staticmethod
    @transaction.atomic
    def approve_application(
        *,
        application: TradeApplication,
        reviewer,
        credit_limit_cents: int = 0,
        payment_terms_days: int = 30,
        notes: str = "",
    ) -> TradeApplication:
        if application.status not in {"pending", ""}:
            raise ConflictError("Application is not pending review.")

        org = application.organization
        if TradeAccount.objects.filter(organization=org).exists():
            account = org.trade_account
        else:
            account = TradeAccount.objects.create(
                organization=org,
                account_number=generate_account_number(),
                status=TradeAccount.Status.APPROVED,
                credit_limit_cents=credit_limit_cents,
                payment_terms_days=payment_terms_days,
            )

        account.status = TradeAccount.Status.APPROVED
        account.credit_limit_cents = credit_limit_cents
        account.payment_terms_days = payment_terms_days
        account.save()

        application.status = "approved"
        application.notes = notes
        application.reviewed_by = reviewer
        application.save(update_fields=["status", "notes", "reviewed_by", "updated_at"])

        Customer.objects.filter(organization=org).update(
            trade_account_status=Customer.TradeStatus.APPROVED,
            credit_limit_cents=credit_limit_cents,
            payment_terms_days=payment_terms_days,
        )

        log_operation(
            user=reviewer,
            module=OperationalAuditLog.Module.TRADE,
            action="approve",
            resource_type="trade_application",
            resource_id=application.public_id,
            details={"credit_limit_cents": credit_limit_cents},
        )
        return application

    @staticmethod
    @transaction.atomic
    def reject_application(
        *,
        application: TradeApplication,
        reviewer,
        notes: str = "",
    ) -> TradeApplication:
        if application.status not in {"pending", ""}:
            raise ConflictError("Application is not pending review.")

        application.status = "rejected"
        application.notes = notes
        application.reviewed_by = reviewer
        application.save(update_fields=["status", "notes", "reviewed_by", "updated_at"])

        Customer.objects.filter(organization=application.organization).update(
            trade_account_status=Customer.TradeStatus.REJECTED,
        )

        log_operation(
            user=reviewer,
            module=OperationalAuditLog.Module.TRADE,
            action="reject",
            resource_type="trade_application",
            resource_id=application.public_id,
            details={"notes": notes},
        )
        return application

    @staticmethod
    @transaction.atomic
    def update_credit_limit(
        *,
        account: TradeAccount,
        credit_limit_cents: int,
        user,
    ) -> TradeAccount:
        if credit_limit_cents < account.credit_used_cents:
            raise BusinessRuleError("Credit limit cannot be below current usage.")
        account.credit_limit_cents = credit_limit_cents
        account.save(update_fields=["credit_limit_cents", "updated_at"])
        Customer.objects.filter(organization=account.organization).update(
            credit_limit_cents=credit_limit_cents,
        )
        log_operation(
            user=user,
            module=OperationalAuditLog.Module.TRADE,
            action="update_credit_limit",
            resource_type="trade_account",
            resource_id=account.public_id,
            details={"credit_limit_cents": credit_limit_cents},
        )
        return account
