import type { AxiosError } from "axios";

import type { ApiErrorBody } from "./types/common";

export type ApiErrorCode =
  | "NETWORK_ERROR"
  | "TIMEOUT"
  | "VALIDATION_ERROR"
  | "UNAUTHORIZED"
  | "FORBIDDEN"
  | "NOT_FOUND"
  | "CONFLICT"
  | "BUSINESS_RULE"
  | "RATE_LIMITED"
  | "SERVER_ERROR"
  | "UNKNOWN";

/**
 * Normalised API error for consistent UI handling across the storefront and future ERP modules.
 */
export class ApiError extends Error {
  readonly code: ApiErrorCode;
  readonly status: number;
  readonly details?: ApiErrorBody["error"]["details"];

  constructor(
    message: string,
    options: {
      code: ApiErrorCode;
      status: number;
      details?: ApiErrorBody["error"]["details"];
      cause?: unknown;
    }
  ) {
    super(message, { cause: options.cause });
    this.name = "ApiError";
    this.code = options.code;
    this.status = options.status;
    this.details = options.details;
  }
}

function mapStatusToCode(status: number): ApiErrorCode {
  switch (status) {
    case 400:
      return "VALIDATION_ERROR";
    case 401:
      return "UNAUTHORIZED";
    case 403:
      return "FORBIDDEN";
    case 404:
      return "NOT_FOUND";
    case 409:
      return "CONFLICT";
    case 422:
      return "BUSINESS_RULE";
    case 429:
      return "RATE_LIMITED";
    default:
      return status >= 500 ? "SERVER_ERROR" : "UNKNOWN";
  }
}

export function isApiError(error: unknown): error is ApiError {
  return error instanceof ApiError;
}

export function parseApiError(error: unknown): ApiError {
  if (isApiError(error)) {
    return error;
  }

  if (isAxiosError(error)) {
    if (error.code === "ECONNABORTED") {
      return new ApiError("Request timed out. Please try again.", {
        code: "TIMEOUT",
        status: 0,
        cause: error,
      });
    }

    if (!error.response) {
      return new ApiError(
        "Unable to reach the server. Check your connection and try again.",
        { code: "NETWORK_ERROR", status: 0, cause: error }
      );
    }

    const { status, data } = error.response;
    const body = data as ApiErrorBody | undefined;
    const message =
      body?.error?.message ??
      error.message ??
      "An unexpected error occurred.";

    return new ApiError(message, {
      code: body?.error?.code
        ? (body.error.code as ApiErrorCode)
        : mapStatusToCode(status),
      status,
      details: body?.error?.details,
      cause: error,
    });
  }

  if (error instanceof Error) {
    return new ApiError(error.message, {
      code: "UNKNOWN",
      status: 0,
      cause: error,
    });
  }

  return new ApiError("An unexpected error occurred.", {
    code: "UNKNOWN",
    status: 0,
    cause: error,
  });
}

export function getFieldErrors(
  error: ApiError
): Record<string, string> | undefined {
  if (!error.details || Array.isArray(error.details)) {
    return undefined;
  }

  const result: Record<string, string> = {};
  for (const [field, messages] of Object.entries(error.details)) {
    if (Array.isArray(messages) && messages[0]) {
      result[field] = messages[0];
    } else if (typeof messages === "string") {
      result[field] = messages;
    }
  }
  return Object.keys(result).length > 0 ? result : undefined;
}

function isAxiosError(error: unknown): error is AxiosError {
  return (
    typeof error === "object" &&
    error !== null &&
    "isAxiosError" in error &&
    (error as AxiosError).isAxiosError === true
  );
}
