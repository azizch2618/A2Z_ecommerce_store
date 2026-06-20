/** Permission codenames — must match backend `apps/accounts/rbac.py`. */

export const Permission = {
  DASHBOARD_VIEW: "dashboard.view",
  ANALYTICS_VIEW: "analytics.view",
  REPORTS_VIEW: "reports.view",
  REPORTS_EXPORT: "reports.export",
  CATALOG_VIEW: "catalog.view",
  CATALOG_MANAGE: "catalog.manage",
  INVENTORY_VIEW: "inventory.view",
  INVENTORY_MANAGE: "inventory.manage",
  WAREHOUSE_VIEW: "warehouse.view",
  WAREHOUSE_MANAGE: "warehouse.manage",
  ORDERS_VIEW: "orders.view",
  ORDERS_MANAGE: "orders.manage",
  CUSTOMERS_VIEW: "customers.view",
  CUSTOMERS_MANAGE: "customers.manage",
  TRADE_VIEW: "trade.view",
  TRADE_APPROVE: "trade.approve",
  SUPPLIERS_VIEW: "suppliers.view",
  SUPPLIERS_MANAGE: "suppliers.manage",
  SETTINGS_VIEW: "settings.view",
  SETTINGS_MANAGE: "settings.manage",
  USERS_MANAGE: "users.manage",
  STORE_CHECKOUT: "store.checkout",
  STORE_TRADE_PRICING: "store.trade_pricing",
  CRM_VIEW: "crm.view",
  CRM_MANAGE: "crm.manage",
  QUOTES_VIEW: "quotes.view",
  QUOTES_MANAGE: "quotes.manage",
  QUOTES_APPROVE: "quotes.approve",
} as const;

export type PermissionCodename = (typeof Permission)[keyof typeof Permission];

export const ALL_PERMISSIONS: PermissionCodename[] = Object.values(Permission);
