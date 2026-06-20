/**
 * Admin demo mode is disabled in production builds regardless of env var.
 */
export function isAdminDemoEnabled(): boolean {
  if (process.env.NODE_ENV === "production") {
    return false;
  }
  return process.env.NEXT_PUBLIC_ADMIN_DEMO === "true";
}
