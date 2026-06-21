# Human Resources Management (HRM Core)

Core HR module built on the [ERP Foundation](./ERP_FOUNDATION.md) — employee records, documents, attendance, leave workflows, asset assignment, org structure, and dashboard KPIs. Integrates with the Workflow Engine, Notification Engine, and Audit Framework. **Payroll is out of scope.**

## Architecture

```
Company
  └── Business Unit
        └── Department
              └── Employee (Party link)
                    ├── Documents (contracts, certs, licenses)
                    ├── Attendance (clock in/out)
                    ├── Leave balances + LeaveRequest → Workflow
                    └── AssetAssignment ← HrmAsset
```

| Module | App | API Base |
|--------|-----|----------|
| HRM Core | `apps/hrm` | `/api/v1/hrm/admin/` |

## Data Model

### Employee (`hrm_employees`)

| Field | Description |
|-------|-------------|
| `employee_number` | Auto: **`EMP-2026-000001`** |
| `first_name`, `last_name`, `email`, `phone` | Personal details |
| `job_title`, `employment_type`, `hire_date`, `status` | Employment |
| `department`, `cost_center`, `manager` | Org links |
| `user` | Optional link to `accounts.User` |
| `party` | ERP Party record (created on hire) |

**Employment types:** `full_time`, `part_time`, `contract`, `casual`  
**Status:** `active`, `on_leave`, `terminated`, `suspended`

### Employee Documents (`hrm_employee_documents`)

| Type | Use |
|------|-----|
| `contract` | Employment contracts |
| `certification` | Training / certifications |
| `license` | Professional licenses |
| `other` | General HR files |

Uploaded via multipart form; expiry date optional.

### Attendance (`hrm_attendance_records`)

One open clock-in per employee per day. **Clock in** creates a record; **clock out** closes it.

### Leave (`hrm_leave_balances`, `hrm_leave_requests`)

| Leave type | Default balance (on hire) |
|------------|---------------------------|
| `annual` | 20 days |
| `sick` | 10 days |
| `unpaid` | 0 days |

**Leave request status:** `draft` → `submitted` → `approved` | `rejected`

Numbering: **`LR-2026-000001`**

Workflow: `leave_approval` (seeded in ERP foundation). HR Officer submits; HR Manager or Department Manager approves/rejects.

Notifications: `leave_submitted`, `leave_approved`, `leave_rejected`.

### Assets (`hrm_assets`, `hrm_asset_assignments`)

| Category | Examples |
|----------|----------|
| `laptop` | Laptops |
| `phone` | Mobile phones |
| `tool` | Tools / equipment |
| `vehicle` | Fleet vehicles |
| `other` | Other assets |

Numbering: **`HA-2026-000001`**

Assignment tracks issue/return with condition notes. Notification: `asset_assigned`.

## API Endpoints

| Method | Path | Permission | Description |
|--------|------|------------|-------------|
| GET | `/admin/dashboard/` | `hrm.view` | KPIs |
| GET | `/admin/org-structure/` | `hrm.view` | Company → dept → employee tree |
| GET/POST | `/admin/employees/` | view / manage | List / create employees |
| GET | `/admin/employees/{id}/` | `hrm.view` | Detail + balances + documents |
| POST | `/admin/employees/{id}/documents/` | `hrm.manage` | Upload document |
| POST | `/admin/employees/{id}/clock-in/` | `hrm.manage` | Clock in |
| POST | `/admin/employees/{id}/clock-out/` | `hrm.manage` | Clock out |
| GET | `/admin/employees/{id}/attendance/` | `hrm.view` | Attendance history |
| GET/POST | `/admin/leave-requests/` | view / manage | List / create leave |
| POST | `/admin/leave-requests/{id}/submit/` | `hrm.manage` | Submit for approval |
| POST | `/admin/leave-requests/{id}/approve/` | `hrm.approve` | Approve |
| POST | `/admin/leave-requests/{id}/reject/` | `hrm.approve` | Reject |
| GET/POST | `/admin/assets/` | view / manage | Asset registry |
| POST | `/admin/assets/{id}/assign/` | `hrm.manage` | Assign to employee |
| GET | `/admin/asset-assignments/` | `hrm.view` | Active assignments |
| POST | `/admin/asset-assignments/{id}/return/` | `hrm.manage` | Return asset |

## Dashboard KPIs

| KPI | Source |
|-----|--------|
| Headcount | Active employees |
| Clocked in today | Open attendance records |
| On leave today | Approved leave spanning today |
| Pending leave requests | Status `submitted` |
| Annual leave remaining | Sum of annual balances − used |
| Active asset assignments | Status `assigned` |

## RBAC

| Role | Permissions |
|------|-------------|
| `hr-officer` | `hrm.view`, `hrm.manage` |
| `hr-manager` | `hrm.view`, `hrm.manage`, `hrm.approve` |
| `department-manager` | `hrm.view`, `hrm.approve`, `hrm.self` |
| `employee` | `hrm.self` |
| `admin`, `manager` | Full HRM access (via manager perm set) |

## Audit

All create/update/workflow actions log to `AuditModule.HRM` via `HrmAuditService`.

## Frontend

| Route | Screen |
|-------|--------|
| `/admin-dashboard/hrm` | HR dashboard (KPIs, employees, leave, assets, org tree) |
| `/admin-dashboard/hrm/employees` | Employee directory |

## Seed & Setup

```bash
python manage.py makemigrations hrm
python manage.py migrate
python manage.py seed_erp_foundation   # workflows, notification templates, leave approval
```

## Out of Scope (in HRM)

Recruitment, performance reviews, and employee self-service portal UI remain in HRM. **Payroll** is a separate module — see [Payroll](./PAYROLL.md).

## Related Docs

- [ERP Foundation](./ERP_FOUNDATION.md)
- [Accounting Foundation](./ACCOUNTING.md)
- [AR/AP](./AR_AP.md)
