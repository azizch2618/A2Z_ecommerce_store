"""Enterprise RBAC — permission catalog and role matrix."""

from __future__ import annotations

from apps.accounts.constants import RoleSlug


class PermissionCodename:
    """Canonical permission identifiers — keep in sync with frontend `lib/rbac`."""

    DASHBOARD_VIEW = "dashboard.view"
    ANALYTICS_VIEW = "analytics.view"
    REPORTS_VIEW = "reports.view"
    REPORTS_EXPORT = "reports.export"
    CATALOG_VIEW = "catalog.view"
    CATALOG_MANAGE = "catalog.manage"
    INVENTORY_VIEW = "inventory.view"
    INVENTORY_MANAGE = "inventory.manage"
    WAREHOUSE_VIEW = "warehouse.view"
    WAREHOUSE_MANAGE = "warehouse.manage"
    ORDERS_VIEW = "orders.view"
    ORDERS_MANAGE = "orders.manage"
    CUSTOMERS_VIEW = "customers.view"
    CUSTOMERS_MANAGE = "customers.manage"
    TRADE_VIEW = "trade.view"
    TRADE_APPROVE = "trade.approve"
    SUPPLIERS_VIEW = "suppliers.view"
    SUPPLIERS_MANAGE = "suppliers.manage"
    SETTINGS_VIEW = "settings.view"
    SETTINGS_MANAGE = "settings.manage"
    USERS_MANAGE = "users.manage"
    STORE_CHECKOUT = "store.checkout"
    STORE_TRADE_PRICING = "store.trade_pricing"
    CRM_VIEW = "crm.view"
    CRM_MANAGE = "crm.manage"
    QUOTES_VIEW = "quotes.view"
    QUOTES_MANAGE = "quotes.manage"
    QUOTES_APPROVE = "quotes.approve"
    PROCUREMENT_VIEW = "procurement.view"
    PROCUREMENT_MANAGE = "procurement.manage"
    PROCUREMENT_APPROVE = "procurement.approve"
    SUPPLIER_PORTAL = "supplier.portal"
    WMS_VIEW = "wms.view"
    WMS_MANAGE = "wms.manage"
    WMS_APPROVE = "wms.approve"
    WMS_EXECUTE = "wms.execute"
    ACCOUNTING_VIEW = "accounting.view"
    ACCOUNTING_MANAGE = "accounting.manage"
    ACCOUNTING_POST = "accounting.post"
    RECEIVABLES_VIEW = "receivables.view"
    RECEIVABLES_MANAGE = "receivables.manage"
    RECEIVABLES_APPROVE = "receivables.approve"
    PAYABLES_VIEW = "payables.view"
    PAYABLES_MANAGE = "payables.manage"
    PAYABLES_APPROVE = "payables.approve"
    HRM_VIEW = "hrm.view"
    HRM_MANAGE = "hrm.manage"
    HRM_APPROVE = "hrm.approve"
    HRM_SELF = "hrm.self"
    PAYROLL_VIEW = "payroll.view"
    PAYROLL_MANAGE = "payroll.manage"
    PAYROLL_APPROVE = "payroll.approve"
    PAYROLL_POST = "payroll.post"


