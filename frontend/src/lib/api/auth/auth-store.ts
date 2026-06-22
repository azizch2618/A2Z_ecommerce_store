import { create } from "zustand";
import { persist } from "zustand/middleware";

import { authDebug } from "@/lib/auth/auth-debug";
import type { AuthMeResponse } from "../types/auth";
import { clearTokens, hasAuthTokens, setTokens as persistSessionTokens } from "./token-storage";
interface AuthState {
  user: AuthMeResponse | null;
  isAuthenticated: boolean;
  isHydrated: boolean;
  setUser: (user: AuthMeResponse | null) => void;
  setTokens: (access: string, refresh: string) => void;
  logout: () => void;
  markHydrated: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      isAuthenticated: false,
      isHydrated: false,
      setUser: (user) => {
        authDebug("auth-store", "setUser", {
          email: user?.email ?? null,
          roles: user?.roles,
        });
        set({ user, isAuthenticated: user !== null });
      },
      setTokens: (_access, _refresh) => {
        persistSessionTokens({ access: _access, refresh: _refresh });
        authDebug("auth-store", "setTokens — session marked authenticated");
        set({ isAuthenticated: true });
      },      logout: () => {
        clearTokens();
        set({ user: null, isAuthenticated: false });
      },
      markHydrated: () => set({ isHydrated: true }),
    }),
    {
      name: "a2z-auth-store",
      partialize: (state) => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
      onRehydrateStorage: () => (state) => {
        if (state) {
          state.isAuthenticated =
            state.isAuthenticated || hasAuthTokens() || Boolean(state.user);
          state.markHydrated();
        }
      },
    }
  )
);
