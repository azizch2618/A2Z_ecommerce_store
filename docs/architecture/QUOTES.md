# Quotation & Sales Workflow

Sales quotations built on the ERP foundation — Party-linked customers, workflow approval, PDF generation, customer acceptance, and conversion to sales orders.

## Architecture

```
CRM Opportunity (won)
        │
        ▼
  Quote (draft) ──► WorkflowEngine (threshold approval)
        │
        ├──► PDF (ReportLab)
        ├──► Customer accept/reject
        └──► Order (DocumentSequence + OrderService)
```

| Layer | Location |
|-------|----------|
| Models | `apps/trade_accounts/models.py` — `Quote`, `QuoteLine` |
| Business logic | `apps/quotes/services.py` — `QuoteService` |
| API | `apps/quotes/views.py` — `/api/v1/quotes/` |
| PDF | `apps/quotes/pdf_service.py` |
| CRM integration | `apps/crm/quotation_service.py` |

Customer data is **not duplicated** — quotes reference `Party`, `Customer`, `TradeAccount`, and `CrmOpportunity`.

## Quote statuses

| Status | Description |
|--------|-------------|
| `draft` | Editable; line items can be added |
| `pending_approval` | Total ≥ threshold; awaiting manager |
| `approved` | Ready to send |
| `rejected` | Internal or customer rejection |
| `sent` | Delivered to customer |
| `accepted` | Customer accepted |
| `expired` | Past `valid_until` |
| `converted` | Linked to a sales order |

## Approval workflow

- Threshold: `QUOTE_APPROVAL_THRESHOLD_CENTS` (default **500000** = $5,000 AUD inc GST)
- Workflow code: `quote_approval` (`WorkflowCode.QUOTE_APPROVAL`)
- Approval history stored via `WorkflowEngine` → `WorkflowAction` + instance `history`
- Auto-approve when total is below threshold on submit

## Domain events

| Event | When |
|-------|------|
| `quote.created` | Manual create or CRM won → draft |
| `quote.approved` | Manager approval |
| `quote.accepted` | Customer acceptance |
| `quote.converted` | Converted to order |

Handlers in `apps/erp/services/events.py` write audit logs and notify sales on acceptance.

## RBAC

| Permission | Roles |
|------------|-------|
| `quotes.view` | Sales Rep, Manager, Admin |
| `quotes.manage` | Sales Rep, Manager, Admin |
| `quotes.approve` | Manager, Admin |

## API routes

**Admin** (staff RBAC):

- `GET /quotes/admin/dashboard/` — KPIs
- `GET|POST /quotes/admin/` — list / create
- `GET|PATCH /quotes/admin/{id}/` — detail / update
- `POST /quotes/admin/{id}/lines/` — add line
- `POST /quotes/admin/{id}/submit|approve|reject|send|convert/`
- `GET /quotes/admin/{id}/pdf/`

**Customer portal**:

- `GET /quotes/my/` — sent/accepted/expired/converted quotes
- `POST /quotes/my/{id}/accept|reject/`
- `GET /quotes/my/{id}/pdf/`

## Frontend

- Admin dashboard: `/admin-dashboard/quotes`
- Quote list: `/admin-dashboard/quotes/list`
- Quote detail: `/admin-dashboard/quotes/[id]`
- Customer quotes on trade account page (`/account/trade`)

## Seed & config

```bash
python manage.py seed_erp_foundation   # includes quote_approval workflow
```

Set threshold via env: `QUOTE_APPROVAL_THRESHOLD_CENTS=500000`
