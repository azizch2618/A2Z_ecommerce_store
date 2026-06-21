from django.db import models


class KpiCategory(models.TextChoices):
    EXECUTIVE = "executive", "Executive"
    SALES = "sales", "Sales"
    INVENTORY = "inventory", "Inventory"
    PROCUREMENT = "procurement", "Procurement"
    FINANCE = "finance", "Finance"
    HR = "hr", "Human Resources"


class KpiUnit(models.TextChoices):
    CURRENCY = "currency", "Currency (AUD)"
    COUNT = "count", "Count"
    PERCENT = "percent", "Percent"
    DAYS = "days", "Days"


class ReportFormat(models.TextChoices):
    CSV = "csv", "CSV"
    EXCEL = "excel", "Excel"
    PDF = "pdf", "PDF"


class ScheduleFrequency(models.TextChoices):
    DAILY = "daily", "Daily"
    WEEKLY = "weekly", "Weekly"
    MONTHLY = "monthly", "Monthly"
