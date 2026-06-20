import { AuthLayout, ForgotPasswordForm } from "@/components/auth";

export const metadata = {
  title: "Forgot password | A2Z Tools",
  description: "Reset your A2Z Tools account password.",
};

export default function ForgotPasswordPage() {
  return (
    <AuthLayout
      title="Reset your password"
      subtitle="We'll email you a link to choose a new password."
    >
      <ForgotPasswordForm />
    </AuthLayout>
  );
}
