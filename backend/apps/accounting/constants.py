from django.db import models


class AccountType(models.TextChoices):
    ASSET = "asset", "Asset"
    LIABILITY = "liability", "Liability"
    EQUITY = "equity", "Equity"
    REVENUE = "revenue", "Revenue"
    EXPENSE = "expense", "Expense"


class PeriodStatus(models.TextChoices):
    OPEN = "open", "Open"
    CLOSED = "closed", "Closed"


class JournalStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    POSTED = "posted", "Posted"
    REVERSED = "reversed", "Reversed"


class JournalLineSide(models.TextChoices):
    DEBIT = "debit", "Debit"
    CREDIT = "credit", "Credit"


class TaxTreatment(models.TextChoices):
    GST_EXCLUSIVE = "gst_exclusive", "GST Exclusive"
    GST_INCLUSIVE = "gst_inclusive", "GST Inclusive"
    GST_FREE = "gst_free", "GST Free"
    INPUT_TAXED = "input_taxed", "Input Taxed"


# Standard account codes for event mappings (seeded)
class StandardAccountCode:
    BANK = "1100"
    ACCOUNTS_RECEIVABLE = "1200"
    INVENTORY = "1300"
    GST_RECEIVABLE = "1400"
    ACCOUNTS_PAYABLE = "2100"
    GRN_ACCRUAL = "2150"
    GST_PAYABLE = "2200"
    TRADE_CREDIT_RESERVE = "2300"
    WAGES_PAYABLE = "2400"
    PAYG_WITHHOLDING = "2410"
    SUPER_PAYABLE = "2420"
    RETAINED_EARNINGS = "3100"
    SALES_REVENUE = "4100"
    COGS = "5100"
    INVENTORY_ADJUSTMENT = "5200"
    WAGES_EXPENSE = "5300"


# Domain events that accounting listens to
class AccountingSourceEvent:
    ORDER_PAID = "order.paid"
    GOODS_RECEIVED = "goods.received"
    INVENTORY_ADJUSTED = "inventory.adjusted"
    TRADE_APPROVED = "trade.approved"
