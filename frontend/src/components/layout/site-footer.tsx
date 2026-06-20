"use client";

import * as React from "react";
import Link from "next/link";

import {
  footerLinkGroups,
  paymentMethods,
  socialLinks,
  type FooterLinkGroup,
} from "@/config/navigation";
import { brand } from "@/config/brand";
import { SiteLogo } from "@/components/layout/header/site-logo";
import { Container } from "@/components/layout/container";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Separator } from "@/components/ui/separator";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";

export interface SiteFooterProps extends React.HTMLAttributes<HTMLElement> {
  linkGroups?: FooterLinkGroup[];
}

function FooterColumns({ groups }: { groups: FooterLinkGroup[] }) {
  return (
    <div className="grid gap-8 sm:grid-cols-2 lg:grid-cols-4">
      {groups.map((group) => (
        <div key={group.title}>
          <h2 className="mb-4 text-sm font-semibold uppercase tracking-wider text-white">
            {group.title}
          </h2>
          <ul className="space-y-3">
            {group.links.map((link) => (
              <li key={link.href}>
                <Link
                  href={link.href}
                  className="text-sm text-neutral-300 transition-colors hover:text-white hover:underline"
                >
                  {link.label}
                </Link>
              </li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  );
}

function NewsletterSignup() {
  const [submitted, setSubmitted] = React.useState(false);

  return (
    <div className="rounded-lg border border-white/10 bg-white/5 p-5 lg:max-w-md">
      <h2 className="text-sm font-semibold uppercase tracking-wider text-white">
        Stay in the loop
      </h2>
      <p className="mt-2 text-sm text-neutral-300">
        Get trade tips, new products, and exclusive offers.
      </p>
      {submitted ? (
        <p className="mt-4 text-sm font-medium text-success">
          Thanks — you&apos;re subscribed.
        </p>
      ) : (
        <form
          className="mt-4 flex flex-col gap-2 sm:flex-row"
          onSubmit={(event) => {
            event.preventDefault();
            setSubmitted(true);
          }}
        >
          <Input
            type="email"
            required
            placeholder="you@company.com.au"
            aria-label="Email address"
            className="border-white/20 bg-white/10 text-white placeholder:text-neutral-400"
          />
          <Button type="submit" variant="default" className="shrink-0">
            Subscribe
          </Button>
        </form>
      )}
      <p className="mt-2 text-xs text-neutral-400">
        We respect your privacy. Unsubscribe anytime.
      </p>
    </div>
  );
}

function SiteFooter({
  linkGroups = footerLinkGroups,
  className,
  ...props
}: SiteFooterProps) {
  return (
    <footer
      className={cn("bg-surface-dark text-neutral-300", className)}
      {...props}
    >
      <Container className="py-12 md:py-16">
        <div className="mb-10 flex flex-col gap-8 lg:flex-row lg:items-start lg:justify-between">
          <SiteLogo variant="reversed" />
          <NewsletterSignup />
        </div>

        <div className="hidden lg:block">
          <FooterColumns groups={linkGroups} />
        </div>

        <div className="lg:hidden">
          <Accordion type="multiple" className="w-full">
            {linkGroups.map((group) => (
              <AccordionItem
                key={group.title}
                value={group.title}
                className="border-white/10"
              >
                <AccordionTrigger className="text-white hover:no-underline">
                  {group.title}
                </AccordionTrigger>
                <AccordionContent>
                  <ul className="space-y-3">
                    {group.links.map((link) => (
                      <li key={link.href}>
                        <Link
                          href={link.href}
                          className="text-sm text-neutral-300 hover:text-white hover:underline"
                        >
                          {link.label}
                        </Link>
                      </li>
                    ))}
                  </ul>
                </AccordionContent>
              </AccordionItem>
            ))}
          </Accordion>
        </div>

        <Separator className="my-8 bg-white/10" />

        <div className="flex flex-wrap items-center gap-x-4 gap-y-2 text-xs text-neutral-400">
          <span>ABN: 12 345 678 901</span>
          <span aria-hidden>·</span>
          <span>GST Registered</span>
          <span aria-hidden>·</span>
          <span>Australian Owned & Operated</span>
        </div>

        <div className="mt-6 flex flex-wrap gap-2">
          {paymentMethods.map((method) => (
            <span
              key={method}
              className="rounded border border-white/15 px-2.5 py-1 text-xs text-neutral-300"
            >
              {method}
            </span>
          ))}
        </div>

        <Separator className="my-8 bg-white/10" />

        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <p className="text-sm text-neutral-400">
            © {new Date().getFullYear()} {brand.legalName}. All rights reserved.
          </p>
          <div className="flex flex-wrap gap-4">
            {socialLinks.map((social) => (
              <Link
                key={social.label}
                href={social.href}
                className="text-sm text-neutral-400 transition-colors hover:text-white hover:underline"
                target="_blank"
                rel="noopener noreferrer"
              >
                {social.label}
              </Link>
            ))}
          </div>
        </div>
      </Container>
    </footer>
  );
}

export { SiteFooter };