SYSTEM_PERMISSIONS: tuple[dict[str, str], ...] = (
    {"codename": PermissionCodename.DASHBOARD_VIEW, "module": "dashboard", "description": "View admin dashboard"},
    {"codename": PermissionCodename.ANALYTICS_VIEW, "module": "analytics", "description": "View analytics"},
    {"codename": PermissionCodename.REPORTS_VIEW, "module": "reports", "description": "View reports"},
    {"codename": PermissionCodename.REPORTS_EXPORT, "module": "reports", "description": "Export reports"},
    {"codename": PermissionCodename.CATALOG_VIEW, "module": "catalog", "description": "View products, categories, brands"},
    {"codename": PermissionCodename.CATALOG_MANAGE, "module": "catalog", "description": "Create and edit catalog"},
    {"codename": PermissionCodename.INVENTORY_VIEW, "module": "inventory", "description": "View stock levels"},
    {"codename": PermissionCodename.INVENTORY_MANAGE, "module": "inventory", "description": "Stock in/out/transfer"},
    {"codename": PermissionCodename.WAREHOUSE_VIEW, "module": "warehouse", "description": "View warehouses"},
    {"codename": PermissionCodename.WAREHOUSE_MANAGE, "module": "warehouse", "description": "Manage warehouses"},
    {"codename": PermissionCodename.ORDERS_VIEW, "module": "orders", "description": "View orders"},
    {"codename": PermissionCodename.ORDERS_MANAGE, "module": "orders", "description": "Update order status"},
    {"codename": PermissionCodename.CUSTOMERS_VIEW, "module": "customers", "description": "View customers"},
    {"codename": PermissionCodename.CUSTOMERS_MANAGE, "module": "customers", "description": "Edit customer accounts"},
    {"codename": PermissionCodename.TRADE_VIEW, "module": "trade", "description": "View trade applications"},
    {"codename": PermissionCodename.TRADE_APPROVE, "module": "trade", "description": "Approve/reject trade accounts"},
    {"codename": PermissionCodename.SUPPLIERS_VIEW, "module": "suppliers", "description": "View suppliers"},
    {"codename": PermissionCodename.SUPPLIERS_MANAGE, "module": "suppliers", "description": "Manage suppliers"},
    {"codename": PermissionCodename.SETTINGS_VIEW, "module": "settings", "description": "View system settings"},
    {"codename": PermissionCodename.SETTINGS_MANAGE, "module": "settings", "description": "Edit system settings"},
    {"codename": PermissionCodename.USERS_MANAGE, "module": "users", "description": "Manage users and roles"},
    {"codename": PermissionCodename.STORE_CHECKOUT, "module": "store", "description": "Place orders on storefront"},
    {"codename": PermissionCodename.STORE_TRADE_PRICING, "module": "store", "description": "View trade pricing"},
    {"codename": PermissionCodename.CRM_VIEW, "module": "crm", "description": "View CRM leads and opportunities"},
    {"codename": PermissionCodename.CRM_MANAGE, "module": "crm", "description": "Create and manage CRM records"},
    {"codename": PermissionCodename.QUOTES_VIEW, "module": "quotes", "description": "View quotations"},
    {"codename": PermissionCodename.QUOTES_MANAGE, "module": "quotes", "description": "Create and manage quotations"},
    {"codename": PermissionCodename.QUOTES_APPROVE, "module": "quotes", "description": "Approve or reject quotations"},
    {"codename": PermissionCodename.PROCUREMENT_VIEW, "module": "procurement", "description": "View procurement dashboard and requisitions"},
    {"codename": PermissionCodename.PROCUREMENT_MANAGE, "module": "procurement", "description": "Create and manage purchase requisitions and POs"},
    {"codename": PermissionCodename.PROCUREMENT_APPROVE, "module": "procurement", "description": "Approve purchase requisitions and POs"},
    {"codename": PermissionCodename.SUPPLIER_PORTAL, "module": "procurement", "description": "Supplier portal access"},
    {"codename": PermissionCodename.WMS_VIEW, "module": "wms", "description": "View WMS dashboard and bin locations"},
    {"codename": PermissionCodename.WMS_MANAGE, "module": "wms", "description": "Manage transfers, picks, and cycle counts"},
    {"codename": PermissionCodename.WMS_APPROVE, "module": "wms", "description": "Approve transfers and adjustments"},
    {"codename": PermissionCodename.WMS_EXECUTE, "module": "wms", "description": "Execute picks, putaway, and counts"},
    {"codename": PermissionCodename.ACCOUNTING_VIEW, "module": "accounting", "description": "View chart of accounts, journals, and financial reports"},
    {"codename": PermissionCodename.ACCOUNTING_MANAGE, "module": "accounting", "description": "Create draft journal entries and manage COA"},
    {"codename": PermissionCodename.ACCOUNTING_POST, "module": "accounting", "description": "Post journals and close accounting periods"},
    {"codename": PermissionCodename.RECEIVABLES_VIEW, "module": "receivables", "description": "View customer invoices, statements, and AR reports"},
    {"codename": PermissionCodename.RECEIVABLES_MANAGE, "module": "receivables", "description": "Create and manage customer invoices and payments"},
    {"codename": PermissionCodename.RECEIVABLES_APPROVE, "module": "receivables", "description": "Approve credit notes and high-value AR actions"},
    {"codename": PermissionCodename.PAYABLES_VIEW, "module": "payables", "description": "View supplier invoices, statements, and AP reports"},
    {"codename": PermissionCodename.PAYABLES_MANAGE, "module": "payables", "description": "Create and manage supplier invoices and payments"},
    {"codename": PermissionCodename.PAYABLES_APPROVE, "module": "payables", "description": "Approve supplier invoices and debit notes"},
    {"codename": PermissionCodename.HRM_VIEW, "module": "hrm", "description": "View employees, attendance, leave, and HR reports"},
    {"codename": PermissionCodename.HRM_MANAGE, "module": "hrm", "description": "Manage employees, documents, attendance, and assets"},
    {"codename": PermissionCodename.HRM_APPROVE, "module": "hrm", "description": "Approve leave requests"},
    {"codename": PermissionCodename.HRM_SELF, "module": "hrm", "description": "Self-service clock in/out and leave submission"},
    {"codename": PermissionCodename.PAYROLL_VIEW, "module": "payroll", "description": "View payroll periods, payslips, and reports"},
    {"codename": PermissionCodename.PAYROLL_MANAGE, "module": "payroll", "description": "Manage salary structures, calculate payroll, and adjustments"},
    {"codename": PermissionCodename.PAYROLL_APPROVE, "module": "payroll", "description": "Approve payroll runs"},
    {"codename": PermissionCodename.PAYROLL_POST, "module": "payroll", "description": "Post payroll runs to general ledger"},
)

