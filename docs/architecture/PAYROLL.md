# Payroll Module

Payroll processing built on [HRM Core](./HRM.md) and the [Accounting Foundation](./ACCOUNTING.md) — salary structures, pay run lifecycle, payslips, GL posting, and Australian readiness scaffolding (super, PAYG, awards). **Full tax/compliance calculations are not implemented yet.**

## Architecture

```
HRM Employee + SalaryStructure
         │
         ▼
   PayrollPeriod (draft → calculated → approved → posted)
         │
         ├── Payslip × N (per employee)
         │     └── PayslipLine (earnings, deductions, leave, adjustments)
         │
         └── DomainEvent payroll.run.posted
                    │
                    ▼
         AccountingEventProcessor → JournalEntry
              Dr Wages Expense (5300)
              Cr Wages Payable (2400)
              Cr PAYG Withholding (2410)
              Cr Super Payable (2420)
```

| Module | App | API Base |
|--------|-----|----------|
| Payroll | `apps/payroll` | `/api/v1/payroll/admin/` |

## Payroll Period Lifecycle

| Status | Description |
|--------|-------------|
| `draft` | Period created; adjustments can be added |
| `calculated` | Payslips generated from salary structures + leave + adjustments |
| `approved` | Workflow-approved; payslips finalized |
| `posted` | GL journal posted via accounting events |

Numbering: **`PRUN-2026-000001`**

Workflow: `payroll_run_approval` — calculated → approved (Payroll Manager / HR Manager).

## Salary Structure

Per-employee effective-dated structure with components:

| Component type | Purpose |
|----------------|---------|
| `base` | Base salary (cents per pay period) |
| `allowance` | Taxable allowances |
| `deduction` | Pre-tax or post-tax deductions |
| `super` | Superannuation (employer cost — AU readiness) |
| `payg` | PAYG withholding placeholder (fixed amount, not calculated) |
| `overtime` | Overtime earnings (future-ready) |

**Australian readiness fields:**
- `awardCode` on structure (e.g. `MA000004`)
- `isTaxable`, `isSuperable` flags on components
- Component types for super and PAYG without automated rate engines

## Payroll Calculation

On **calculate**, for each active employee with an effective salary structure:

1. Sum base + allowances + overtime components
2. Subtract structural deductions
3. Apply unpaid leave deduction (approved unpaid leave overlapping period × daily rate)
4. Apply manual `PayrollAdjustment` lines
5. Include PAYG/super from structure components (placeholder amounts)
6. Generate payslip + line items
7. Notify employee (`payslip_available`)

## Payslips

Numbering: **`PS-2026-000001`**

PDF via ReportLab: `GET /admin/payslips/{id}/pdf/`

## GL Integration

Event: `payroll.run.posted`

| Account | Code | Side |
|---------|------|------|
| Wages & Salaries Expense | 5300 | Debit |
| Wages Payable | 2400 | Credit |
| PAYG Withholding Payable | 2410 | Credit |
| Superannuation Payable | 2420 | Credit |

Payload: `wages_expense_cents`, `net_pay_cents`, `payg_cents`, `super_cents`

## API Endpoints

| Method | Path | Permission |
|--------|------|------------|
| GET | `/admin/dashboard/` | `payroll.view` |
| GET/POST | `/admin/periods/` | view / manage |
| GET | `/admin/periods/{id}/` | `payroll.view` |
| POST | `/admin/periods/{id}/calculate/` | `payroll.manage` |
| POST | `/admin/periods/{id}/approve/` | `payroll.approve` |
| POST | `/admin/periods/{id}/post/` | `payroll.post` |
| POST | `/admin/periods/{id}/adjustments/` | `payroll.manage` |
| GET/POST | `/admin/salary-structures/` | view / manage |
| GET | `/admin/payslips/` | `payroll.view` |
| GET | `/admin/payslips/{id}/pdf/` | `payroll.view` |
| GET | `/admin/employees/{id}/payroll-history/` | `payroll.view` |

## Dashboard KPIs

| KPI | Source |
|-----|--------|
| Total payroll YTD | Sum net pay from posted runs (FY) |
| Gross payroll YTD | Sum gross from posted runs |
| Posted runs | Count of posted periods in FY |
| Pending approval | Periods in `calculated` status |
| Department cost | Net pay by department (posted) |
| Upcoming runs | Draft/calculated periods by pay date |

## RBAC

| Role | Permissions |
|------|-------------|
| `payroll-officer` | `payroll.view`, `payroll.manage` |
| `payroll-manager` | view, manage, approve, post |
| `hr-manager` | `payroll.view`, `payroll.approve` |
| `admin`, `manager` | Full payroll access |

## Notifications

| Template | Trigger |
|----------|---------|
| `payslip_available` | After payslip calculated |
| `payroll_processed` | After period posted |

## Setup

```bash
python manage.py makemigrations payroll erp accounting
python manage.py migrate
python manage.py seed_erp_foundation
python manage.py seed_accounting_foundation
```

## Out of Scope (Future)

- Automated PAYG tax tables / STP reporting
- Super guarantee percentage calculation
- Award rate engines and penalty rates
- Bank file / ABA payment export

## Related Docs

- [HRM Core](./HRM.md)
- [Accounting Foundation](./ACCOUNTING.md)
