/** Role slugs — must match backend `apps/accounts/constants.py`. */

export const Role = {
  SUPER_ADMIN: "super-admin",
  ADMIN: "admin",
  MANAGER: "manager",
  WAREHOUSE_MANAGER: "warehouse-manager",
  SALES_REP: "sales-representative",
  CUSTOMER_SERVICE: "customer-service",
  TRADE_REVIEWER: "trade-reviewer",
  TRADE_CUSTOMER: "trade-customer",
  PROCUREMENT_OFFICER: "procurement-officer",
  PROCUREMENT_MANAGER: "procurement-manager",
  WAREHOUSE_OPERATOR: "warehouse-operator",
  HR_OFFICER: "hr-officer",
  HR_MANAGER: "hr-manager",
  DEPARTMENT_MANAGER: "department-manager",
  EMPLOYEE: "employee",
  SUPPLIER_USER: "supplier-user",
  CUSTOMER: "customer",
  STAFF: "staff",
} as const;

export type RoleSlug = (typeof Role)[keyof typeof Role];

export const ADMIN_PORTAL_ROLES: RoleSlug[] = [
  Role.SUPER_ADMIN,
  Role.ADMIN,
  Role.MANAGER,
  Role.WAREHOUSE_MANAGER,
  Role.SALES_REP,
  Role.CUSTOMER_SERVICE,
  Role.TRADE_REVIEWER,
  Role.PROCUREMENT_OFFICER,
  Role.PROCUREMENT_MANAGER,
  Role.WAREHOUSE_OPERATOR,
  Role.HR_OFFICER,
  Role.HR_MANAGER,
  Role.DEPARTMENT_MANAGER,
  Role.STAFF,
];

export const ROLE_LABELS: Record<RoleSlug, string> = {
  [Role.SUPER_ADMIN]: "Super Admin",
  [Role.ADMIN]: "Admin",
  [Role.MANAGER]: "Manager",
  [Role.WAREHOUSE_MANAGER]: "Warehouse Manager",
  [Role.SALES_REP]: "Sales Representative",
  [Role.CUSTOMER_SERVICE]: "Customer Service",
  [Role.TRADE_REVIEWER]: "Trade Reviewer",
  [Role.PROCUREMENT_OFFICER]: "Procurement Officer",
  [Role.PROCUREMENT_MANAGER]: "Procurement Manager",
  [Role.WAREHOUSE_OPERATOR]: "Warehouse Operator",
  [Role.HR_OFFICER]: "HR Officer",
  [Role.HR_MANAGER]: "HR Manager",
  [Role.DEPARTMENT_MANAGER]: "Department Manager",
  [Role.EMPLOYEE]: "Employee",
  [Role.SUPPLIER_USER]: "Supplier User",
  [Role.TRADE_CUSTOMER]: "Trade Customer",
  [Role.CUSTOMER]: "Customer",
  [Role.STAFF]: "Staff",
};

export function getPrimaryRoleLabel(roles: string[]): string {
  for (const slug of ADMIN_PORTAL_ROLES) {
    if (roles.includes(slug)) {
      return ROLE_LABELS[slug];
    }
  }
  if (roles.includes(Role.TRADE_CUSTOMER)) return ROLE_LABELS[Role.TRADE_CUSTOMER];
  if (roles.includes(Role.CUSTOMER)) return ROLE_LABELS[Role.CUSTOMER];
  return "User";
}
