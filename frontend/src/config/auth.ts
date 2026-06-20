import type { LoginFormState, RegisterFormState } from "@/types/auth";

export const loginBreadcrumbs = [
  { label: "Home", href: "/" },
  { label: "Sign in" },
];

export const registerBreadcrumbs = [
  { label: "Home", href: "/" },
  { label: "Create account" },
];

export const forgotPasswordBreadcrumbs = [
  { label: "Home", href: "/" },
  { label: "Sign in", href: "/login" },
  { label: "Forgot password" },
];

export const defaultLoginForm: LoginFormState = {
  email: "",
  password: "",
  rememberMe: false,
};

export const defaultRegisterForm: RegisterFormState = {
  firstName: "",
  lastName: "",
  company: "",
  abn: "",
  email: "",
  phone: "",
  password: "",
  confirmPassword: "",
  accountType: "standard",
};

export const authTrustPoints = [
  "Australian owned & GST registered",
  "Secure checkout & encrypted sign-in",
  "Trade accounts with Net 30 terms",
] as const;
