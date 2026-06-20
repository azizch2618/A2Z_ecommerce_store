import type { ApiAddress, ApiTimestamps } from "./common";

export type CustomerType = "retail" | "trade" | "contractor" | "business";

export type TradeAccountStatus =
  | "pending"
  | "approved"
  | "suspended"
  | "rejected"
  | null;

export interface AuthTokens {
  access: string;
  refresh: string;
}

export interface AuthUser {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  phone: string | null;
  avatar_url: string | null;
  email_verified: boolean;
  roles?: string[];
  permissions?: string[];
}

export interface AuthCustomer {
  id: string;
  customer_type: CustomerType;
  trade_account_status: TradeAccountStatus;
  credit_limit_cents: number;
  payment_terms_days: number | null;
}

export interface AuthOrganization {
  id: string;
  legal_name: string;
  trading_name: string | null;
  abn: string | null;
  abn_verified: boolean;
}

export interface AuthMeResponse extends ApiTimestamps {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  phone: string | null;
  avatar_url: string | null;
  email_verified: boolean;
  customer: AuthCustomer;
  organization: AuthOrganization | null;
  roles: string[];
  permissions?: string[];
}

export interface LoginPayload {
  email: string;
  password: string;
}

export interface RegisterPayload {
  email: string;
  password: string;
  password_confirm: string;
  first_name: string;
  last_name: string;
  phone?: string;
  customer_type?: CustomerType;
  company_name?: string;
  abn?: string;
  marketing_opt_in?: boolean;
}

export interface LoginResponse {
  user: AuthUser;
  customer: AuthCustomer;
  tokens?: AuthTokens;
}

export interface RegisterResponse extends LoginResponse {
  message: string;
}

export interface VerifyEmailPayload {
  uid: string;
  token: string;
}

export interface VerifyEmailResponse {
  message: string;
  user: AuthUser;
}

export interface MessageResponse {
  message: string;
}

export interface RefreshTokenPayload {
  refresh: string;
}

export interface RefreshTokenResponse {
  access: string;
  refresh: string;
}

export interface UpdateProfilePayload {
  first_name?: string;
  last_name?: string;
  phone?: string;
  preferences?: Record<string, unknown>;
}

export type AddressListResponse = { data: ApiAddress[] };
