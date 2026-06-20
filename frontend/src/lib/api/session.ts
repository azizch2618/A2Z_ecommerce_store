import { STORAGE_KEYS } from "./config";

const SESSION_KEY_PATTERN =
  /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;

function generateUuid(): string {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    return crypto.randomUUID();
  }
  return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, (char) => {
    const random = (Math.random() * 16) | 0;
    const value = char === "x" ? random : (random & 0x3) | 0x8;
    return value.toString(16);
  });
}

/**
 * Guest cart session key — sent as `X-Session-Key` per API spec.
 */
export function getOrCreateSessionKey(): string {
  if (typeof window === "undefined") {
    return "";
  }

  const existing = localStorage.getItem(STORAGE_KEYS.sessionKey);
  if (existing && SESSION_KEY_PATTERN.test(existing)) {
    return existing;
  }

  const sessionKey = generateUuid();
  localStorage.setItem(STORAGE_KEYS.sessionKey, sessionKey);
  return sessionKey;
}

export function getSessionKey(): string | null {
  if (typeof window === "undefined") {
    return null;
  }
  return localStorage.getItem(STORAGE_KEYS.sessionKey);
}

export function clearSessionKey(): void {
  if (typeof window === "undefined") {
    return;
  }
  localStorage.removeItem(STORAGE_KEYS.sessionKey);
}
