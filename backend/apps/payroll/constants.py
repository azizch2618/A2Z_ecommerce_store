from django.db import models


class PayrollPeriodStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    CALCULATED = "calculated", "Calculated"
    APPROVED = "approved", "Approved"
    POSTED = "posted", "Posted"


class PayFrequency(models.TextChoices):
    WEEKLY = "weekly", "Weekly"
    FORTNIGHTLY = "fortnightly", "Fortnightly"
    MONTHLY = "monthly", "Monthly"


class SalaryComponentType(models.TextChoices):
    BASE = "base", "Base Salary"
    ALLOWANCE = "allowance", "Allowance"
    DEDUCTION = "deduction", "Deduction"
    SUPER = "super", "Superannuation"
    PAYG = "payg", "PAYG Withholding"
    OVERTIME = "overtime", "Overtime"


class PayslipLineType(models.TextChoices):
    EARNING = "earning", "Earning"
    ALLOWANCE = "allowance", "Allowance"
    DEDUCTION = "deduction", "Deduction"
    LEAVE = "leave", "Leave Deduction"
    OVERTIME = "overtime", "Overtime"
    ADJUSTMENT = "adjustment", "Manual Adjustment"
    SUPER = "super", "Superannuation"
    PAYG = "payg", "PAYG Withholding"


class PayslipStatus(models.TextChoices):
    CALCULATED = "calculated", "Calculated"
    FINALIZED = "finalized", "Finalized"
