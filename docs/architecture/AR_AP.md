# Accounts Receivable & Accounts Payable

Subledger modules built on the [Accounting Foundation](./ACCOUNTING.md) — customer invoicing, supplier invoice matching, payments, credit/debit notes, aging, and GL integration via `AccountingEventProcessor`.

## Architecture

```
Orders / CRM              Procurement (PO → GRN)
      │                            │
      ▼                            ▼
 CustomerInvoice              SupplierInvoice
 (issue → AR)                 (match PO/GRN → approve → AP)
      │                            │
      ▼                            ▼
 Payments / Credit Notes      Payments / Debit Notes
      │                            │
      └──────── AccountingEventProcessor ────────┘
                    JournalEntry (auto-post)
```

| Module | App | API Base |
|--------|-----|----------|
| Accounts Receivable | `apps/receivables` | `/api/v1/receivables/admin/` |
| Accounts Payable | `apps/payables` | `/api/v1/payables/admin/` |

## Accounts Receivable

### Customer Invoices

| Status | Description |
|--------|-------------|
| `draft` | Editable |
| `issued` | Posted to GL (Dr AR, Cr Revenue/GST) |
| `partially_paid` | Payment allocated |
| `paid` | Fully settled |
| `overdue` | Past due date with balance |
| `cancelled` | Voided |

Numbering: **`INV-2026-000001`**

Create from order or manual lines → **issue** triggers `ar.invoice.issued`.

### Customer Statements

`GET /admin/customers/{customerId}/statement/` — outstanding balance, invoice list, payment history.

### Credit Notes

Numbering: **`CN-2026-000001`**. Issue reduces AR and reverses revenue/GST via `ar.credit_note.issued`.

### Customer Aging

Buckets: current (≤30), 31–60, 61–90, 91–120, 120+ days past due.

`GET /admin/reports/aging/` | `GET /admin/reports/outstanding/`

## Accounts Payable

### Supplier Invoices

Three-way match against **Purchase Order** and **Goods Receipt**:

1. Create from PO (`POST /admin/invoices/` with `poId`)
2. Submit → starts `ap_invoice_approval` workflow
3. Match → validates qty/cost vs PO received
4. Approve (Finance Manager) → `ap.invoice.approved` journal

| Status | Description |
|--------|-------------|
| `draft` | Created from PO |
| `submitted` | In approval workflow |
| `matched` | PO/GRN match OK |
| `approved` | GL posted (Dr GRN Accrual/GST, Cr AP) |
| `partially_paid` / `paid` | Settlement |
| `cancelled` | Voided |

Numbering: **`AP-2026-000001`**

### Supplier Statements

`GET /admin/suppliers/{supplierId}/statement/`

### Debit Notes

Numbering: **`DN-2026-000001`**. Reduces AP liability via `ap.debit_note.issued`.

### Supplier Aging

Same bucket structure as AR. `GET /admin/reports/aging/`

## Accounting Integration

| Event | Journal |
|-------|---------|
| `ar.invoice.issued` | Dr AR, Cr Revenue, Cr GST Payable |
| `ar.payment.received` | Dr Bank, Cr AR |
| `ar.credit_note.issued` | Dr Revenue/GST, Cr AR |
| `ap.invoice.approved` | Dr GRN Accrual/GST Receivable, Cr AP |
| `ap.payment.made` | Dr AP, Cr Bank |
| `ap.debit_note.issued` | Dr AP, Cr GRN Accrual/GST Receivable |

Control accounts: **1200** AR, **2100** AP (seeded with accounting foundation).

## Approval Workflows

| Code | Document |
|------|----------|
| `ar_invoice_approval` | Customer invoice (optional submit/approve) |
| `ap_invoice_approval` | Supplier invoice (match → approve) |

Finance Manager role required for approve transitions.

## Reports

| Report | AR Endpoint | AP Endpoint |
|--------|-------------|-------------|
| Summary | `/admin/summary/` | `/admin/summary/` |
| Aging | `/admin/reports/aging/` | `/admin/reports/aging/` |
| Outstanding | `/admin/reports/outstanding/` | `/admin/reports/outstanding/` |

## RBAC

| Permission | Finance User | Finance Manager |
|------------|:------------:|:---------------:|
| `receivables.view` / `payables.view` | ✓ | ✓ |
| `receivables.manage` / `payables.manage` | ✓ | ✓ |
| `receivables.approve` / `payables.approve` | | ✓ |

Admin and Manager roles include full AR/AP permissions.

## Setup

```bash
python manage.py migrate
python manage.py seed_erp_foundation
python manage.py seed_accounting_foundation
```

Re-run `seed_accounting_foundation` after upgrade to pick up AR/AP event mappings and account **2100**.

## Database Tables

| Table | Purpose |
|-------|---------|
| `receivables_customer_invoices` | AR invoice headers |
| `receivables_customer_invoice_lines` | Line items |
| `receivables_customer_payments` | Customer receipts |
| `receivables_payment_allocations` | Payment → invoice |
| `receivables_credit_notes` | Credit notes |
| `payables_supplier_invoices` | AP invoice headers |
| `payables_supplier_invoice_lines` | Matched PO lines |
| `payables_supplier_payments` | Supplier payments |
| `payables_payment_allocations` | Payment → invoice |
| `payables_debit_notes` | Debit notes |
