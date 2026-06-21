import type { PermissionCodename } from "@/lib/rbac/permissions";
import { Permission } from "@/lib/rbac/permissions";

export type AdminNavIcon =
  | "layout-dashboard"
  | "package"
  | "folder-tree"
  | "tag"
  | "warehouse"
  | "building-2"
  | "shopping-cart"
  | "users"
  | "handshake"
  | "truck"
  | "bar-chart-3"
  | "line-chart"
  | "contact-2"
  | "file-text"
  | "clipboard-list"
  | "boxes"
  | "users-round"
  | "settings";

export interface AdminNavItem {
  label: string;
  href: string;
  icon: AdminNavIcon;
  badge?: number;
  section?: string;
  /** RBAC permission required to see this nav item */
  permission: PermissionCodename;
}

export const adminNavItems: AdminNavItem[] = [
  { label: "Dashboard", href: "/admin-dashboard", icon: "layout-dashboard", permission: Permission.DASHBOARD_VIEW },
  { label: "Products", href: "/admin-dashboard/products", icon: "package", section: "Catalog", permission: Permission.CATALOG_VIEW },
  { label: "Categories", href: "/admin-dashboard/categories", icon: "folder-tree", section: "Catalog", permission: Permission.CATALOG_VIEW },
  { label: "Brands", href: "/admin-dashboard/brands", icon: "tag", section: "Catalog", permission: Permission.CATALOG_VIEW },
  { label: "Inventory", href: "/admin-dashboard/inventory", icon: "warehouse", section: "Operations", permission: Permission.INVENTORY_VIEW },
  { label: "Warehouses", href: "/admin-dashboard/warehouses", icon: "building-2", section: "Operations", permission: Permission.WAREHOUSE_VIEW },
  { label: "Orders", href: "/admin-dashboard/orders", icon: "shopping-cart", section: "Sales", badge: 12, permission: Permission.ORDERS_VIEW },
  { label: "Customers", href: "/admin-dashboard/customers", icon: "users", section: "Sales", permission: Permission.CUSTOMERS_VIEW },
  { label: "Trade Accounts", href: "/admin-dashboard/trade-accounts", icon: "handshake", section: "Sales", badge: 5, permission: Permission.TRADE_VIEW },
  { label: "CRM", href: "/admin-dashboard/crm", icon: "contact-2", section: "Sales", permission: Permission.CRM_VIEW },
  { label: "Quotes", href: "/admin-dashboard/quotes", icon: "file-text", section: "Sales", permission: Permission.QUOTES_VIEW },
  { label: "Procurement", href: "/admin-dashboard/procurement", icon: "clipboard-list", section: "Procurement", permission: Permission.PROCUREMENT_VIEW },
  { label: "WMS", href: "/admin-dashboard/wms", icon: "boxes", section: "Operations", permission: Permission.WMS_VIEW },
  { label: "HR", href: "/admin-dashboard/hrm", icon: "users-round", section: "People", permission: Permission.HRM_VIEW },
  { label: "Suppliers", href: "/admin-dashboard/suppliers", icon: "truck", section: "Procurement", permission: Permission.SUPPLIERS_VIEW },
  { label: "Reports", href: "/admin-dashboard/reports", icon: "bar-chart-3", section: "Insights", permission: Permission.REPORTS_VIEW },
  { label: "Analytics", href: "/admin-dashboard/analytics", icon: "line-chart", section: "Insights", permission: Permission.ANALYTICS_VIEW },
  { label: "Settings", href: "/admin-dashboard/settings", icon: "settings", section: "System", permission: Permission.SETTINGS_VIEW },
];

export const adminUser = {
  name: "Sarah Mitchell",
  role: "Operations Manager",
  email: "sarah.mitchell@a2ztools.com.au",
  initials: "SM",
};
