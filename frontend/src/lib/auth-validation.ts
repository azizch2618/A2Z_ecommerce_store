import { getPhoneError, isValidEmail } from "@/lib/australian-address";
import type { LoginFormErrors, LoginFormState, RegisterFormErrors, RegisterFormState } from "@/types/auth";

export function validateLoginForm(form: LoginFormState): LoginFormErrors {
  const errors: LoginFormErrors = {};

  if (!form.email.trim()) {
    errors.email = "Email is required";
  } else if (!isValidEmail(form.email)) {
    errors.email = "Enter a valid email address";
  }

  if (!form.password) {
    errors.password = "Password is required";
  } else if (form.password.length < 8) {
    errors.password = "Password must be at least 8 characters";
  }

  return errors;
}

function isValidAbn(value: string): boolean {
  const digits = value.replace(/\D/g, "");
  return digits.length === 11;
}

export function validateRegisterForm(form: RegisterFormState): RegisterFormErrors {
  const errors: RegisterFormErrors = {};

  if (!form.firstName.trim()) errors.firstName = "First name is required";
  if (!form.lastName.trim()) errors.lastName = "Last name is required";

  if (form.accountType === "trade") {
    if (!form.company.trim()) errors.company = "Company name is required for trade accounts";
    if (!form.abn.trim()) {
      errors.abn = "ABN is required for trade accounts";
    } else if (!isValidAbn(form.abn)) {
      errors.abn = "Enter a valid 11-digit ABN";
    }
  }

  if (!form.email.trim()) {
    errors.email = "Email is required";
  } else if (!isValidEmail(form.email)) {
    errors.email = "Enter a valid email address";
  }

  const phoneError = getPhoneError(form.phone);
  if (phoneError) errors.phone = phoneError;

  if (!form.password) {
    errors.password = "Password is required";
  } else if (form.password.length < 8) {
    errors.password = "Password must be at least 8 characters";
  }

  if (!form.confirmPassword) {
    errors.confirmPassword = "Please confirm your password";
  } else if (form.password !== form.confirmPassword) {
    errors.confirmPassword = "Passwords do not match";
  }

  return errors;
}
