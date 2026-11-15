import { NextResponse } from "next/server";
import { findOrderFor, orderSummary } from "@/lib/server/support";
import { recordFailure, tooManyAttempts } from "@/lib/server/password";

const ip = (req: Request) => req.headers.get("x-forwarded-for")?.split(",")[0]?.trim() || "unknown";

/** The support form checks the order number and email together; it only shows details when both match. */
export async function POST(req: Request) {
  const { orderRef, email } = (await req.json().catch(() => ({}))) as { orderRef?: string; email?: string };
  if (!orderRef || !email) return NextResponse.json({ found: false });
  if (tooManyAttempts(`support-lookup:${email}`, ip(req))) return NextResponse.json({ found: false, slow: true });
  const o = await findOrderFor(String(orderRef), String(email));
  if (!o) {
    recordFailure(`support-lookup:${email}`, ip(req));
    return NextResponse.json({ found: false });
  }
  return NextResponse.json({ found: true, order: await orderSummary(o) }, { headers: { "cache-control": "no-store" } });
}
