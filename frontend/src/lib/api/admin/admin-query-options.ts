import { hasAuthTokens } from "../auth/token-storage";
import { withAdminApiLog } from "./log-admin-api-error";

export function createAdminLiveQueryOptions<T>(
  context: string,
  queryKey: readonly unknown[],
  queryFn: () => Promise<T>,
  staleTime = 60_000
) {
  return {
    queryKey,
    queryFn: () => withAdminApiLog(context, queryFn),
    enabled: hasAuthTokens(),
    retry: false as const,
    staleTime,
  };
}
