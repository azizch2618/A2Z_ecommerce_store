"""ERP foundation constants — document types, events, workflow codes."""
from django.db import models


class DocumentType(models.TextChoices):
    SALES_ORDER = "SO", "Sales Order"
    PURCHASE_ORDER = "PO", "Purchase Order"
    PURCHASE_REQUEST = "PR", "Purchase Request"
    INVOICE = "INV", "Invoice"
    QUOTE = "QT", "Quote"
    GOODS_RECEIPT = "GRN", "Goods Receipt"
    STOCK_MOVEMENT = "SM", "Stock Movement"
    STOCK_TRANSFER = "ST", "Stock Transfer"
    PICK_LIST = "PK", "Pick List"
    PUTAWAY = "PT", "Putaway Task"
    CYCLE_COUNT = "CC", "Cycle Count"
    ADJUSTMENT = "ADJ", "Inventory Adjustment"
    TRADE_ACCOUNT = "TA", "Trade Account"
    JOURNAL_ENTRY = "JE", "Journal Entry"
    AP_INVOICE = "AP", "AP Invoice"
    AR_PAYMENT = "RP", "AR Payment"
    AP_PAYMENT = "PP", "AP Payment"
    CREDIT_NOTE = "CN", "Credit Note"
    DEBIT_NOTE = "DN", "Debit Note"
    EMPLOYEE = "EMP", "Employee"
    LEAVE_REQUEST = "LR", "Leave Request"
    HRM_ASSET = "HA", "HRM Asset"


class DomainEventType(models.TextChoices):
    ORDER_CREATED = "order.created", "Order Created"
    ORDER_PAID = "order.paid", "Order Paid"
    ORDER_SHIPPED = "order.shipped", "Order Shipped"
    ORDER_CANCELLED = "order.cancelled", "Order Cancelled"
    INVENTORY_RECEIVED = "inventory.received", "Inventory Received"
    INVENTORY_ADJUSTED = "inventory.adjusted", "Inventory Adjusted"
    INVENTORY_TRANSFERRED = "inventory.transferred", "Inventory Transferred"
    TRADE_APPROVED = "trade.approved", "Trade Approved"
    TRADE_REJECTED = "trade.rejected", "Trade Rejected"
    PO_CREATED = "po.created", "Purchase Order Created"
    PO_SUBMITTED = "po.submitted", "Purchase Order Submitted"
    PO_APPROVED = "po.approved", "Purchase Order Approved"
    PO_RECEIVED = "po.received", "Purchase Order Received"
    PURCHASE_REQUEST_CREATED = "purchase_request.created", "Purchase Request Created"
    PURCHASE_REQUEST_APPROVED = "purchase_request.approved", "Purchase Request Approved"
    GOODS_RECEIVED = "goods.received", "Goods Received"
    SUPPLIER_DELIVERY_DELAYED = "supplier.delivery_delayed", "Supplier Delivery Delayed"
    WORKFLOW_COMPLETED = "workflow.completed", "Workflow Completed"
    CRM_LEAD_CREATED = "crm.lead.created", "CRM Lead Created"
    CRM_OPPORTUNITY_WON = "crm.opportunity.won", "CRM Opportunity Won"
    CRM_OPPORTUNITY_LOST = "crm.opportunity.lost", "CRM Opportunity Lost"
    QUOTE_DRAFT_CREATED = "quote.draft.created", "Quote Draft Created"
    QUOTE_CREATED = "quote.created", "Quote Created"
    QUOTE_APPROVED = "quote.approved", "Quote Approved"
    QUOTE_ACCEPTED = "quote.accepted", "Quote Accepted"
    QUOTE_CONVERTED = "quote.converted", "Quote Converted"
    PICK_COMPLETED = "pick.completed", "Pick Completed"
    CYCLE_COUNT_COMPLETED = "cycle_count.completed", "Cycle Count Completed"
    JOURNAL_POSTED = "journal.posted", "Journal Posted"
    AR_INVOICE_ISSUED = "ar.invoice.issued", "AR Invoice Issued"
    AR_PAYMENT_RECEIVED = "ar.payment.received", "AR Payment Received"
    AR_CREDIT_NOTE_ISSUED = "ar.credit_note.issued", "AR Credit Note Issued"
    AP_INVOICE_APPROVED = "ap.invoice.approved", "AP Invoice Approved"
    AP_PAYMENT_MADE = "ap.payment.made", "AP Payment Made"
    AP_DEBIT_NOTE_ISSUED = "ap.debit_note.issued", "AP Debit Note Issued"


class WorkflowCode(models.TextChoices):
    TRADE_APPROVAL = "trade_approval", "Trade Account Approval"
    PO_APPROVAL = "po_approval", "Purchase Order Approval"
    LEAVE_APPROVAL = "leave_approval", "Leave Approval"
    CRM_OPPORTUNITY = "crm_opportunity", "CRM Opportunity Pipeline"
    QUOTE_APPROVAL = "quote_approval", "Quote Approval"
    PR_APPROVAL = "pr_approval", "Purchase Requisition Approval"
    WMS_TRANSFER_APPROVAL = "wms_transfer_approval", "WMS Transfer Approval"
    WMS_ADJUSTMENT_APPROVAL = "wms_adjustment_approval", "WMS Adjustment Approval"
    AR_INVOICE_APPROVAL = "ar_invoice_approval", "AR Invoice Approval"
    AP_INVOICE_APPROVAL = "ap_invoice_approval", "AP Invoice Approval"


class AuditModule(models.TextChoices):
    ERP = "erp", "ERP Platform"
    CATALOG = "catalog", "Catalog"
    INVENTORY = "inventory", "Inventory"
    ORDERS = "orders", "Orders"
    TRADE = "trade", "Trade"
    SUPPLIERS = "suppliers", "Suppliers"
    CUSTOMERS = "customers", "Customers"
    REPORTS = "reports", "Reports"
    WORKFLOW = "workflow", "Workflow"
    NOTIFICATIONS = "notifications", "Notifications"
    CRM = "crm", "CRM"
    QUOTES = "quotes", "Quotes"
    PROCUREMENT = "procurement", "Procurement"
    WMS = "wms", "Warehouse Management"
    ACCOUNTING = "accounting", "Accounting"
    RECEIVABLES = "receivables", "Accounts Receivable"
    PAYABLES = "payables", "Accounts Payable"
    HRM = "hrm", "Human Resources"


class PartyType(models.TextChoices):
    PERSON = "person", "Person"
    ORGANIZATION = "organization", "Organization"


class PartyRole(models.TextChoices):
    CUSTOMER = "customer", "Customer"
    SUPPLIER = "supplier", "Supplier"
    EMPLOYEE = "employee", "Employee"
    CONTACT = "contact", "Contact"


class AddressType(models.TextChoices):
    BILLING = "billing", "Billing"
    SHIPPING = "shipping", "Shipping"
    REGISTERED = "registered", "Registered Office"
    SITE = "site", "Site"
    WAREHOUSE = "warehouse", "Warehouse"


class NotificationChannel(models.TextChoices):
    EMAIL = "email", "Email"
    IN_APP = "in_app", "In-App"
    SMS = "sms", "SMS"


class NotificationStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    SENT = "sent", "Sent"
    FAILED = "failed", "Failed"
    READ = "read", "Read"


class DomainEventStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    PUBLISHED = "published", "Published"
    FAILED = "failed", "Failed"


class WorkflowInstanceStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    COMPLETED = "completed", "Completed"
    CANCELLED = "cancelled", "Cancelled"
