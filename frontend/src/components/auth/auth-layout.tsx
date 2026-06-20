import type { ReactNode } from "react";
import Image from "next/image";
import Link from "next/link";
import { CheckCircle2 } from "lucide-react";

import { brand } from "@/config/brand";
import { authTrustPoints } from "@/config/auth";
import { cn } from "@/lib/utils";

export interface AuthLayoutProps {
  children: ReactNode;
  title: string;
  subtitle: string;
  className?: string;
}

function AuthLayout({ children, title, subtitle, className }: AuthLayoutProps) {
  return (
    <div className={cn("min-h-[calc(100vh-var(--header-height-mobile))] lg:min-h-[calc(100vh-var(--header-height-desktop))]", className)}>
      <div className="grid min-h-inherit lg:grid-cols-2">
        <div className="relative hidden overflow-hidden bg-brand-navy lg:flex lg:flex-col lg:justify-between lg:p-10 xl:p-14">
          <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,hsl(var(--brand-accent)/0.25),transparent_55%)]" />
          <div className="relative">
            <Link href="/" className="inline-block">
              <Image
                src={brand.logo.full.src}
                alt={brand.logo.full.alt}
                width={brand.logo.full.width}
                height={brand.logo.full.height}
                className="h-10 w-auto max-w-[140px] rounded-md object-contain brightness-0 invert"
              />
            </Link>
            <h2 className="mt-10 max-w-md text-3xl font-bold tracking-tight text-white">
              Professional hardware for Australian trade & IT teams
            </h2>
            <p className="mt-4 max-w-md text-sm leading-relaxed text-white/75">
              Sign in to manage orders, trade pricing, saved quotes, and project
              deliveries — all with GST-inclusive Australian checkout.
            </p>
          </div>
          <ul className="relative space-y-3">
            {authTrustPoints.map((point) => (
              <li key={point} className="flex items-center gap-2.5 text-sm text-white/90">
                <CheckCircle2 className="size-4 shrink-0 text-brand-blue" aria-hidden />
                {point}
              </li>
            ))}
          </ul>
        </div>

        <div className="flex flex-col justify-center bg-background px-4 py-10 sm:px-6 lg:px-10 xl:px-16">
          <div className="mx-auto w-full max-w-md">
            <div className="mb-8 lg:hidden">
              <Link href="/" className="inline-block">
                <Image
                  src={brand.logo.full.src}
                  alt={brand.logo.full.alt}
                  width={brand.logo.full.width}
                  height={brand.logo.full.height}
                  className="h-9 w-auto max-w-[120px] rounded-md object-contain"
                />
              </Link>
            </div>
            <div className="mb-8">
              <h1 className="text-2xl font-bold text-foreground md:text-3xl">{title}</h1>
              <p className="mt-2 text-sm text-muted-foreground">{subtitle}</p>
            </div>
            {children}
          </div>
        </div>
      </div>
    </div>
  );
}

export { AuthLayout };
