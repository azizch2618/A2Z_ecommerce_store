# Accounting Foundation

General ledger infrastructure for A2Z Tools — chart of accounts, fiscal periods, double-entry journals, Australian GST, event-driven postings, and reporting. **Does not include AP, AR, or Payroll** (future modules consume this layer).

## Architecture

```
Domain Events                    Accounting Foundation
─────────────────               ───────────────────────
order.paid          ──►  AccountingEventProcessor ──► JournalEntry (auto-post)
goods.received      ──►         │                      JournalLine × N
inventory.adjusted  ──►         │                      (balanced debits/credits)
trade.approved      ──►         ▼
                         ChartOfAccount + AccountingPeriod (open check)
                                        │
                                        ▼
                              ReportingService
                         Trial Balance | GL | GST Summary
```

| Layer | Location |
|-------|----------|
| Models | `apps/accounting/models.py` |
| Business logic | `apps/accounting/services.py` |
| GST engine | `apps/accounting/tax.py` |
| Event handlers | `apps/accounting/event_handlers.py` |
| Admin API | `/api/v1/accounting/admin/` |
| Seed | `python manage.py seed_accounting_foundation` |

## Chart of Accounts

Five account types: **Asset**, **Liability**, **Equity**, **Revenue**, **Expense**.

Default seeded codes (per company):

| Code | Name | Type |
|------|------|------|
| 1100 | Bank Account | Asset |
| 1200 | Accounts Receivable | Asset |
| 1300 | Inventory | Asset |
| 1400 | GST Receivable | Asset |
| 2150 | GRN Accrual | Liability |
| 2200 | GST Payable | Liability |
| 2300 | Trade Credit Reserve | Liability |
| 3100 | Retained Earnings | Equity |
| 4100 | Sales Revenue | Revenue |
| 5100 | Cost of Goods Sold | Expense |
| 5200 | Inventory Adjustments | Expense |

Accounts are company-scoped with optional parent hierarchy. Posting accounts accept journal lines.

## Fiscal Periods

- **FiscalYear** — aligned to company `fiscal_year_start_month` (default July = AU)
- **AccountingPeriod** — monthly sub-periods within the FY
- Status: `open` | `closed` — posting blocked when closed

## Journal Engine

Double-entry: every **JournalEntry** has one or more **JournalLine** rows; total debits must equal total credits before posting.

| Status | Meaning |
|--------|---------|
| `draft` | Editable; lines can be added |
| `posted` | Immutable; included in reports |

Document numbering: **`JE-2026-000001`** via `DocumentSequenceService` (`DocumentType.JOURNAL_ENTRY`).

### Financial dimensions

Journal entries and lines optionally link:

- **Company** (required on entry)
- **Department** (`erp.Department`)
- **Cost Center** (`erp.CostCenter`)

## Tax Engine

Australian GST at 10% (`PricingService.GST_RATE`):

| Treatment | Behaviour |
|-----------|-----------|
| `gst_exclusive` | Amount is ex-GST; GST calculated |
| `gst_inclusive` | Amount split into ex-GST + GST |
| `gst_free` | No GST |

API: `POST /api/v1/accounting/admin/tax/calculate/`

## Accounting Event Mappings

Domain events trigger automatic journal creation via `AccountingEventMapping` templates:

| Event | Debit | Credit |
|-------|-------|--------|
| `order.paid` | Bank (inc GST) | Revenue (ex GST), GST Payable |
| `goods.received` | Inventory | GRN Accrual |
| `inventory.adjusted` | Inventory Adjustment | Inventory |
| `trade.approved` | — | Memo only (`auto_post: false`) |

Payload fields (e.g. `total_ex_gst_cents`, `gst_cents`) map to line amounts via `amount_source`.

## Audit Trail

- **AccountingAuditLog** — accounting-specific immutable log
- Mirrors to global **AuditEvent** (`AuditModule.ACCOUNTING`)
- Actions: `coa_create`, `journal_create`, `journal_post`, `period_close`, `event_journal`, etc.

## Reporting Foundation

| Report | Endpoint |
|--------|----------|
| Trial Balance | `GET /admin/reports/trial-balance/?periodId=` |
| General Ledger | `GET /admin/reports/general-ledger/?accountCode=` |
| GST Summary | `GET /admin/reports/gst-summary/?periodId=` |

GST summary returns sales ex-GST, output GST, input GST, and net GST payable.

## RBAC

| Role | Permissions |
|------|-------------|
| Finance User | `accounting.view`, `accounting.manage` (draft journals) |
| Finance Manager | + `accounting.post` (post journals, close periods) |
| Admin / Manager | Full accounting permissions |

Permission codenames: `accounting.view`, `accounting.manage`, `accounting.post`.

## API Summary

| Method | Path | Permission |
|--------|------|------------|
| GET/POST | `/admin/chart-of-accounts/` | view / manage |
| GET | `/admin/chart-of-accounts/{id}/` | view |
| GET/POST | `/admin/fiscal-years/` | view / post |
| POST | `/admin/periods/{id}/close/` | post |
| POST | `/admin/periods/{id}/reopen/` | post |
| GET/POST | `/admin/journals/` | view / manage |
| POST | `/admin/journals/{id}/lines/` | manage |
| POST | `/admin/journals/{id}/post/` | post |
| GET | `/admin/event-mappings/` | view |
| POST | `/admin/tax/calculate/` | view |
| GET | `/admin/reports/trial-balance/` | view |
| GET | `/admin/reports/general-ledger/` | view |
| GET | `/admin/reports/gst-summary/` | view |
| GET | `/admin/audit-log/` | view |

## Database Tables

| Table | Purpose |
|-------|---------|
| `accounting_chart_of_accounts` | GL accounts |
| `accounting_fiscal_years` | Financial years |
| `accounting_periods` | Monthly periods |
| `accounting_journal_entries` | Journal headers |
| `accounting_journal_lines` | Debit/credit lines |
| `accounting_event_mappings` | Event → journal templates |
| `accounting_event_mapping_lines` | Template line rules |
| `accounting_audit_logs` | Accounting audit trail |

## Subledger Modules

Built on this foundation:

- **[Accounts Receivable & Accounts Payable](./AR_AP.md)** — customer/supplier invoices, payments, credit/debit notes, aging, GL integration

Still out of scope:

- **Payroll** — expense and liability postings

## Setup

```bash
python manage.py migrate
python manage.py seed_erp_foundation
python manage.py seed_accounting_foundation
```
