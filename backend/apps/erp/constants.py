"""ERP foundation constants — document types, events, workflow codes."""
from django.db import models


class DocumentType(models.TextChoices):
    SALES_ORDER = "SO", "Sales Order"
    PURCHASE_ORDER = "PO", "Purchase Order"
    INVOICE = "INV", "Invoice"
    QUOTE = "QT", "Quote"
    GOODS_RECEIPT = "GRN", "Goods Receipt"
    STOCK_MOVEMENT = "SM", "Stock Movement"
    TRADE_ACCOUNT = "TA", "Trade Account"


class DomainEventType(models.TextChoices):
    ORDER_CREATED = "order.created", "Order Created"
    ORDER_PAID = "order.paid", "Order Paid"
    ORDER_SHIPPED = "order.shipped", "Order Shipped"
    ORDER_CANCELLED = "order.cancelled", "Order Cancelled"
    INVENTORY_RECEIVED = "inventory.received", "Inventory Received"
    INVENTORY_ADJUSTED = "inventory.adjusted", "Inventory Adjusted"
    TRADE_APPROVED = "trade.approved", "Trade Approved"
    TRADE_REJECTED = "trade.rejected", "Trade Rejected"
    PO_CREATED = "po.created", "Purchase Order Created"
    PO_SUBMITTED = "po.submitted", "Purchase Order Submitted"
    PO_APPROVED = "po.approved", "Purchase Order Approved"
    PO_RECEIVED = "po.received", "Purchase Order Received"
    WORKFLOW_COMPLETED = "workflow.completed", "Workflow Completed"


class WorkflowCode(models.TextChoices):
    TRADE_APPROVAL = "trade_approval", "Trade Account Approval"
    PO_APPROVAL = "po_approval", "Purchase Order Approval"
    LEAVE_APPROVAL = "leave_approval", "Leave Approval"


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
