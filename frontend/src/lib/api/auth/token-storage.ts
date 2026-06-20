import { STORAGE_KEYS } from "../config";

/** Cookie set on the frontend origin so Next.js middleware can detect a session. */
export const SESSION_COOKIE_NAME = "a2z_session";

/** HttpOnly access cookie name (set by API; readable by middleware when domain is shared). */
export const ACCESS_COOKIE_NAME = "a2z_access";

export interface StoredTokens {
  access: string;
  refresh: string;
}

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

/** @deprecated Tokens are stored in HttpOnly cookies by the API. */
export function getAccessToken(): string | null {
  return null;
}

/** @deprecated Tokens are stored in HttpOnly cookies by the API. */
export function getRefreshToken(): string | null {
  return null;
}

/** Mark the client session active after login/register (JWTs are HttpOnly on API). */
export function setTokens(_tokens: StoredTokens): void {
  if (typeof window === "undefined") {
    return;
  }
  setSessionCookie();
  clearLegacyTokenStorage();
}

export function clearTokens(): void {
  if (typeof window === "undefined") {
    return;
  }
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
  return document.cookie.includes(`${SESSION_COOKIE_NAME}=`);
}
