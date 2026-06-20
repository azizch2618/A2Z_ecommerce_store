import { AuthLayout, RegisterForm } from "@/components/auth";

export const metadata = {
  title: "Create account | A2Z Tools",
  description:
    "Register for an A2Z Tools account — standard or trade customer with Australian B2B pricing.",
};

export default function RegisterPage() {
  return (
    <AuthLayout
      title="Create your account"
      subtitle="Join A2Z Tools as a standard or trade customer. All prices include Australian GST."
    >
      <RegisterForm />
    </AuthLayout>
  );
}
