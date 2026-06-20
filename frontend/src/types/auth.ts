export type AccountType = "standard" | "trade";

export type TradeAccountStatus = "approved" | "pending" | "not_applied";

export interface AuthUser {
  id: string;
  firstName: string;
  lastName: string;
  company: string;
  email: string;
  phone: string;
  abn?: string;
  accountType: AccountType;
  tradeStatus: TradeAccountStatus;
  creditLimit?: number;
  memberSince: string;
}

export interface LoginFormState {
  email: string;
  password: string;
  rememberMe: boolean;
}

export interface RegisterFormState {
  firstName: string;
  lastName: string;
  company: string;
  abn: string;
  email: string;
  phone: string;
  password: string;
  confirmPassword: string;
  accountType: AccountType;
}

export interface LoginFormErrors {
  email?: string;
  password?: string;
}

export interface RegisterFormErrors {
  firstName?: string;
  lastName?: string;
  company?: string;
  abn?: string;
  email?: string;
  phone?: string;
  password?: string;
  confirmPassword?: string;
}
