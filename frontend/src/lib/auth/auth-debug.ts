const AUTH_DEBUG =
  process.env.NODE_ENV === "development" ||
  process.env.NEXT_PUBLIC_AUTH_DEBUG === "true";

export function authDebug(
  scope: string,
  message: string,
  data?: Record<string, unknown>
): void {
  if (!AUTH_DEBUG) {
    return;
  }
  if (data) {
    console.info(`[auth:${scope}] ${message}`, data);
  } else {
    console.info(`[auth:${scope}] ${message}`);
  }
}
