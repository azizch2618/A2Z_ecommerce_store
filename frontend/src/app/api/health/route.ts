import { NextResponse } from "next/server";

/** Frontend readiness probe for Docker / load balancers. */
export async function GET() {
  return NextResponse.json({ status: "ok" });
}
