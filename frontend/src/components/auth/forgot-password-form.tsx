"use client";

import * as React from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { ArrowLeft } from "lucide-react";
import { toast } from "sonner";

import { validateLoginForm } from "@/lib/auth-validation";
import { useForgotPassword } from "@/lib/api/hooks/use-auth";
import type { LoginFormErrors } from "@/types/auth";
import { AuthCard } from "@/components/auth/auth-card";
import { Button } from "@/components/ui/button";
import { FormField } from "@/components/ui/form-field";
import { Input } from "@/components/ui/input";

function ForgotPasswordForm() {
  const router = useRouter();
  const forgotPasswordMutation = useForgotPassword();
  const [email, setEmail] = React.useState("");
  const [errors, setErrors] = React.useState<LoginFormErrors>({});

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    const validationErrors = validateLoginForm({
      email,
      password: "placeholder1",
      rememberMe: false,
    });
    const emailError = validationErrors.email
      ? { email: validationErrors.email }
      : {};
    setErrors(emailError);

    if (Object.keys(emailError).length > 0) return;

    try {
      await forgotPasswordMutation.mutateAsync(email);
      toast.success("Reset link sent", {
        description: `If an account exists for ${email}, you'll receive instructions shortly.`,
      });
      router.push("/login");
    } catch {
      toast.error("Could not send reset link");
    }
  };

  return (
    <AuthCard>
      <form onSubmit={handleSubmit} className="space-y-5">
        <p className="text-sm text-muted-foreground">
          Enter your email and we&apos;ll send you a link to reset your password.
        </p>
        <FormField id="email" label="Email" required error={errors.email}>
          <Input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="you@company.com.au"
            autoComplete="email"
          />
        </FormField>
        <Button type="submit" size="lg" className="w-full" loading={forgotPasswordMutation.isPending}>
          Send reset link
        </Button>
      </form>
      <Button asChild variant="ghost" className="mt-4 w-full gap-2">
        <Link href="/login">
          <ArrowLeft className="size-4" />
          Back to sign in
        </Link>
      </Button>
    </AuthCard>
  );
}

export { ForgotPasswordForm };
