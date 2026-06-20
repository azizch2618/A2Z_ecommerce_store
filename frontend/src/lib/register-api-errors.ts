import type { RegisterFormErrors } from "@/types/auth";
import { getFieldErrors, isApiError } from "@/lib/api/errors";

const FIELD_MAP: Record<string, keyof RegisterFormErrors> = {
  first_name: "firstName",
  last_name: "lastName",
  company_name: "company",
  abn: "abn",
  email: "email",
  phone: "phone",
  password: "password",
  password_confirm: "confirmPassword",
};

export function mapRegisterApiErrors(error: unknown): {
  formError?: string;
  fieldErrors: RegisterFormErrors;
} {
  if (!isApiError(error)) {
    return {
      formError: "Registration failed. Please try again.",
      fieldErrors: {},
    };
  }

  const fieldErrors: RegisterFormErrors = {};
  const apiFieldErrors = getFieldErrors(error);

  if (apiFieldErrors) {
    for (const [apiField, message] of Object.entries(apiFieldErrors)) {
      const formField = FIELD_MAP[apiField];
      if (formField) {
        fieldErrors[formField] = message;
      }
    }
  }

  return {
    formError: error.message,
    fieldErrors,
  };
}
