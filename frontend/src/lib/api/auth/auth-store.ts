import { create } from "zustand";
import { persist } from "zustand/middleware";

import type { AuthMeResponse } from "../types/auth";
import { clearTokens, hasAuthTokens, setTokens } from "./token-storage";

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
      setUser: (user) =>
        set({ user, isAuthenticated: user !== null }),
      setTokens: (_access, _refresh) => {
        setTokens({ access: _access, refresh: _refresh });
        set({ isAuthenticated: true });
      },
      logout: () => {
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
