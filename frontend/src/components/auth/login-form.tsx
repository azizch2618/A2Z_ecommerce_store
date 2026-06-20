"use client";

import * as React from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { toast } from "sonner";

import { defaultLoginForm } from "@/config/auth";
import { validateLoginForm } from "@/lib/auth-validation";
import { useLogin } from "@/lib/api/hooks/use-auth";
import type { LoginFormErrors, LoginFormState } from "@/types/auth";
import { AuthCard } from "@/components/auth/auth-card";
import { SocialLoginButton } from "@/components/auth/social-login-button";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { FormField } from "@/components/ui/form-field";
import { Input } from "@/components/ui/input";
import { Separator } from "@/components/ui/separator";

function LoginForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const loginMutation = useLogin();
  const [form, setForm] = React.useState<LoginFormState>(defaultLoginForm);
  const [errors, setErrors] = React.useState<LoginFormErrors>({});

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    const validationErrors = validateLoginForm(form);
    setErrors(validationErrors);

    if (Object.keys(validationErrors).length > 0) return;

    try {
      await loginMutation.mutateAsync({
        email: form.email,
        password: form.password,
      });
      toast.success("Signed in successfully");
      const redirect = searchParams.get("redirect") ?? "/account";
      router.push(redirect);
    } catch {
      toast.error("Sign in failed", {
        description: "Check your email and password. Demo: customer@demo.a2ztools.com",
      });
    }
  };

  const handleGoogleLogin = () => {
    toast.info("Google sign-in (demo)", {
      description: "OAuth integration will be added with the backend.",
    });
  };

  return (
    <AuthCard>
      <form onSubmit={handleSubmit} className="space-y-5">
        <FormField id="email" label="Email" required error={errors.email}>
          <Input
            type="email"
            value={form.email}
            onChange={(e) => setForm((c) => ({ ...c, email: e.target.value }))}
            placeholder="you@company.com.au"
            autoComplete="email"
          />
        </FormField>

        <FormField id="password" label="Password" required error={errors.password}>
          <Input
            type="password"
            value={form.password}
            onChange={(e) => setForm((c) => ({ ...c, password: e.target.value }))}
            placeholder="••••••••"
            autoComplete="current-password"
          />
        </FormField>

        <div className="flex flex-wrap items-center justify-between gap-3">
          <label className="flex cursor-pointer items-center gap-2.5">
            <Checkbox
              checked={form.rememberMe}
              onCheckedChange={(checked) =>
                setForm((c) => ({ ...c, rememberMe: checked === true }))
              }
            />
            <span className="text-sm text-foreground">Remember me</span>
          </label>
          <Link
            href="/forgot-password"
            className="text-sm font-medium text-brand-blue hover:underline"
          >
            Forgot password?
          </Link>
        </div>

        <Button type="submit" size="lg" className="w-full" loading={loginMutation.isPending}>
          Sign in
        </Button>
      </form>

      <div className="relative my-6">
        <Separator />
        <span className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 bg-card px-3 text-xs text-muted-foreground">
          or
        </span>
      </div>

      <SocialLoginButton provider="google" onClick={handleGoogleLogin} />

      <p className="mt-6 text-center text-sm text-muted-foreground">
        Don&apos;t have an account?{" "}
        <Link href="/register" className="font-medium text-brand-blue hover:underline">
          Create account
        </Link>
      </p>
    </AuthCard>
  );
}

export { LoginForm };