_ALL_PERMISSIONS = frozenset(p["codename"] for p in SYSTEM_PERMISSIONS)

INTERNAL_ROLES = frozenset({
    RoleSlug.SUPER_ADMIN,
    RoleSlug.ADMIN,
    RoleSlug.MANAGER,
    RoleSlug.WAREHOUSE_MANAGER,
    RoleSlug.SALES_REP,
    RoleSlug.CUSTOMER_SERVICE,
    RoleSlug.TRADE_REVIEWER,
    RoleSlug.PROCUREMENT_OFFICER,
    RoleSlug.PROCUREMENT_MANAGER,
    RoleSlug.WAREHOUSE_OPERATOR,
    RoleSlug.FINANCE_USER,
    RoleSlug.FINANCE_MANAGER,
    RoleSlug.HR_OFFICER,
    RoleSlug.HR_MANAGER,
    RoleSlug.DEPARTMENT_MANAGER,
    RoleSlug.EMPLOYEE,
    RoleSlug.PAYROLL_OFFICER,
    RoleSlug.PAYROLL_MANAGER,
    RoleSlug.STAFF,
})

SUPPLIER_ROLES = frozenset({
    RoleSlug.SUPPLIER_USER,
})

CUSTOMER_ROLES = frozenset({
    RoleSlug.CUSTOMER,
    RoleSlug.TRADE_CUSTOMER,
})

_MANAGER_PERMS = frozenset({
    PermissionCodename.DASHBOARD_VIEW,
    PermissionCodename.ANALYTICS_VIEW,
    PermissionCodename.REPORTS_VIEW,
    PermissionCodename.REPORTS_EXPORT,
    PermissionCodename.CATALOG_VIEW,
    PermissionCodename.CATALOG_MANAGE,
    PermissionCodename.INVENTORY_VIEW,
    PermissionCodename.ORDERS_VIEW,
    PermissionCodename.ORDERS_MANAGE,
    PermissionCodename.CUSTOMERS_VIEW,
    PermissionCodename.CUSTOMERS_MANAGE,
    PermissionCodename.TRADE_VIEW,
    PermissionCodename.SUPPLIERS_VIEW,
    PermissionCodename.SUPPLIERS_MANAGE,
    PermissionCodename.SETTINGS_VIEW,
    PermissionCodename.CRM_VIEW,
    PermissionCodename.CRM_MANAGE,
    PermissionCodename.QUOTES_VIEW,
    PermissionCodename.QUOTES_MANAGE,
    PermissionCodename.QUOTES_APPROVE,
    PermissionCodename.PROCUREMENT_VIEW,
    PermissionCodename.PROCUREMENT_MANAGE,
    PermissionCodename.PROCUREMENT_APPROVE,
    PermissionCodename.ACCOUNTING_VIEW,
    PermissionCodename.ACCOUNTING_MANAGE,
    PermissionCodename.ACCOUNTING_POST,
    PermissionCodename.RECEIVABLES_VIEW,
    PermissionCodename.RECEIVABLES_MANAGE,
    PermissionCodename.RECEIVABLES_APPROVE,
    PermissionCodename.PAYABLES_VIEW,
    PermissionCodename.PAYABLES_MANAGE,
    PermissionCodename.PAYABLES_APPROVE,
    PermissionCodename.HRM_VIEW,
    PermissionCodename.HRM_MANAGE,
    PermissionCodename.HRM_APPROVE,
    PermissionCodename.PAYROLL_VIEW,
    PermissionCodename.PAYROLL_MANAGE,
    PermissionCodename.PAYROLL_APPROVE,
    PermissionCodename.PAYROLL_POST,
})

