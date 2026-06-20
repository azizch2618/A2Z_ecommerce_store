import { isApiError } from "../errors";

export function logAdminApiFailure(context: string, error: unknown): void {
  const message = isApiError(error)
    ? `[admin-api] ${context}: ${error.message} (status ${error.status}, code ${error.code})`
    : `[admin-api] ${context}: ${
        error instanceof Error ? error.message : "Unknown error"
      }`;

  console.error(message, error);
}

export async function withAdminApiLog<T>(
  context: string,
  fn: () => Promise<T>
): Promise<T> {
  try {
    return await fn();
  } catch (error) {
    logAdminApiFailure(context, error);
    throw error;
  }
}
