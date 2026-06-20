"use client";

import * as React from "react";
import { QueryClientProvider } from "@tanstack/react-query";
import { ReactQueryDevtools } from "@tanstack/react-query-devtools";

import { useAuthStore } from "@/lib/api/auth/auth-store";
import {
  getAccessToken,
  getRefreshToken,
  setTokens,
} from "@/lib/api/auth/token-storage";
import { createQueryClient } from "@/lib/api/query-client";

export function AppProviders({ children }: { children: React.ReactNode }) {
  const [queryClient] = React.useState(() => createQueryClient());
  const markHydrated = useAuthStore((s) => s.markHydrated);

  React.useEffect(() => {
    markHydrated();
    const access = getAccessToken();
    const refresh = getRefreshToken();
    if (access && refresh) {
      setTokens({ access, refresh });
    }
  }, [markHydrated]);

  return (
    <QueryClientProvider client={queryClient}>
      {children}
      {process.env.NODE_ENV === "development" ? (
        <ReactQueryDevtools initialIsOpen={false} buttonPosition="bottom-left" />
      ) : null}
    </QueryClientProvider>
  );
}
