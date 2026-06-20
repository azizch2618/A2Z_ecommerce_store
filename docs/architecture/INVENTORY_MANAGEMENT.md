# Production Inventory Management

Australian-compliant inventory valuation and WMS APIs for A2Z Tools.

## Features

| Feature | Endpoint | Notes |
|---------|----------|-------|
| Stock movement ledger | `GET /inventory/movements/` | Filter by `date_from`, `date_to`, `transaction_type`, `sku` |
| Movement detail | `GET /inventory/movements/{id}/` | Single append-only ledger entry |
| Warehouse transfers | `POST /inventory/stock-transfer/` | Paired TRANSFER_OUT / TRANSFER_IN |
| Transfer history | `GET /inventory/transfers/` | Grouped by `transfer_group_id` |
| Reorder levels | `PATCH /inventory/levels/{id}/` | `reorder_point`, `reorder_quantity` |
| Low stock alerts | `GET /inventory/alerts/low-stock/` | Live query |
| Notifications | `GET /inventory/notifications/` | Persisted alerts with acknowledge |
| Inventory valuation | `GET /inventory/valuation/` | Weighted average, ex-GST + 10% GST |
| Ledger summary | `GET /inventory/ledger/summary/` | Period receipts/issues (BAS-ready ex-GST) |

## Australian business rules

- **Currency:** AUD (`A2Z_CURRENCY_CODE`)
- **GST:** 10% (`A2Z_GST_RATE`) — inventory valued **excluding GST** (balance sheet asset); GST component reported separately for BAS
- **Valuation method:** Weighted average cost per SKU per warehouse
- **Costs on receipt:** Recorded ex-GST (`cost_price_cents` on stock-in)
- **States:** Warehouse addresses use Australian state codes (NSW, VIC, etc.)

## Notification lifecycle

1. Stock movement updates `InventoryLevel`
2. `InventoryAlertService.sync_alerts_for_level()` creates/updates `InventoryAlert`
3. Staff see active alerts at `GET /inventory/notifications/`
4. `POST /inventory/notifications/{id}/acknowledge/` marks acknowledged
5. Stock above reorder point auto-resolves alerts

## Frontend

- Admin **Inventory** page uses live API when JWT present; mock store in demo mode
- Tabs: stock levels (inline reorder edit), movement ledger, transfer ledger, valuation, notifications

## Tests

```bash
cd backend
python manage.py test apps.inventory.tests
```
