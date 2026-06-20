const STORAGE_KEY = "a2z-recent-searches";
const MAX_RECENT_SEARCHES = 5;

function isBrowser(): boolean {
  return typeof window !== "undefined";
}

export function getRecentSearches(): string[] {
  if (!isBrowser()) return [];

  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (!raw) return [];
    const parsed: unknown = JSON.parse(raw);
    if (!Array.isArray(parsed)) return [];
    return parsed.filter((item): item is string => typeof item === "string").slice(0, MAX_RECENT_SEARCHES);
  } catch {
    return [];
  }
}

export function addRecentSearch(query: string): string[] {
  const trimmed = query.trim();
  if (!trimmed || !isBrowser()) return getRecentSearches();

  const next = [trimmed, ...getRecentSearches().filter((item) => item !== trimmed)].slice(
    0,
    MAX_RECENT_SEARCHES
  );

  try {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
  } catch {
    // Ignore quota / privacy mode errors
  }

  return next;
}

export function clearRecentSearches(): void {
  if (!isBrowser()) return;
  try {
    window.localStorage.removeItem(STORAGE_KEY);
  } catch {
    // Ignore
  }
}

export { MAX_RECENT_SEARCHES };
