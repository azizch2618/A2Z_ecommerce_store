"use client";

import * as React from "react";
import Link from "next/link";
import { Building2, CheckCircle2, Mail, User } from "lucide-react";

import { defaultRegisterForm } from "@/config/auth";
import { validateRegisterForm } from "@/lib/auth-validation";
import { useRegister, useResendVerificationEmail } from "@/lib/api/hooks/use-auth";
import { mapRegisterApiErrors } from "@/lib/register-api-errors";
import { cn } from "@/lib/utils";
import type { AccountType, RegisterFormErrors, RegisterFormState } from "@/types/auth";
import { AuthCard } from "@/components/auth/auth-card";
import { Button } from "@/components/ui/button";
import { FormField } from "@/components/ui/form-field";
import { Input } from "@/components/ui/input";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";

type RegisterStep = "form" | "success";

interface RegisterSuccessState {
  email: string;
  message: string;
  accountType: AccountType;
}

function RegisterSuccessPanel({
  success,
  onResend,
  isResending,
}: {
  success: RegisterSuccessState;
  onResend: () => void;
  isResending: boolean;
}) {
  return (
    <AuthCard>
      <div className="space-y-5 text-center">
        <div className="mx-auto flex size-14 items-center justify-center rounded-full bg-brand-blue-light/40 dark:bg-brand-blue-light/10">
          <CheckCircle2 className="size-7 text-brand-blue" aria-hidden />
        </div>
        <div>
          <h2 className="text-xl font-semibold text-foreground">Account created</h2>
          <p className="mt-2 text-sm text-muted-foreground">{success.message}</p>
        </div>

        <div className="rounded-lg border border-border bg-muted/40 p-4 text-left">
          <div className="flex items-start gap-3">
            <Mail className="mt-0.5 size-4 shrink-0 text-brand-blue" aria-hidden />
            <div className="space-y-1 text-sm">
              <p className="font-medium text-foreground">Verify your email to activate</p>
              <p className="text-muted-foreground">
                We sent a verification link to{" "}
                <span className="font-medium text-foreground">{success.email}</span>.
                Open the link to activate your account.
              </p>
              {success.accountType === "trade" ? (
                <p className="text-muted-foreground">
                  Your trade account application is pending review after email verification.
                </p>
              ) : null}
            </div>
          </div>
        </div>

        <div className="flex flex-col gap-2">
          <Button type="button" variant="outline" loading={isResending} onClick={onResend}>
            Resend verification email
          </Button>
          <Button asChild>
            <Link href="/login">Continue to sign in</Link>
          </Button>
        </div>
      </div>
    </AuthCard>
  );
}

