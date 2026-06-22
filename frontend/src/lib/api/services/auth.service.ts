import { apiDelete, apiGet, apiPatch, apiPost } from "../client";
import { API_ENDPOINTS } from "../config";
import { useAuthStore } from "../auth/auth-store";
import { hasAuthTokens } from "../auth/token-storage";
import { authDebug } from "@/lib/auth/auth-debug";
import { getSessionKey } from "../session";
import { mergeGuestCart } from "./cart.service";
import type {
  AddressListResponse,
  AuthMeResponse,
  LoginPayload,
  LoginResponse,
  MessageResponse,
  RegisterPayload,
  RegisterResponse,
  UpdateProfilePayload,
  VerifyEmailPayload,
  VerifyEmailResponse,
} from "../types/auth";
import type { ApiAddress } from "../types/common";

/** Authenticate and store JWT tokens */
export async function login(payload: LoginPayload): Promise<LoginResponse> {
  const data = await apiPost<LoginResponse, LoginPayload>(
    API_ENDPOINTS.auth.login,
    payload,
    { skipSessionKey: true }
  );

  useAuthStore.getState().setTokens(
    data.tokens?.access ?? "",
    data.tokens?.refresh ?? ""
  );

  authDebug("login", "session marked after login", {
    hasSessionCookie: hasAuthTokens(),
    email: data.user.email,
    roles: data.user.roles,
  });

  const sessionKey = getSessionKey();
  if (sessionKey) {
    try {
      await mergeGuestCart({ session_key: sessionKey });
    } catch {
      // Non-fatal — cart merge can fail if guest cart empty
    }
  }

  try {
    const user = await fetchCurrentUser();
    authDebug("login", "current user loaded", {
      email: user.email,
      roles: user.roles,
      permissions: user.permissions?.length ?? 0,
    });
  } catch (error) {
    authDebug("login", "current user fetch failed after login", {
      error: error instanceof Error ? error.message : String(error),
    });
  }

  return data;
}

/** Register new customer account */
export async function register(
  payload: RegisterPayload
): Promise<RegisterResponse> {
  const data = await apiPost<RegisterResponse, RegisterPayload>(
    API_ENDPOINTS.auth.register,
    payload,
    { skipSessionKey: true }
  );

  useAuthStore.getState().setTokens(
    data.tokens?.access ?? "",
    data.tokens?.refresh ?? ""
  );

  const sessionKey = getSessionKey();
  if (sessionKey) {
    try {
      await mergeGuestCart({ session_key: sessionKey });
    } catch {
      // Non-fatal — guest cart may be empty
    }
  }

  try {
    await fetchCurrentUser();
  } catch {
    // Tokens are stored; profile can load on next navigation.
  }

  return data;
}

/** Revoke refresh token and clear session cookies */
export async function logout(): Promise<void> {
  try {
    await apiPost(API_ENDPOINTS.auth.logout, {});
  } finally {
    useAuthStore.getState().logout();
  }
}

/** Fetch and cache current user profile */
export async function fetchCurrentUser(): Promise<AuthMeResponse> {
  authDebug("me", "fetching current user");
  const user = await apiGet<AuthMeResponse>(API_ENDPOINTS.auth.me);
  useAuthStore.getState().setUser(user);
  authDebug("me", "current user stored", {
    email: user.email,
    roles: user.roles,
  });
  return user;
}

/** Update profile fields */
export async function updateProfile(
  payload: UpdateProfilePayload
): Promise<AuthMeResponse> {
  const user = await apiPatch<AuthMeResponse, UpdateProfilePayload>(
    API_ENDPOINTS.auth.me,
    payload
  );
  useAuthStore.getState().setUser(user);
  return user;
}

/** List saved addresses */
export async function fetchAddresses(): Promise<AddressListResponse> {
  const rows = await apiGet<ApiAddress[]>(API_ENDPOINTS.customers.addresses);
  return {
    data: rows.map((row) => ({
      ...row,
      id: row.id ?? (row as ApiAddress & { public_id?: string }).public_id,
    })),
  };
}

/** Create address */
export async function createAddress(
  payload: ApiAddress
): Promise<ApiAddress> {
  return apiPost<ApiAddress, ApiAddress>(
    API_ENDPOINTS.customers.addresses,
    payload
  );
}

/** Update address */
export async function updateAddress(
  addressId: string,
  payload: Partial<ApiAddress>
): Promise<ApiAddress> {
  return apiPatch<ApiAddress, Partial<ApiAddress>>(
    API_ENDPOINTS.customers.address(addressId),
    payload
  );
}

/** Delete address */
export async function deleteAddress(addressId: string): Promise<void> {
  await apiDelete(API_ENDPOINTS.customers.address(addressId));
}

/** Request password reset email */
export async function forgotPassword(email: string): Promise<{ message: string }> {
  return apiPost<{ message: string }>(API_ENDPOINTS.auth.forgotPassword, {
    email,
  });
}

/** Activate account by verifying email token */
export async function verifyEmail(
  payload: VerifyEmailPayload
): Promise<VerifyEmailResponse> {
  return apiPost<VerifyEmailResponse, VerifyEmailPayload>(
    API_ENDPOINTS.auth.verifyEmail,
    payload,
    { skipSessionKey: true }
  );
}

/** Resend verification email for authenticated user */
export async function resendVerificationEmail(): Promise<MessageResponse> {
  return apiPost<MessageResponse>(API_ENDPOINTS.auth.resendVerification);
}
