"use client";

import * as React from "react";
import { Mail, Sparkles } from "lucide-react";

import { newsletterContent } from "@/config/homepage";
import { Section } from "@/components/layout/section";
import { Heading, Text } from "@/components/ui/typography";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

function NewsletterSection() {
  const [submitted, setSubmitted] = React.useState(false);

  return (
    <Section variant="default" className="pb-16 md:pb-20">
      <div className="relative overflow-hidden rounded-2xl border border-border bg-gradient-to-br from-brand-navy via-brand-navy-light to-brand-blue px-6 py-10 shadow-lg md:px-12 md:py-14">
        <div
          className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_top_right,rgba(255,255,255,0.12),transparent_50%)]"
          aria-hidden
        />
        <div
          className="pointer-events-none absolute -right-8 -top-8 size-40 rounded-full bg-brand-amber/10 blur-3xl"
          aria-hidden
        />

        <div className="relative mx-auto max-w-2xl text-center">
          <div className="mx-auto mb-5 flex size-12 items-center justify-center rounded-xl bg-white/10 text-brand-amber backdrop-blur-sm">
            <Mail className="size-5" aria-hidden />
          </div>
          <p className="text-xs font-semibold uppercase tracking-[0.16em] text-brand-amber">
            Stay ahead
          </p>
          <Heading level="h2" as="h2" className="mt-2 text-white">
            {newsletterContent.title}
          </Heading>
          <Text variant="lead" className="mt-3 text-neutral-300">
            {newsletterContent.description}
          </Text>

          {submitted ? (
            <div className="mt-8 inline-flex items-center gap-2 rounded-lg border border-success/30 bg-success/20 px-4 py-3 text-sm font-medium text-white">
              <Sparkles className="size-4" aria-hidden />
              Thanks — you&apos;re on the list.
            </div>
          ) : (
            <form
              className="mx-auto mt-8 flex max-w-lg flex-col gap-3 sm:flex-row"
              onSubmit={(event) => {
                event.preventDefault();
                setSubmitted(true);
              }}
            >
              <Input
                type="email"
                required
                placeholder={newsletterContent.placeholder}
                aria-label="Email address"
                className="h-12 flex-1 border-white/20 bg-white/10 text-base text-white placeholder:text-neutral-400 focus-visible:border-white/40 focus-visible:bg-white/15"
              />
              <Button
                type="submit"
                size="lg"
                variant="trade"
                className="h-12 w-full shrink-0 sm:w-auto"
              >
                {newsletterContent.buttonLabel}
              </Button>
            </form>
          )}

          <p className="mt-4 text-xs text-neutral-400">
            {newsletterContent.note}
          </p>
        </div>
      </div>
    </Section>
  );
}

export { NewsletterSection };
