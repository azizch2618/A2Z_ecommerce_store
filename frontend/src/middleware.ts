import {
  ACCESS_COOKIE_NAME,
  SESSION_COOKIE_NAME,
} from "@/lib/api/auth/token-storage";
import { isAdminDemoEnabled } from "@/lib/security/admin-demo";
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

const PROTECTED_PREFIXES = ["/account", "/admin-dashboard", "/checkout"];

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const isProtected = PROTECTED_PREFIXES.some(
    (prefix) => pathname === prefix || pathname.startsWith(`${prefix}/`)
  );

  if (!isProtected) {
    return NextResponse.next();
  }

  const hasSession =
    request.cookies.has(ACCESS_COOKIE_NAME) ||
    request.cookies.has(SESSION_COOKIE_NAME);

  if (pathname.startsWith("/admin-dashboard") && isAdminDemoEnabled()) {
    return NextResponse.next();
  }

  if (!hasSession) {
    const loginUrl = new URL("/login", request.url);
    loginUrl.searchParams.set("redirect", pathname);
    return NextResponse.redirect(loginUrl);
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/account/:path*", "/admin-dashboard/:path*", "/checkout/:path*"],
};
