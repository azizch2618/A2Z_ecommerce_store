"""System role identifiers for RBAC."""

from enum import StrEnum


class RoleSlug(StrEnum):
    SUPER_ADMIN = "super-admin"
    ADMIN = "admin"
    MANAGER = "manager"
    WAREHOUSE_MANAGER = "warehouse-manager"
    WAREHOUSE_OPERATOR = "warehouse-operator"
    SALES_REP = "sales-representative"
    CUSTOMER_SERVICE = "customer-service"
    TRADE_REVIEWER = "trade-reviewer"
    PROCUREMENT_OFFICER = "procurement-officer"
    PROCUREMENT_MANAGER = "procurement-manager"
    FINANCE_USER = "finance-user"
    FINANCE_MANAGER = "finance-manager"
    SUPPLIER_USER = "supplier-user"
    TRADE_CUSTOMER = "trade-customer"
    CUSTOMER = "customer"
    # Legacy — migrated to manager; kept for backward compatibility
    STAFF = "staff"


SYSTEM_ROLES: tuple[dict[str, str | bool], ...] = (
    {
        "name": "Super Admin",
        "slug": RoleSlug.SUPER_ADMIN,
        "description": "Full system access including user and role management.",
        "is_system": True,
    },
    {
        "name": "Admin",
        "slug": RoleSlug.ADMIN,
        "description": "Platform administration without user/role management.",
        "is_system": True,
    },
    {
        "name": "Manager",
        "slug": RoleSlug.MANAGER,
        "description": "Operational oversight across catalog, orders, and customers.",
        "is_system": True,
    },
    {
        "name": "Warehouse Manager",
        "slug": RoleSlug.WAREHOUSE_MANAGER,
        "description": "Inventory, warehouses, and fulfillment operations.",
        "is_system": True,
    },
    {
        "name": "Warehouse Operator",
        "slug": RoleSlug.WAREHOUSE_OPERATOR,
        "description": "Floor operations — pick, putaway, and cycle counts.",
        "is_system": True,
    },
    {
        "name": "Sales Representative",
        "slug": RoleSlug.SALES_REP,
        "description": "Sales pipeline, orders, and trade account visibility.",
        "is_system": True,
    },
    {
        "name": "Customer Service",
        "slug": RoleSlug.CUSTOMER_SERVICE,
        "description": "Customer support, order updates, and account assistance.",
        "is_system": True,
    },
    {
        "name": "Trade Reviewer",
        "slug": RoleSlug.TRADE_REVIEWER,
        "description": "Review and approve/reject B2B trade account applications.",
        "is_system": True,
    },
    {
        "name": "Procurement Officer",
        "slug": RoleSlug.PROCUREMENT_OFFICER,
        "description": "Create and manage purchase requisitions and orders.",
        "is_system": True,
    },
    {
        "name": "Procurement Manager",
        "slug": RoleSlug.PROCUREMENT_MANAGER,
        "description": "Approve requisitions and oversee procurement spend.",
        "is_system": True,
    },
    {
        "name": "Finance User",
        "slug": RoleSlug.FINANCE_USER,
        "description": "View financial reports and create draft journal entries.",
        "is_system": True,
    },
    {
        "name": "Finance Manager",
        "slug": RoleSlug.FINANCE_MANAGER,
        "description": "Post journals, close periods, and oversee accounting.",
        "is_system": True,
    },
    {
        "name": "Supplier User",
        "slug": RoleSlug.SUPPLIER_USER,
        "description": "Supplier portal access for purchase orders and documents.",
        "is_system": True,
    },
    {
        "name": "Trade Customer",
        "slug": RoleSlug.TRADE_CUSTOMER,
        "description": "B2B trade account with trade pricing on storefront.",
        "is_system": True,
    },
    {
        "name": "Customer",
        "slug": RoleSlug.CUSTOMER,
        "description": "Retail storefront customer.",
        "is_system": True,
    },
    {
        "name": "Staff",
        "slug": RoleSlug.STAFF,
        "description": "Legacy staff role — equivalent to Manager.",
        "is_system": True,
    },
)

TRADE_CUSTOMER_TYPES = frozenset({"trade", "contractor", "business"})

# Roles that grant access to the admin dashboard
ADMIN_PORTAL_ROLES = frozenset({
    RoleSlug.SUPER_ADMIN,
    RoleSlug.ADMIN,
    RoleSlug.MANAGER,
    RoleSlug.WAREHOUSE_MANAGER,
    RoleSlug.WAREHOUSE_OPERATOR,
    RoleSlug.SALES_REP,
    RoleSlug.CUSTOMER_SERVICE,
    RoleSlug.TRADE_REVIEWER,
    RoleSlug.FINANCE_USER,
    RoleSlug.FINANCE_MANAGER,
    RoleSlug.STAFF,
})
