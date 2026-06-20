# Enterprise Role-Based Access Control (RBAC)

A2Z Tools uses **explicit role-based access control**: fine-grained **permission codenames** control API and UI access. Permissions are granted **only** through assigned `UserRole` records.

Django flags serve separate purposes:

| Flag | Purpose |
|------|---------|
| `is_staff` | Access to Django admin UI and staff-only API docs — **does not** grant business permissions |
| `is_superuser` | Full system access; auto-assigns `super-admin` RBAC role |

## Roles

| Role | Slug | Scope |
|------|------|--------|
| Super Admin | `super-admin` | Full system including user/role management |
| Admin | `admin` | Platform administration (no `users.manage`) |
| Manager | `manager` | Operational oversight — catalog, orders, customers, suppliers |
| Warehouse Manager | `warehouse-manager` | Inventory, warehouses, PO receipt, fulfillment |
| Sales Representative | `sales-representative` | Orders, customers, trade visibility |
| Customer Service | `customer-service` | Customer support and order updates |
| Trade Reviewer | `trade-reviewer` | Approve/reject B2B trade applications |
| Trade Customer | `trade-customer` | B2B storefront with trade pricing |
| Customer | `customer` | Retail storefront checkout |

Legacy `staff` role maps to **Manager** permissions for backward compatibility.

## Permission Model

Permissions use `module.action` codenames stored in `accounts_permission`:

```
dashboard.view      catalog.view       catalog.manage
inventory.view      inventory.manage   warehouse.view
orders.view         orders.manage      customers.view
suppliers.view      suppliers.manage   trade.approve
settings.manage     users.manage       store.checkout
store.trade_pricing ...
```

### Source of truth

| Layer | Purpose |
|-------|---------|
| `backend/apps/accounts/rbac.py` → `ROLE_PERMISSIONS` | **Seed matrix** — version-controlled defaults for migrations and `ensure_system_roles()` |
| `role_permissions` table | **Runtime source** — `PermissionService.get_user_permissions()` reads from the database |
| `frontend/src/lib/rbac/permissions.ts` | **UI codenames** — must match backend `PermissionCodename` |

After deploy or permission changes, run:

```bash
cd backend
python manage.py shell -c "from apps.accounts.services import RoleService; RoleService.ensure_system_roles()"
```

`seed_role_permissions()` adds missing mappings and **removes** permissions no longer in `ROLE_PERMISSIONS`.

> **Note:** `UserRole.organization` scopes roles to an organization. Users receive permissions from **global roles** (`organization=NULL`) and **org-scoped roles** when their customer profile or `OrganizationMember` record belongs to that organization.

## Backend Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        API Request                          │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  DRF Permission Classes (apps/accounts/permissions.py)      │
│  • HasRole / HasPermission    • CanViewInventory            │
│  • CanViewSuppliers           • CanCheckout                 │
│  • require_permissions(...) factory                         │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  PermissionService (apps/accounts/services.py)              │
│  • get_user_permissions() → queries role_permissions DB     │
│  • has_permission()         • Superuser → all permissions   │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Data: User → UserRole → Role → RolePermission → Permission │
└─────────────────────────────────────────────────────────────┘
```

### Django integration

- `User.is_superuser` → auto-assigns `super-admin` role on save (`RoleService.sync_platform_roles`)
- `User.is_staff` → auto-assigns `manager` role
- Customer registration → `customer` or `trade-customer` based on `customer_type`

### DRF defaults

- **Default:** `IsAuthenticated` (see `config/settings/base.py`)
- **Public endpoints** must explicitly set `permission_classes = [AllowAny]` (catalog read, cart, auth, analytics, coupons)

### Module permission classes

| Class | Codename |
|-------|----------|
| `CanViewInventory` | `inventory.view` |
| `CanManageInventory` | `inventory.manage` |
| `CanViewSuppliers` | `suppliers.view` |
| `CanManageSuppliers` | `suppliers.manage` |
| `CanViewOrders` | `orders.view` |
| `CanManageOrders` | `orders.manage` |
| `CanCheckout` | `store.checkout` |

### DRF usage

```python
from apps.accounts.permissions import (
    CanViewInventory,
    CanManageInventory,
    CanViewSuppliers,
    CanManageSuppliers,
    CanCheckout,
    require_permissions,
)
from apps.accounts.rbac import PermissionCodename

class InventoryListView(generics.ListAPIView):
    permission_classes = [CanViewInventory]

class SupplierListView(generics.ListAPIView):
    permission_classes = [CanViewSuppliers]

class OrderListCreateView(generics.ListCreateAPIView):
    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated(), CanCheckout(), IsEmailVerified()]
        return [IsAuthenticated()]
