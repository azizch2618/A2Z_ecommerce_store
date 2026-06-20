# Procurement & Supplier Portal

Purchase requisitions, PO workflow, goods receipt, supplier portal, and procurement KPIs — built on the ERP foundation (WorkflowEngine, Party model, NotificationEngine, AuditFramework, DocumentSequence).

## Architecture

```
Purchase Request (draft)
        │
        ▼ submit
  WorkflowEngine (pr_approval)
        │
        ├── approved ──► convert ──► Purchase Order
        └── rejected
                │
                ▼
        PO workflow (po_approval) ──► Supplier Portal
                │
                ▼
        Goods Receipt (GRN) ──► InventoryService.stock_in
```

| Layer | Location |
|-------|----------|
| Models | `apps/procurement/models.py` |
| Business logic | `apps/procurement/services.py` |
| Admin API | `apps/procurement/views.py` — `/api/v1/procurement/admin/` |
| Supplier portal API | `/api/v1/procurement/portal/` |
| PO extensions | `apps/suppliers/models.py`, `services.py` |

## Purchase requisition statuses

| Status | Description |
|--------|-------------|
| `draft` | Editable; lines can be added |
| `submitted` | Awaiting procurement manager approval |
| `approved` | Ready to convert to PO |
| `rejected` | Declined by approver |
| `converted` | Linked to a purchase order |

### Requisition fields

- Requested by (authenticated user)
- Department / cost center (ERP org structure)
- Priority (`low`, `medium`, `high`, `urgent`)
- Justification
- Warehouse and optional preferred supplier

## Procurement workflow

1. **Purchase request** — `PurchaseRequestService.create` → `PR-{seq}`
2. **Approval** — `WorkflowCode.PR_APPROVAL` (`procurement-manager`, `manager`, `admin`)
3. **Purchase order** — `PurchaseRequestService.convert_to_po` → `PO-{seq}` + `PO_APPROVAL` workflow
4. **Supplier** — portal acknowledge, expected delivery, documents, payment status
5. **Goods receipt** — full or partial via `GoodsReceiptService.receive_po`
6. **Inventory** — stock in with `reference_type="goods_receipt"`

## Goods receipt

- Document type: `GRN` (goods receipt note)
- Tracks quantity, batch number, received date per line
- PO status: `partial_received` or `received`
- GRN status: `partial` or `full`

## Supplier portal

Suppliers access via `SupplierMembership` (user ↔ supplier link).

| Capability | Endpoint |
|------------|----------|
| View POs | `GET /procurement/portal/purchase-orders/` |
| Acknowledge | `POST .../acknowledge/` |
| Expected delivery | `POST .../expected-delivery/` |
| Payment status | `GET .../payment-status/` |
| Upload documents | `POST /procurement/portal/documents/upload/` |

Frontend: `/supplier-portal`

## Supplier performance KPIs

- On-time delivery %
- Average lead time (days)
- Order accuracy %
- Purchase spend

## Procurement dashboard KPIs

- Open requisitions
- Open purchase orders
- Procurement spend
- Aggregate supplier performance

Admin UI: `/admin-dashboard/procurement`

## Domain events

| Event | When |
|-------|------|
| `purchase_request.created` | Requisition created |
| `purchase_request.approved` | Requisition approved |
| `goods.received` | GRN posted |
| `supplier.delivery_delayed` | Received after expected date |

## RBAC

| Role | Permissions |
|------|-------------|
| Procurement Officer | `procurement.view`, `procurement.manage` |
| Procurement Manager | + `procurement.approve` |
| Warehouse Manager | `procurement.view`, `inventory.manage` (receive) |
| Supplier User | `supplier.portal` |
| Admin / Manager | Full procurement + PO workflow |

## Notifications

Templates (seeded): `pr_submitted`, `goods_received`, `supplier_delivery_delayed`

## Audit

Module: `AuditModule.PROCUREMENT` — requisition lifecycle, goods receipt, document uploads.

## API quick reference

```
GET  /api/v1/procurement/admin/dashboard/
GET  /api/v1/procurement/admin/requests/
POST /api/v1/procurement/admin/requests/
POST /api/v1/procurement/admin/requests/{id}/submit|approve|reject|convert/
GET  /api/v1/procurement/admin/goods-receipts/
GET  /api/v1/procurement/portal/purchase-orders/
POST /api/v1/suppliers/purchase-orders/{id}/receive/   # warehouse receive
```

## Tests

```bash
python manage.py test apps.procurement.tests.test_procurement_api
```
