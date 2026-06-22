import type { AuthMeResponse, AuthUser } from "@/lib/api/types/auth";
import { canAccessAdminPortal } from "@/lib/rbac/access";

type RedirectUser = Pick<AuthMeResponse, "roles" | "permissions"> | AuthUser;

/**
 * Customer → /account (or deep-link redirect).
 * Admin/staff → /admin-dashboard.
 */
export function resolvePostLoginRedirect(
  user: RedirectUser,
  redirectParam: string | null
): string {
  const isAdmin = canAccessAdminPortal(user.roles, user.permissions);

  if (isAdmin) {
    return "/admin-dashboard";
  }

  return redirectParam ?? "/account";
}
