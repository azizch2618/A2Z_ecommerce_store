"""Trade credit authorization, charging, and audit trail."""
from __future__ import annotations

import logging

from django.db import transaction

from apps.core.exceptions import BusinessRuleError, ConflictError
from apps.orders.models import Order
from apps.trade_accounts.models import TradeAccount, TradeCreditAuditLog

logger = logging.getLogger(__name__)


class TradeCreditService:
    @staticmethod
    def get_approved_account_for_customer(customer) -> TradeAccount | None:
        if not customer or not customer.organization_id:
            return None
        return (
            TradeAccount.objects.select_for_update()
            .filter(
                organization_id=customer.organization_id,
                status=TradeAccount.Status.APPROVED,
            )
            .first()
        )

    @staticmethod
    def validate_credit_for_order(*, trade_account: TradeAccount, order: Order) -> None:
        if trade_account.status != TradeAccount.Status.APPROVED:
            raise BusinessRuleError("Trade account is not approved for credit purchases.")

        if trade_account.credit_limit_cents <= 0:
            raise BusinessRuleError("Trade account has no credit limit configured.")

        available = trade_account.credit_available_cents
        if order.total_inc_gst_cents > available:
            raise ConflictError(
                f"Insufficient trade credit. Available: ${available / 100:,.2f}, "
                f"required: ${order.total_inc_gst_cents / 100:,.2f}."
            )

    @staticmethod
    @transaction.atomic
    def authorize_and_charge(
        *,
        trade_account: TradeAccount,
        order: Order,
        user,
    ) -> TradeAccount:
        """Validate credit, charge the account, and write an audit log entry."""
        trade_account = (
            TradeAccount.objects.select_for_update()
            .filter(pk=trade_account.pk)
            .first()
        )
        if not trade_account:
            raise BusinessRuleError("Trade account not found.")

        TradeCreditService.validate_credit_for_order(
            trade_account=trade_account,
            order=order,
        )

        credit_used_before = trade_account.credit_used_cents
        trade_account.credit_used_cents += order.total_inc_gst_cents
        trade_account.save(update_fields=["credit_used_cents", "updated_at"])

        TradeCreditAuditLog.objects.create(
            trade_account=trade_account,
            order=order,
            user=user,
            action=TradeCreditAuditLog.Action.CHARGE,
            amount_cents=order.total_inc_gst_cents,
            credit_limit_cents=trade_account.credit_limit_cents,
            credit_used_before=credit_used_before,
            credit_used_after=trade_account.credit_used_cents,
            metadata={
                "order_number": order.order_number,
                "order_public_id": str(order.public_id),
            },
        )

        logger.info(
            "Trade credit charged: account=%s order=%s amount_cents=%s",
            trade_account.account_number,
            order.order_number,
            order.total_inc_gst_cents,
        )
        return trade_account