function RegisterForm() {
  const registerMutation = useRegister();
  const resendMutation = useResendVerificationEmail();
  const [step, setStep] = React.useState<RegisterStep>("form");
  const [success, setSuccess] = React.useState<RegisterSuccessState | null>(null);
  const [form, setForm] = React.useState<RegisterFormState>(defaultRegisterForm);
  const [errors, setErrors] = React.useState<RegisterFormErrors>({});
  const [formError, setFormError] = React.useState<string | null>(null);

  const updateField = <K extends keyof RegisterFormState>(
    field: K,
    value: RegisterFormState[K]
  ) => {
    setForm((current) => ({ ...current, [field]: value }));
    setErrors((current) => {
      if (!current[field as keyof RegisterFormErrors]) return current;
      const next = { ...current };
      delete next[field as keyof RegisterFormErrors];
      return next;
    });
    setFormError(null);
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setFormError(null);

    const validationErrors = validateRegisterForm(form);
    setErrors(validationErrors);
    if (Object.keys(validationErrors).length > 0) return;

    const isTrade = form.accountType === "trade";

    try {
      const response = await registerMutation.mutateAsync({
        email: form.email.trim(),
        password: form.password,
        password_confirm: form.confirmPassword,
        first_name: form.firstName.trim(),
        last_name: form.lastName.trim(),
        phone: form.phone.trim(),
        customer_type: isTrade ? "trade" : "retail",
        ...(isTrade
          ? {
              company_name: form.company.trim(),
              abn: form.abn.replace(/\D/g, ""),
            }
          : {}),
      });

      setSuccess({
        email: form.email.trim(),
        message: response.message,
        accountType: form.accountType,
      });
      setStep("success");
    } catch (error) {
      const mapped = mapRegisterApiErrors(error);
      setErrors((current) => ({ ...current, ...mapped.fieldErrors }));
      setFormError(mapped.formError ?? "Registration failed. Please try again.");
    }
  };

  const handleResend = async () => {
    if (!success) return;
    try {
      const result = await resendMutation.mutateAsync();
      setSuccess((current) =>
        current ? { ...current, message: result.message } : current
      );
    } catch {
      setFormError("Could not resend verification email. Try again from your account.");
    }
  };

  if (step === "success" && success) {
    return (
      <RegisterSuccessPanel
        success={success}
        onResend={handleResend}
        isResending={resendMutation.isPending}
      />
    );
  }

  const accountOptions: Array<{
    value: AccountType;
    label: string;
    description: string;
    icon: typeof User;
  }> = [
    {
      value: "standard",
      label: "Standard customer",
      description: "Personal or small business purchases with card checkout.",
      icon: User,
    },
    {
      value: "trade",
      label: "Trade customer",
      description: "B2B account with trade pricing, quotes, and Net 30 terms.",
      icon: Building2,
    },
  ];

  return (
    <AuthCard>
      <form onSubmit={handleSubmit} className="space-y-5" noValidate>
        {formError ? (
          <div
            role="alert"
            className="rounded-lg border border-destructive/30 bg-destructive/5 px-4 py-3 text-sm text-destructive"
          >
            {formError}
          </div>
        ) : null}

        <fieldset className="space-y-3" disabled={registerMutation.isPending}>
          <legend className="text-sm font-semibold text-foreground">Account type</legend>
          <RadioGroup
            value={form.accountType}
            onValueChange={(value) => updateField("accountType", value as AccountType)}
            className="grid gap-3 sm:grid-cols-2"
          >
            {accountOptions.map((option) => {
              const Icon = option.icon;
              const id = `account-type-${option.value}`;
              return (
                <label
                  key={option.value}
                  htmlFor={id}
                  className={cn(
                    "flex cursor-pointer flex-col gap-2 rounded-lg border p-4 transition-colors",
                    form.accountType === option.value
                      ? "border-brand-blue bg-brand-blue-light/30 dark:bg-brand-blue-light/10"
                      : "border-border hover:border-brand-blue/30"
                  )}
                >
                  <div className="flex items-center gap-2">
                    <RadioGroupItem value={option.value} id={id} />
                    <Icon className="size-4 text-brand-blue" aria-hidden />
                    <span className="text-sm font-medium text-foreground">
                      {option.label}
                    </span>
                  </div>
                  <p className="pl-7 text-xs text-muted-foreground">{option.description}</p>
                </label>
              );
            })}
          </RadioGroup>
        </fieldset>

        <div className="grid gap-4 sm:grid-cols-2">
          <FormField
            id="firstName"
            label="First name"
            required
            error={errors.firstName}
          >
            <Input
              value={form.firstName}
              onChange={(e) => updateField("firstName", e.target.value)}
              autoComplete="given-name"
              disabled={registerMutation.isPending}
            />
          </FormField>
          <FormField
            id="lastName"
            label="Last name"
            required
            error={errors.lastName}
          >
            <Input
              value={form.lastName}
              onChange={(e) => updateField("lastName", e.target.value)}
              autoComplete="family-name"
              disabled={registerMutation.isPending}
            />
          </FormField>
          <FormField
            id="company"
            label="Company name"
            required={form.accountType === "trade"}
            error={errors.company}
            className="sm:col-span-2"
          >
            <Input
              value={form.company}
              onChange={(e) => updateField("company", e.target.value)}
              placeholder="Business or organisation"
              autoComplete="organization"
              disabled={registerMutation.isPending}
            />
          </FormField>
          <FormField
            id="abn"
            label="ABN"
            required={form.accountType === "trade"}
            error={errors.abn}
            hint="11-digit Australian Business Number"
            className="sm:col-span-2"
          >
            <Input
              value={form.abn}
              onChange={(e) =>
                updateField("abn", e.target.value.replace(/\D/g, "").slice(0, 11))
              }
              placeholder="12 345 678 901"
              inputMode="numeric"
              disabled={registerMutation.isPending}
            />
          </FormField>
          <FormField id="email" label="Email" required error={errors.email}>
            <Input
              type="email"
              value={form.email}
              onChange={(e) => updateField("email", e.target.value)}
              placeholder="you@company.com.au"
              autoComplete="email"
              disabled={registerMutation.isPending}
            />
          </FormField>
          <FormField
            id="phone"
            label="Phone"
            required
            error={errors.phone}
            hint="Australian landline or mobile"
          >
            <Input
              type="tel"
              value={form.phone}
              onChange={(e) => updateField("phone", e.target.value)}
              placeholder="02 9123 4567"
              autoComplete="tel"
              disabled={registerMutation.isPending}
            />
          </FormField>
          <FormField
            id="password"
            label="Password"
            required
            error={errors.password}
            hint="Minimum 8 characters"
          >
            <Input
              type="password"
              value={form.password}
              onChange={(e) => updateField("password", e.target.value)}
              autoComplete="new-password"
              disabled={registerMutation.isPending}
            />
          </FormField>
          <FormField
            id="confirmPassword"
            label="Confirm password"
            required
            error={errors.confirmPassword}
          >
            <Input
              type="password"
              value={form.confirmPassword}
              onChange={(e) => updateField("confirmPassword", e.target.value)}
              autoComplete="new-password"
              disabled={registerMutation.isPending}
            />
          </FormField>
        </div>

        <Button
          type="submit"
          size="lg"
          className="w-full"
          loading={registerMutation.isPending}
          disabled={registerMutation.isPending}
        >
          Create account
        </Button>
      </form>

      <p className="mt-6 text-center text-sm text-muted-foreground">
        Already have an account?{" "}
        <Link href="/login" className="font-medium text-brand-blue hover:underline">
          Sign in
        </Link>
      </p>
    </AuthCard>
  );
}

export { RegisterForm };
