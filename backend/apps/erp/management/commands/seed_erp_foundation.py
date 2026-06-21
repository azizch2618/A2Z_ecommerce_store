"""Seed ERP foundation defaults — company, sequences, workflows, templates."""
from __future__ import annotations

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.erp.constants import DocumentType, NotificationChannel, WorkflowCode
from apps.erp.models import (
    BusinessUnit,
    Company,
    Department,
    CostCenter,
    NotificationTemplate,
    PlatformSetting,
    WorkflowDefinition,
)
from apps.erp.services.document_sequence import DocumentSequenceService


class Command(BaseCommand):
    help = "Seed ERP foundation: default company, document sequences, workflows, notification templates."

    @transaction.atomic
    def handle(self, *args, **options):
        company, created = Company.objects.get_or_create(
            code="A2Z",
            defaults={
                "legal_name": "A2Z Tools Pty Ltd",
                "trading_name": "A2Z Tools",
                "abn": "",
                "gst_registered": True,
                "base_currency": "AUD",
                "email": "admin@a2ztools.com.au",
                "is_default": True,
                "is_active": True,
            },
        )
        if not company.is_default:
            Company.objects.filter(is_default=True).exclude(pk=company.pk).update(is_default=False)
            company.is_default = True
            company.save(update_fields=["is_default", "updated_at"])

        bu, _ = BusinessUnit.objects.get_or_create(
            company=company,
            code="OPS",
            defaults={"name": "Operations", "is_active": True},
        )
        dept, _ = Department.objects.get_or_create(
            business_unit=bu,
            code="WH",
            defaults={"name": "Warehouse & Logistics", "is_active": True},
        )
        CostCenter.objects.get_or_create(
            department=dept,
            code="WH-001",
            defaults={"name": "Sydney Distribution Centre", "is_active": True},
        )

        DocumentSequenceService.ensure_sequences(company=company)

        WorkflowDefinition.objects.update_or_create(
            code=WorkflowCode.TRADE_APPROVAL,
            defaults={
                "name": "Trade Account Approval",
                "document_type": "trade_application",
                "initial_state": "pending",
                "states": ["pending", "under_review", "approved", "rejected"],
                "transitions": [
                    {
                        "from": "pending",
                        "to": "under_review",
                        "action": "review",
                        "label": "Start Review",
                        "required_roles": ["trade-reviewer", "admin", "super-admin"],
                    },
                    {
                        "from": "pending",
                        "to": "approved",
                        "action": "approve",
                        "label": "Approve",
                        "required_roles": ["trade-reviewer", "admin", "super-admin"],
                        "terminal_states": ["approved"],
                    },
                    {
                        "from": "under_review",
                        "to": "approved",
                        "action": "approve",
                        "label": "Approve",
                        "required_roles": ["trade-reviewer", "admin", "super-admin"],
                        "terminal_states": ["approved"],
                    },
                    {
                        "from": "under_review",
                        "to": "rejected",
                        "action": "reject",
                        "label": "Reject",
                        "required_roles": ["trade-reviewer", "admin", "super-admin"],
                        "terminal_states": ["rejected"],
                    },
                    {
                        "from": "pending",
                        "to": "rejected",
                        "action": "reject",
                        "label": "Reject",
                        "required_roles": ["trade-reviewer", "admin", "super-admin"],
                        "terminal_states": ["rejected"],
                    },
                ],
                "is_active": True,
            },
        )

        WorkflowDefinition.objects.update_or_create(
            code=WorkflowCode.PO_APPROVAL,
            defaults={
                "name": "Purchase Order Approval",
                "document_type": "purchase_order",
                "initial_state": "draft",
                "states": ["draft", "submitted", "approved", "confirmed", "cancelled"],
                "transitions": [
                    {
                        "from": "draft",
                        "to": "submitted",
                        "action": "submit",
                        "label": "Submit for Approval",
                        "required_roles": [
                            "procurement-officer",
                            "procurement-manager",
                            "manager",
                            "admin",
                            "super-admin",
                        ],
                    },
                    {
                        "from": "submitted",
                        "to": "approved",
                        "action": "approve",
                        "label": "Approve",
                        "required_roles": [
                            "procurement-manager",
                            "manager",
                            "admin",
                            "super-admin",
                        ],
                    },
                    {
                        "from": "approved",
                        "to": "confirmed",
                        "action": "confirm",
                        "label": "Confirm with Supplier",
                        "required_roles": [
                            "procurement-manager",
                            "manager",
                            "admin",
                            "super-admin",
                        ],
                        "terminal_states": ["confirmed"],
                    },
                    {
                        "from": "draft",
                        "to": "cancelled",
                        "action": "cancel",
                        "label": "Cancel",
                        "required_roles": [
                            "procurement-officer",
                            "procurement-manager",
                            "manager",
                            "admin",
                            "super-admin",
                        ],
                        "terminal_states": ["cancelled"],
                    },
                    {
                        "from": "submitted",
                        "to": "cancelled",
                        "action": "cancel",
                        "label": "Cancel",
                        "required_roles": [
                            "procurement-manager",
                            "manager",
                            "admin",
                            "super-admin",
                        ],
                        "terminal_states": ["cancelled"],
                    },
                ],
                "is_active": True,
            },
        )

        WorkflowDefinition.objects.update_or_create(
            code=WorkflowCode.LEAVE_APPROVAL,
            defaults={
                "name": "Leave Request Approval",
                "document_type": "leave_request",
                "initial_state": "submitted",
                "states": ["submitted", "approved", "rejected"],
                "transitions": [
                    {
                        "from": "submitted",
                        "to": "approved",
                        "action": "approve",
                        "label": "Approve",
                        "required_roles": [
                            "department-manager",
                            "hr-manager",
                            "manager",
                            "admin",
                            "super-admin",
                        ],
                        "terminal_states": ["approved"],
                    },
                    {
                        "from": "submitted",
                        "to": "rejected",
                        "action": "reject",
                        "label": "Reject",
                        "required_roles": [
                            "department-manager",
                            "hr-manager",
                            "manager",
                            "admin",
                            "super-admin",
                        ],
                        "terminal_states": ["rejected"],
                    },
                ],
                "is_active": True,
            },
        )

        WorkflowDefinition.objects.update_or_create(
            code=WorkflowCode.PAYROLL_RUN_APPROVAL,
            defaults={
                "name": "Payroll Run Approval",
                "document_type": "payroll_period",
                "initial_state": "calculated",
                "states": ["calculated", "approved", "rejected"],
                "transitions": [
                    {
                        "from": "calculated",
                        "to": "approved",
                        "action": "approve",
                        "label": "Approve Payroll",
                        "required_roles": [
                            "payroll-manager",
                            "hr-manager",
                            "manager",
                            "admin",
                            "super-admin",
                        ],
                        "terminal_states": ["approved"],
                    },
                    {
                        "from": "calculated",
                        "to": "rejected",
                        "action": "reject",
                        "label": "Reject Payroll",
                        "required_roles": [
                            "payroll-manager",
                            "hr-manager",
                            "manager",
                            "admin",
                            "super-admin",
                        ],
                        "terminal_states": ["rejected"],
                    },
                ],
                "is_active": True,
            },
        )

        WorkflowDefinition.objects.update_or_create(
            code=WorkflowCode.CRM_OPPORTUNITY,
            defaults={
                "name": "CRM Opportunity Pipeline",
                "document_type": "crm_opportunity",
                "initial_state": "qualified",
                "states": ["qualified", "proposal_sent", "won", "lost"],
                "transitions": [
                    {
                        "from": "qualified",
                        "to": "proposal_sent",
                        "action": "send_proposal",
                        "label": "Send Proposal",
                        "required_roles": ["sales-representative", "manager", "admin", "super-admin"],
                    },
                    {
                        "from": "proposal_sent",
                        "to": "won",
                        "action": "win",
                        "label": "Mark Won",
                        "required_roles": ["sales-representative", "manager", "admin", "super-admin"],
                        "terminal_states": ["won"],
                    },
                    {
                        "from": "proposal_sent",
                        "to": "lost",
                        "action": "lose",
                        "label": "Mark Lost",
                        "required_roles": ["sales-representative", "manager", "admin", "super-admin"],
                        "terminal_states": ["lost"],
                    },
                    {
                        "from": "qualified",
                        "to": "lost",
                        "action": "lose",
                        "label": "Mark Lost",
                        "required_roles": ["sales-representative", "manager", "admin", "super-admin"],
                        "terminal_states": ["lost"],
                    },
                ],
                "is_active": True,
            },
        )

        WorkflowDefinition.objects.update_or_create(
            code=WorkflowCode.QUOTE_APPROVAL,
            defaults={
                "name": "Quote Approval",
                "document_type": "quote",
                "initial_state": "pending_approval",
                "states": ["pending_approval", "approved", "rejected"],
                "transitions": [
                    {
                        "from": "pending_approval",
                        "to": "approved",
                        "action": "approve",
                        "label": "Approve Quote",
                        "required_roles": ["manager", "admin", "super-admin"],
                        "terminal_states": ["approved"],
                    },
                    {
                        "from": "pending_approval",
                        "to": "rejected",
                        "action": "reject",
                        "label": "Reject Quote",
                        "required_roles": ["manager", "admin", "super-admin"],
                        "terminal_states": ["rejected"],
                    },
                ],
                "is_active": True,
            },
        )

        WorkflowDefinition.objects.update_or_create(
            code=WorkflowCode.PR_APPROVAL,
            defaults={
                "name": "Purchase Requisition Approval",
                "document_type": "purchase_request",
                "initial_state": "submitted",
                "states": ["submitted", "approved", "rejected"],
                "transitions": [
                    {
                        "from": "submitted",
                        "to": "approved",
                        "action": "approve",
                        "label": "Approve Requisition",
                        "required_roles": [
                            "procurement-manager",
                            "manager",
                            "admin",
                            "super-admin",
                        ],
                        "terminal_states": ["approved"],
                    },
                    {
                        "from": "submitted",
                        "to": "rejected",
                        "action": "reject",
                        "label": "Reject Requisition",
                        "required_roles": [
                            "procurement-manager",
                            "manager",
                            "admin",
                            "super-admin",
                        ],
                        "terminal_states": ["rejected"],
                    },
                ],
                "is_active": True,
            },
        )

        WorkflowDefinition.objects.update_or_create(
            code=WorkflowCode.WMS_TRANSFER_APPROVAL,
            defaults={
                "name": "WMS Stock Transfer Approval",
                "document_type": "stock_transfer",
                "initial_state": "draft",
                "states": ["draft", "submitted", "approved", "rejected"],
                "transitions": [
                    {
                        "from": "draft",
                        "to": "submitted",
                        "action": "submit",
                        "label": "Submit Transfer",
                        "required_roles": [
                            "warehouse-operator",
                            "warehouse-manager",
                            "admin",
                            "super-admin",
                        ],
                    },
                    {
                        "from": "submitted",
                        "to": "approved",
                        "action": "approve",
                        "label": "Approve Transfer",
                        "required_roles": [
                            "warehouse-manager",
                            "admin",
                            "super-admin",
                        ],
                        "terminal_states": ["approved"],
                    },
                    {
                        "from": "submitted",
                        "to": "rejected",
                        "action": "reject",
                        "label": "Reject Transfer",
                        "required_roles": [
                            "warehouse-manager",
                            "admin",
                            "super-admin",
                        ],
                        "terminal_states": ["rejected"],
                    },
                ],
                "is_active": True,
            },
        )

        WorkflowDefinition.objects.update_or_create(
            code=WorkflowCode.WMS_ADJUSTMENT_APPROVAL,
            defaults={
                "name": "WMS Inventory Adjustment Approval",
                "document_type": "inventory_adjustment",
                "initial_state": "draft",
                "states": ["draft", "submitted", "approved", "rejected"],
                "transitions": [
                    {
                        "from": "draft",
                        "to": "submitted",
                        "action": "submit",
                        "label": "Submit Adjustment",
                        "required_roles": [
                            "warehouse-operator",
                            "warehouse-manager",
                            "admin",
                            "super-admin",
                        ],
                    },
                    {
                        "from": "submitted",
                        "to": "approved",
                        "action": "approve",
                        "label": "Approve Adjustment",
                        "required_roles": [
                            "warehouse-manager",
                            "admin",
                            "super-admin",
                        ],
                        "terminal_states": ["approved"],
                    },
                    {
                        "from": "submitted",
                        "to": "rejected",
                        "action": "reject",
                        "label": "Reject Adjustment",
                        "required_roles": [
                            "warehouse-manager",
                            "admin",
                            "super-admin",
                        ],
                        "terminal_states": ["rejected"],
                    },
                ],
                "is_active": True,
            },
        )

        WorkflowDefinition.objects.update_or_create(
            code=WorkflowCode.AR_INVOICE_APPROVAL,
            defaults={
                "name": "AR Invoice Approval",
                "document_type": "customer_invoice",
                "initial_state": "draft",
                "states": ["draft", "submitted", "approved", "rejected"],
                "transitions": [
                    {
                        "from": "draft",
                        "to": "submitted",
                        "action": "submit",
                        "label": "Submit Invoice",
                        "required_roles": ["finance-user", "finance-manager", "admin", "super-admin"],
                    },
                    {
                        "from": "submitted",
                        "to": "approved",
                        "action": "approve",
                        "label": "Approve Invoice",
                        "required_roles": ["finance-manager", "admin", "super-admin"],
                        "terminal_states": ["approved"],
                    },
                    {
                        "from": "submitted",
                        "to": "rejected",
                        "action": "reject",
                        "label": "Reject Invoice",
                        "required_roles": ["finance-manager", "admin", "super-admin"],
                        "terminal_states": ["rejected"],
                    },
                ],
                "is_active": True,
            },
        )

        WorkflowDefinition.objects.update_or_create(
            code=WorkflowCode.AP_INVOICE_APPROVAL,
            defaults={
                "name": "AP Invoice Approval",
                "document_type": "supplier_invoice",
                "initial_state": "submitted",
                "states": ["submitted", "matched", "approved", "rejected"],
                "transitions": [
                    {
                        "from": "submitted",
                        "to": "matched",
                        "action": "match",
                        "label": "Match to PO/GRN",
                        "required_roles": ["finance-user", "finance-manager", "admin", "super-admin"],
                    },
                    {
                        "from": "matched",
                        "to": "approved",
                        "action": "approve",
                        "label": "Approve Invoice",
                        "required_roles": ["finance-manager", "admin", "super-admin"],
                        "terminal_states": ["approved"],
                    },
                    {
                        "from": "submitted",
                        "to": "rejected",
                        "action": "reject",
                        "label": "Reject Invoice",
                        "required_roles": ["finance-manager", "admin", "super-admin"],
                        "terminal_states": ["rejected"],
                    },
                ],
                "is_active": True,
            },
        )

        NotificationTemplate.objects.update_or_create(
            code="pr_submitted",
            defaults={
                "name": "Purchase Requisition Submitted",
                "channel": NotificationChannel.IN_APP,
                "subject_template": "PR {request_number} submitted",
                "body_template": "Purchase requisition {request_number} requires approval.",
                "is_active": True,
            },
        )
        NotificationTemplate.objects.update_or_create(
            code="goods_received",
            defaults={
                "name": "Goods Received",
                "channel": NotificationChannel.IN_APP,
                "subject_template": "GRN {grn_number} posted",
                "body_template": "Goods receipt {grn_number} recorded for PO {po_number}.",
                "is_active": True,
            },
        )
        NotificationTemplate.objects.update_or_create(
            code="supplier_delivery_delayed",
            defaults={
                "name": "Supplier Delivery Delayed",
                "channel": NotificationChannel.IN_APP,
                "subject_template": "PO {po_number} delivery delayed",
                "body_template": "Purchase order {po_number} was received after the expected date.",
                "is_active": True,
            },
        )

        NotificationTemplate.objects.update_or_create(
            code="trade_approved",
            defaults={
                "name": "Trade Account Approved",
                "channel": NotificationChannel.EMAIL,
                "subject_template": "Your trade account has been approved",
                "body_template": "Hello, your trade account application has been approved.",
                "is_active": True,
            },
        )
        NotificationTemplate.objects.update_or_create(
            code="po_submitted",
            defaults={
                "name": "Purchase Order Submitted",
                "channel": NotificationChannel.IN_APP,
                "subject_template": "PO {po_number} submitted",
                "body_template": "Purchase order {po_number} has been submitted for approval.",
                "is_active": True,
            },
        )

        NotificationTemplate.objects.update_or_create(
            code="crm_lead_assigned",
            defaults={
                "name": "CRM Lead Assigned",
                "channel": NotificationChannel.IN_APP,
                "subject_template": "Lead assigned: {lead_title}",
                "body_template": "You have been assigned lead {lead_title}.",
                "is_active": True,
            },
        )
        NotificationTemplate.objects.update_or_create(
            code="crm_opportunity_won",
            defaults={
                "name": "CRM Opportunity Won",
                "channel": NotificationChannel.IN_APP,
                "subject_template": "Opportunity won: {opportunity_name}",
                "body_template": "Opportunity {opportunity_name} has been marked as won.",
                "is_active": True,
            },
        )
        NotificationTemplate.objects.update_or_create(
            code="leave_submitted",
            defaults={
                "name": "Leave Request Submitted",
                "channel": NotificationChannel.IN_APP,
                "subject_template": "Leave request {request_number} submitted",
                "body_template": "{employee_name} submitted leave request {request_number} for approval.",
                "is_active": True,
            },
        )
        NotificationTemplate.objects.update_or_create(
            code="leave_approved",
            defaults={
                "name": "Leave Request Approved",
                "channel": NotificationChannel.IN_APP,
                "subject_template": "Leave approved: {request_number}",
                "body_template": "Your leave request {request_number} has been approved.",
                "is_active": True,
            },
        )
        NotificationTemplate.objects.update_or_create(
            code="leave_rejected",
            defaults={
                "name": "Leave Request Rejected",
                "channel": NotificationChannel.IN_APP,
                "subject_template": "Leave rejected: {request_number}",
                "body_template": "Your leave request {request_number} has been rejected.",
                "is_active": True,
            },
        )
        NotificationTemplate.objects.update_or_create(
            code="asset_assigned",
            defaults={
                "name": "Asset Assigned",
                "channel": NotificationChannel.IN_APP,
                "subject_template": "Asset assigned: {asset_number}",
                "body_template": "You have been assigned {asset_name} ({asset_number}).",
                "is_active": True,
            },
        )
        NotificationTemplate.objects.update_or_create(
            code="payslip_available",
            defaults={
                "name": "Payslip Available",
                "channel": NotificationChannel.IN_APP,
                "subject_template": "Payslip ready: {payslip_number}",
                "body_template": "Your payslip {payslip_number} for {period_name} is available. Net pay: {net_pay}.",
                "is_active": True,
            },
        )
        NotificationTemplate.objects.update_or_create(
            code="payroll_processed",
            defaults={
                "name": "Payroll Processed",
                "channel": NotificationChannel.IN_APP,
                "subject_template": "Payroll posted: {period_number}",
                "body_template": "Payroll run {period_name} ({period_number}) has been posted. Total net pay: {total_net}.",
                "is_active": True,
            },
        )
        NotificationTemplate.objects.update_or_create(
            code="report_delivered",
            defaults={
                "name": "Scheduled Report Delivered",
                "channel": NotificationChannel.IN_APP,
                "subject_template": "Report delivered: {report_name}",
                "body_template": "Your scheduled report '{report_name}' was generated ({filename}).",
                "is_active": True,
            },
        )

        PlatformSetting.objects.update_or_create(
            company=company,
            key="platform.version",
            defaults={"value": {"version": "1.0.0"}, "description": "ERP foundation version"},
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"ERP foundation seeded ({'created' if created else 'updated'} company {company.code})"
            )
        )
