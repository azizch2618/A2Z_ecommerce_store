import axios, {
  type AxiosInstance,
  type AxiosRequestConfig,
  type InternalAxiosRequestConfig,
} from "axios";

import { useAuthStore } from "./auth/auth-store";
import {
  clearTokens,
  getAccessToken,
  getRefreshToken,
  setTokens,
} from "./auth/token-storage";
import { authDebug } from "@/lib/auth/auth-debug";
import { API_BASE_URL, API_DEFAULTS, API_ENDPOINTS } from "./config";
import { parseApiError } from "./errors";
import { getOrCreateSessionKey } from "./session";
import type { RefreshTokenResponse } from "./types/auth";

type RetryableConfig = InternalAxiosRequestConfig & {
  _retry?: boolean;
};

let refreshPromise: Promise<boolean> | null = null;

async function refreshAccessToken(): Promise<boolean> {
  try {
    const refresh = getRefreshToken();
    const { data } = await axios.post<RefreshTokenResponse>(
      `${API_BASE_URL}${API_ENDPOINTS.auth.refresh}`,
      refresh ? { refresh } : {},
      {
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json",
          "Accept-Language": API_DEFAULTS.locale,
        },
        timeout: API_DEFAULTS.requestTimeoutMs,
        withCredentials: true,
      }
    );
    if (data.access) {
      setTokens({
        access: data.access,
        refresh: data.refresh ?? refresh ?? "",
      });
    }
    return true;
  } catch {
    authDebug("refresh", "token refresh failed — clearing session");
    clearTokens();
    useAuthStore.getState().logout();
    return false;
  }
}

function enqueueRefresh(): Promise<boolean> {
  if (!refreshPromise) {
    refreshPromise = refreshAccessToken().finally(() => {
      refreshPromise = null;
    });
  }
  return refreshPromise;
}

/**
 * Singleton Axios client for all Django REST API communication.
 * Uses HttpOnly JWT cookies (withCredentials) and guest session keys.
 */
export const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: API_DEFAULTS.requestTimeoutMs,
  withCredentials: true,
  headers: {
    Accept: "application/json",
    "Content-Type": "application/json",
    "Accept-Language": API_DEFAULTS.locale,
  },
});

apiClient.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const accessToken = getAccessToken();
  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`;
  }

  const includeSessionKey =
    !config.skipSessionKey && typeof window !== "undefined";

  if (includeSessionKey) {
    const sessionKey = getOrCreateSessionKey();
    if (sessionKey) {
      config.headers["X-Session-Key"] = sessionKey;
    }
  }

  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    config.headers["X-Request-Id"] = crypto.randomUUID();
  }

  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config as RetryableConfig | undefined;

    if (
      error.response?.status === 401 &&
      originalRequest &&
      !originalRequest._retry &&
      !originalRequest.url?.includes(API_ENDPOINTS.auth.refresh)
    ) {
      originalRequest._retry = true;
      const refreshed = await enqueueRefresh();

      if (refreshed) {
        return apiClient(originalRequest);
      }
    }

    return Promise.reject(parseApiError(error));
  }
);

/** Typed GET helper */
export async function apiGet<T>(
  url: string,
  config?: AxiosRequestConfig
): Promise<T> {
  const { data } = await apiClient.get<T>(url, config);
  return data;
}

/** Typed POST helper */
export async function apiPost<T, B = unknown>(
  url: string,
  body?: B,
  config?: AxiosRequestConfig
): Promise<T> {
  const { data } = await apiClient.post<T>(url, body, config);
  return data;
}

/** Typed PATCH helper */
export async function apiPatch<T, B = unknown>(
  url: string,
  body?: B,
  config?: AxiosRequestConfig
): Promise<T> {
  const { data } = await apiClient.patch<T>(url, body, config);
  return data;
}

/** Typed DELETE helper */
export async function apiDelete<T>(
  url: string,
  config?: AxiosRequestConfig
): Promise<T> {
  const { data } = await apiClient.delete<T>(url, config);
  return data;
}
