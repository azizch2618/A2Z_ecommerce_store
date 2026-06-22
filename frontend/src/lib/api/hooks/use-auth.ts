"use client";

import {
  useMutation,
  useQuery,
  useQueryClient,
  type UseQueryOptions,
} from "@tanstack/react-query";

import { useAuthStore } from "../auth/auth-store";
import { authDebug } from "@/lib/auth/auth-debug";
import { hasAuthTokens } from "../auth/token-storage";
import {
  createAddress,
  deleteAddress,
  fetchAddresses,
  fetchCurrentUser,
  forgotPassword,
  login,
  logout,
  register,
  resendVerificationEmail,
  updateAddress,
  updateProfile,
  verifyEmail,
} from "../services/auth.service";
import type {
  AuthMeResponse,
  LoginPayload,
  RegisterPayload,
  UpdateProfilePayload,
} from "../types/auth";
import type { ApiAddress } from "../types/common";
import { queryKeys } from "./query-keys";

export function useCurrentUser(
  options?: Omit<UseQueryOptions<AuthMeResponse, Error>, "queryKey" | "queryFn">
) {
  const isHydrated = useAuthStore((s) => s.isHydrated);

  return useQuery({
    queryKey: queryKeys.auth.me(),
    queryFn: fetchCurrentUser,
    enabled: isHydrated && hasAuthTokens(),
    staleTime: 60_000,
    retry: false,
    ...options,
  });
}

export function useAddresses(
  options?: Omit<
    UseQueryOptions<{ data: ApiAddress[] }, Error>,
    "queryKey" | "queryFn"
  >
) {
  return useQuery({
    queryKey: queryKeys.auth.addresses(),
    queryFn: fetchAddresses,
    enabled: hasAuthTokens(),
    ...options,
  });
}

export function useLogin() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: LoginPayload) => login(payload),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: queryKeys.auth.all });
      await queryClient.invalidateQueries({ queryKey: queryKeys.cart.all });
    },
  });
}

export function useRegister() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: RegisterPayload) => register(payload),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: queryKeys.auth.all });
      await queryClient.invalidateQueries({ queryKey: queryKeys.cart.all });
    },
  });
}

export function useLogout() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: logout,
    onSuccess: () => {
      queryClient.clear();
    },
  });
}

export function useUpdateProfile() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: UpdateProfilePayload) => updateProfile(payload),
    onSuccess: (user) => {
      queryClient.setQueryData(queryKeys.auth.me(), user);
    },
  });
}

export function useCreateAddress() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: ApiAddress) => createAddress(payload),
    onSuccess: () => {
      void queryClient.invalidateQueries({
        queryKey: queryKeys.auth.addresses(),
      });
    },
  });
}

export function useUpdateAddress() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      addressId,
      payload,
    }: {
      addressId: string;
      payload: Partial<ApiAddress>;
    }) => updateAddress(addressId, payload),
    onSuccess: () => {
      void queryClient.invalidateQueries({
        queryKey: queryKeys.auth.addresses(),
      });
    },
  });
}

export function useDeleteAddress() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (addressId: string) => deleteAddress(addressId),
    onSuccess: () => {
      void queryClient.invalidateQueries({
        queryKey: queryKeys.auth.addresses(),
      });
    },
  });
}

export function useForgotPassword() {
  return useMutation({
    mutationFn: (email: string) => forgotPassword(email),
  });
}

export function useVerifyEmail() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: { uid: string; token: string }) => verifyEmail(payload),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: queryKeys.auth.all });
    },
  });
}

export function useResendVerificationEmail() {
  return useMutation({
    mutationFn: resendVerificationEmail,
  });
}

/** Convenience selector for auth state */
export function useAuth() {
  const user = useAuthStore((s) => s.user);
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const isHydrated = useAuthStore((s) => s.isHydrated);
  const { data: me, isLoading, error } = useCurrentUser({
    enabled: isHydrated && hasAuthTokens() && !user,
  });

  return {
    user: user ?? me ?? null,
    isAuthenticated: isAuthenticated || Boolean(me),
    isLoading: !isHydrated || isLoading,
    error,
  };
}
