import { STORAGE_KEYS } from "../config";

/** Cookie set on the frontend origin so Next.js middleware can detect a session. */
export const SESSION_COOKIE_NAME = "a2z_session";

/** HttpOnly access cookie name (set by API when using same-site proxy or shared domain). */
export const ACCESS_COOKIE_NAME = "a2z_access";

export interface StoredTokens {
  access: string;
  refresh: string;
}

let inMemoryAccessToken: string | null = null;
let inMemoryRefreshToken: string | null = null;

function setSessionCookie(): void {
  if (typeof document === "undefined") {
    return;
  }
  const secure = window.location.protocol === "https:" ? "; Secure" : "";
  document.cookie = `${SESSION_COOKIE_NAME}=1; Path=/; SameSite=Lax${secure}`;
}

function clearSessionCookie(): void {
  if (typeof document === "undefined") {
    return;
  }
  document.cookie = `${SESSION_COOKIE_NAME}=; Path=/; Max-Age=0`;
}

/** Access token for Authorization header (dev cross-origin) or when returned in login body. */
export function getAccessToken(): string | null {
  if (typeof window === "undefined") {
    return null;
  }
  return inMemoryAccessToken;
}

/** Refresh token for token rotation when cookies are not sent cross-origin. */
export function getRefreshToken(): string | null {
  if (typeof window === "undefined") {
    return null;
  }
  return inMemoryRefreshToken;
}

/**
 * Persist session after login/register.
 * Stores in-memory JWTs when the API returns them; always sets the frontend session cookie
 * so Next.js middleware and route guards can detect an authenticated session.
 */
export function setTokens(tokens: StoredTokens): void {
  if (typeof window === "undefined") {
    return;
  }
  inMemoryAccessToken = tokens.access || null;
  inMemoryRefreshToken = tokens.refresh || null;
  setSessionCookie();
  clearLegacyTokenStorage();
}

export function clearTokens(): void {
  if (typeof window === "undefined") {
    return;
  }
  inMemoryAccessToken = null;
  inMemoryRefreshToken = null;
  clearSessionCookie();
  clearLegacyTokenStorage();
}

function clearLegacyTokenStorage(): void {
  localStorage.removeItem(STORAGE_KEYS.accessToken);
  localStorage.removeItem(STORAGE_KEYS.refreshToken);
}

export function hasAuthTokens(): boolean {
  if (typeof document === "undefined") {
    return false;
  }
  return (
    document.cookie.includes(`${SESSION_COOKIE_NAME}=`) ||
    inMemoryAccessToken !== null
  );
}
