import { NextResponse } from "next/server";
import { clientIp, limit, sameOrigin, tooMany } from "@/lib/server/rateLimit";
import { cleanApplication, startApplication } from "@/lib/server/partnerApply";
import { logError } from "@/lib/server/log";
import { publicUrl } from "@/lib/server/urls";

// Partner sign-up, step 1: check the form and email a confirmation link.
export async function POST(req: Request) {
  if (!sameOrigin(req, publicUrl())) return NextResponse.json({ error: "Bad request" }, { status: 400 });
  if (!limit("partner-apply", clientIp(req), 4, 60 * 60_000)) return tooMany("Thanks: please check your inbox for the confirmation email, or try again in an hour.", 3600);
  const b = (await req.json().catch(() => ({}))) as Record<string, unknown>;
  if (typeof b.company_url === "string" && b.company_url) return NextResponse.json({ ok: true }); // honeypot
  const a = cleanApplication(b);
  if (typeof a === "string") return NextResponse.json({ error: a }, { status: 400 });
  if (!limit("partner-apply-email", a.email, 3, 24 * 60 * 60_000)) return tooMany("We've already sent a few confirmation emails to that address. Please check your inbox.", 3600);
  try {
    await startApplication(a);
  } catch (e) {
    await logError("partner.apply", e, {});
    return NextResponse.json({ error: "Sorry, we couldn't send the confirmation email. Please email hello@mapsie.shop." }, { status: 502 });
  }
  return NextResponse.json({ ok: true });
}