```

### Endpoint → permission map (staff APIs)

| Module | View | Permission |
|--------|------|------------|
| Inventory | List levels, movements, alerts | `inventory.view` |
| Inventory | Stock in/out/transfer/adjust | `inventory.manage` |
| Suppliers | List suppliers, POs | `suppliers.view` |
| Suppliers | Create/submit/confirm/cancel PO | `suppliers.manage` |
| Suppliers | Receive PO (goods receipt) | `inventory.manage` |
| Orders | List own orders | `IsAuthenticated` |
| Orders | List all orders (staff) | `orders.view` |
| Orders | Place order (checkout) | `store.checkout` + verified email |
| Orders | Pack / ship / deliver / cancel | `orders.manage` |
| Catalog | Product/category/brand read | Public (`IsCatalogReadOnly`) |

### Auth API

| Endpoint | Response fields |
|----------|-----------------|
| `GET /api/v1/auth/profile/` | `roles`, `permissions` |
| `GET /api/v1/auth/permissions/` | `roles`, `permissions` |
| Login / Register | `user.permissions`, `user.roles` |

Permissions in auth responses reflect **database** role assignments.

## Frontend Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  middleware.ts + AdminRouteGuard / RouteGuard                 │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  usePermissions / useRoles (hooks/use-permissions.ts)       │
│  Reads auth store → user.permissions, user.roles (from API) │
└─────────────────────────────┬───────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
        Sidebar filter   <Can> component   Route map
     (config/admin/nav)  (component RBAC)  (lib/rbac/access)
```

### Route protection

| Route | Guard | Requirement |
|-------|-------|-------------|
| `/admin-dashboard/*` | `middleware.ts` + `AdminRouteGuard` | Session cookie + `dashboard.view` + per-route permission |
| `/account/*` | `middleware.ts` + `RouteGuard` | Session cookie + JWT |
| `/checkout` | `RouteGuard` (`requireVerified`) | Authenticated + verified email |

Client-side checks are **UX only** — the backend enforces all permissions.

### Sidebar permissions

Each item in `config/admin/nav.ts` declares a `permission`. `AdminSidebar` filters items with `hasPermission()`.

### Component permissions

```tsx
import { Can } from "@/components/rbac/can";
import { Permission } from "@/lib/rbac";

<Can permission={Permission.INVENTORY_MANAGE}>
  <Button>Stock in</Button>
</Can>

<Can permission={Permission.SUPPLIERS_MANAGE}>
  <Button>Create PO</Button>
</Can>
```

### Demo mode

Set `NEXT_PUBLIC_ADMIN_DEMO=true` to grant all permissions without login (mock admin data). **Do not enable in production.**

Development no longer auto-bypasses RBAC — use the explicit flag or sign in as a staff user.

## Role → Permission Matrix (summary)

| Permission | Super Admin | Admin | Manager | WH Mgr | Sales | CS | Trade | Customer |
|------------|:-----------:|:-----:|:-------:|:------:|:-----:|:--:|:-----:|:--------:|
| dashboard.view | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | | |
| catalog.manage | ✓ | ✓ | ✓ | | | | | |
| inventory.manage | ✓ | ✓ | | ✓ | | | | |
| suppliers.view | ✓ | ✓ | ✓ | ✓ | | | | |
| suppliers.manage | ✓ | ✓ | ✓ | | | | | |
| orders.manage | ✓ | ✓ | ✓ | | ✓ | ✓ | | |
| users.manage | ✓ | | | | | | | |
| store.checkout | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| store.trade_pricing | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | |

See `backend/apps/accounts/rbac.py` for the complete matrix.

## Extending RBAC

1. Add codename to `PermissionCodename` in `rbac.py` and `frontend/src/lib/rbac/permissions.ts`
2. Add to `SYSTEM_PERMISSIONS` and relevant `ROLE_PERMISSIONS` entries
3. Run `RoleService.ensure_system_roles()` or create a data migration
4. Apply DRF permission class on new views
5. Add `permission` to admin nav item and wrap UI with `<Can>`

## Testing

```bash
cd backend
python manage.py test apps.accounts.tests.test_rbac
```

Key test cases:
- Role matrix enforcement per module
- Runtime permissions read from `role_permissions` table
- Checkout requires `store.checkout`
- Checkout requires verified email (`IsEmailVerified`)
- Org-scoped roles only apply for matching organization
- Staff order workflow (`pack`, `ship`, `deliver`, `cancel`) requires `orders.manage`
- Inventory API denies sales rep without `inventory.view`

## Related docs

- [Backend Architecture](./BACKEND_ARCHITECTURE.md)
- [Frontend API Integration](./FRONTEND_API_INTEGRATION.md)
- [Inventory Management](./INVENTORY_MANAGEMENT.md)
