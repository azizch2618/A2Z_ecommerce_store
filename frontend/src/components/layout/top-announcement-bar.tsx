"use client";

import * as React from "react";
import Link from "next/link";
import { X } from "lucide-react";

import { announcementMessages } from "@/config/navigation";
import { cn } from "@/lib/utils";
import { Container } from "@/components/layout/container";
import { Button } from "@/components/ui/button";

export interface TopAnnouncementBarProps extends React.HTMLAttributes<HTMLDivElement> {
  message?: string;
  tradeCta?: { label: string; href: string };
  dismissible?: boolean;
}

function TopAnnouncementBar({
  className,
  message = announcementMessages.primary,
  tradeCta = announcementMessages.tradeCta,
  dismissible = true,
  ...props
}: TopAnnouncementBarProps) {
  const [dismissed, setDismissed] = React.useState(false);

  if (dismissed) return null;

  return (
    <div
      className={cn(
        "border-b border-brand-amber/20 bg-brand-amber-light text-sm text-brand-navy",
        className
      )}
      role="region"
      aria-label="Announcement"
      {...props}
    >
      <Container className="relative flex min-h-10 items-center justify-center gap-3 py-2 pr-10 text-center">
        <p className="text-pretty">
          <span>{message}</span>{" "}
          <Link
            href={tradeCta.href}
            className="font-semibold text-brand-blue underline-offset-4 hover:underline"
          >
            {tradeCta.label}
          </Link>
        </p>

        {dismissible ? (
          <Button
            type="button"
            variant="ghost"
            size="icon-sm"
            className="absolute right-0 text-brand-navy hover:bg-brand-amber/20"
            aria-label="Dismiss announcement"
            onClick={() => setDismissed(true)}
          >
            <X className="size-4" />
          </Button>
        ) : null}
      </Container>
    </div>
  );
}

export { TopAnnouncementBar };