ROLE_PERMISSIONS: dict[str, frozenset[str]] = {
    RoleSlug.SUPER_ADMIN: _ALL_PERMISSIONS,
    RoleSlug.ADMIN: _ALL_PERMISSIONS - frozenset({PermissionCodename.USERS_MANAGE}),
    RoleSlug.MANAGER: _MANAGER_PERMS,
    RoleSlug.STAFF: _MANAGER_PERMS,
    RoleSlug.WAREHOUSE_MANAGER: frozenset({
        PermissionCodename.DASHBOARD_VIEW,
        PermissionCodename.INVENTORY_VIEW,
        PermissionCodename.INVENTORY_MANAGE,
        PermissionCodename.WAREHOUSE_VIEW,
        PermissionCodename.WAREHOUSE_MANAGE,
        PermissionCodename.ORDERS_VIEW,
        PermissionCodename.SUPPLIERS_VIEW,
        PermissionCodename.CATALOG_VIEW,
        PermissionCodename.PROCUREMENT_VIEW,
        PermissionCodename.WMS_VIEW,
        PermissionCodename.WMS_MANAGE,
        PermissionCodename.WMS_APPROVE,
        PermissionCodename.WMS_EXECUTE,
    }),
    RoleSlug.WAREHOUSE_OPERATOR: frozenset({
        PermissionCodename.DASHBOARD_VIEW,
        PermissionCodename.INVENTORY_VIEW,
        PermissionCodename.WAREHOUSE_VIEW,
        PermissionCodename.WMS_VIEW,
        PermissionCodename.WMS_EXECUTE,
    }),
    RoleSlug.PROCUREMENT_OFFICER: frozenset({
        PermissionCodename.DASHBOARD_VIEW,
        PermissionCodename.CATALOG_VIEW,
        PermissionCodename.SUPPLIERS_VIEW,
        PermissionCodename.INVENTORY_VIEW,
        PermissionCodename.PROCUREMENT_VIEW,
        PermissionCodename.PROCUREMENT_MANAGE,
    }),
    RoleSlug.PROCUREMENT_MANAGER: frozenset({
        PermissionCodename.DASHBOARD_VIEW,
        PermissionCodename.CATALOG_VIEW,
        PermissionCodename.SUPPLIERS_VIEW,
        PermissionCodename.SUPPLIERS_MANAGE,
        PermissionCodename.INVENTORY_VIEW,
        PermissionCodename.REPORTS_VIEW,
        PermissionCodename.PROCUREMENT_VIEW,
        PermissionCodename.PROCUREMENT_MANAGE,
        PermissionCodename.PROCUREMENT_APPROVE,
    }),
    RoleSlug.SUPPLIER_USER: frozenset({
        PermissionCodename.SUPPLIER_PORTAL,
    }),
    RoleSlug.SALES_REP: frozenset({
        PermissionCodename.DASHBOARD_VIEW,
        PermissionCodename.ANALYTICS_VIEW,
        PermissionCodename.CATALOG_VIEW,
        PermissionCodename.ORDERS_VIEW,
        PermissionCodename.ORDERS_MANAGE,
        PermissionCodename.CUSTOMERS_VIEW,
        PermissionCodename.TRADE_VIEW,
        PermissionCodename.REPORTS_VIEW,
        PermissionCodename.CRM_VIEW,
        PermissionCodename.CRM_MANAGE,
        PermissionCodename.QUOTES_VIEW,
        PermissionCodename.QUOTES_MANAGE,
    }),
    RoleSlug.CUSTOMER_SERVICE: frozenset({
        PermissionCodename.DASHBOARD_VIEW,
        PermissionCodename.ORDERS_VIEW,
        PermissionCodename.ORDERS_MANAGE,
        PermissionCodename.CUSTOMERS_VIEW,
        PermissionCodename.CUSTOMERS_MANAGE,
        PermissionCodename.TRADE_VIEW,
        PermissionCodename.CATALOG_VIEW,
    }),
    RoleSlug.TRADE_REVIEWER: frozenset({
        PermissionCodename.DASHBOARD_VIEW,
        PermissionCodename.TRADE_VIEW,
        PermissionCodename.TRADE_APPROVE,
        PermissionCodename.CUSTOMERS_VIEW,
    }),
    RoleSlug.FINANCE_USER: frozenset({
        PermissionCodename.DASHBOARD_VIEW,
        PermissionCodename.REPORTS_VIEW,
        PermissionCodename.ACCOUNTING_VIEW,
        PermissionCodename.ACCOUNTING_MANAGE,
        PermissionCodename.RECEIVABLES_VIEW,
        PermissionCodename.RECEIVABLES_MANAGE,
        PermissionCodename.PAYABLES_VIEW,
        PermissionCodename.PAYABLES_MANAGE,
    }),
    RoleSlug.FINANCE_MANAGER: frozenset({
        PermissionCodename.DASHBOARD_VIEW,
        PermissionCodename.REPORTS_VIEW,
        PermissionCodename.REPORTS_EXPORT,
        PermissionCodename.ACCOUNTING_VIEW,
        PermissionCodename.ACCOUNTING_MANAGE,
        PermissionCodename.ACCOUNTING_POST,
        PermissionCodename.RECEIVABLES_VIEW,
        PermissionCodename.RECEIVABLES_MANAGE,
        PermissionCodename.RECEIVABLES_APPROVE,
        PermissionCodename.PAYABLES_VIEW,
        PermissionCodename.PAYABLES_MANAGE,
        PermissionCodename.PAYABLES_APPROVE,
        PermissionCodename.PAYROLL_VIEW,
        PermissionCodename.PAYROLL_MANAGE,
        PermissionCodename.PAYROLL_APPROVE,
        PermissionCodename.PAYROLL_POST,
    }),
    RoleSlug.HR_OFFICER: frozenset({
        PermissionCodename.DASHBOARD_VIEW,
        PermissionCodename.HRM_VIEW,
        PermissionCodename.HRM_MANAGE,
    }),
    RoleSlug.HR_MANAGER: frozenset({
        PermissionCodename.DASHBOARD_VIEW,
        PermissionCodename.REPORTS_VIEW,
        PermissionCodename.HRM_VIEW,
        PermissionCodename.HRM_MANAGE,
        PermissionCodename.HRM_APPROVE,
        PermissionCodename.PAYROLL_VIEW,
        PermissionCodename.PAYROLL_APPROVE,
    }),
    RoleSlug.PAYROLL_OFFICER: frozenset({
        PermissionCodename.DASHBOARD_VIEW,
        PermissionCodename.PAYROLL_VIEW,
        PermissionCodename.PAYROLL_MANAGE,
    }),
    RoleSlug.PAYROLL_MANAGER: frozenset({
        PermissionCodename.DASHBOARD_VIEW,
        PermissionCodename.REPORTS_VIEW,
        PermissionCodename.PAYROLL_VIEW,
        PermissionCodename.PAYROLL_MANAGE,
        PermissionCodename.PAYROLL_APPROVE,
        PermissionCodename.PAYROLL_POST,
    }),
    RoleSlug.DEPARTMENT_MANAGER: frozenset({
        PermissionCodename.DASHBOARD_VIEW,
        PermissionCodename.HRM_VIEW,
        PermissionCodename.HRM_APPROVE,
        PermissionCodename.HRM_SELF,
    }),
    RoleSlug.EMPLOYEE: frozenset({
        PermissionCodename.HRM_SELF,
    }),
    RoleSlug.TRADE_CUSTOMER: frozenset({
        PermissionCodename.STORE_CHECKOUT,
        PermissionCodename.STORE_TRADE_PRICING,
    }),
    RoleSlug.CUSTOMER: frozenset({
        PermissionCodename.STORE_CHECKOUT,
    }),
}
