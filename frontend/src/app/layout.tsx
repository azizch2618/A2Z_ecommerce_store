import type { Metadata } from "next";

import { AppProviders } from "@/components/providers/app-providers";
import { brand } from "@/config/brand";
import { fontMono, fontSans } from "@/lib/fonts";
import "./globals.css";

export const metadata: Metadata = {
  title: "A2Z Tools — Australian Hardware & Networking",
  description:
    "Enterprise-grade networking, tools, and security for Australian trade professionals and businesses.",
  icons: {
    icon: brand.logo.full.src,
    apple: brand.logo.full.src,
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en-AU"
      className={`${fontSans.variable} ${fontMono.variable}`}
      suppressHydrationWarning
    >
      <body
        className="min-h-screen font-sans antialiased"
        suppressHydrationWarning
      >
        <AppProviders>{children}</AppProviders>
      </body>
    </html>
  );
}
