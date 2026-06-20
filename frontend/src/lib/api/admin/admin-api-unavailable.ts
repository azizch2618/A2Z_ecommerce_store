import { logAdminApiFailure } from "./log-admin-api-error";

export class AdminApiUnavailableError extends Error {
  readonly feature: string;

  constructor(feature: string) {
    super(`Admin API for ${feature} is not available.`);
    this.name = "AdminApiUnavailableError";
    this.feature = feature;
  }
}

export function throwAdminApiUnavailable(feature: string): never {
  const error = new AdminApiUnavailableError(feature);
  logAdminApiFailure(feature, error);
  throw error;
}
