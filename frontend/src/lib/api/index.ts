/**
 * A2Z Tools API Integration Layer
 *
 * Enterprise-grade client for Django REST Framework backend.
 * @example
 * ```ts
 * import { fetchProducts, useProductDetails, useAddToCart } from "@/lib/api";
 * ```
 */

export {
  API_BASE_URL,
  API_DEFAULTS,
  API_ENDPOINTS,
  API_VERSION,
  STORAGE_KEYS,
} from "./config";

export { apiClient, apiGet, apiPost, apiPatch, apiDelete } from "./client";

export {
  ApiError,
  isApiError,
  parseApiError,
  getFieldErrors,
  type ApiErrorCode,
} from "./errors";

export {
  getOrCreateSessionKey,
  getSessionKey,
  clearSessionKey,
} from "./session";

export { createQueryClient } from "./query-client";

export {
  getAccessToken,
  getRefreshToken,
  setTokens,
  clearTokens,
  hasAuthTokens,
} from "./auth/token-storage";

export { useAuthStore } from "./auth/auth-store";

export type * from "./types";

export * from "./services";

export * from "./hooks";
