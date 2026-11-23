import { NextResponse } from "next/server";
import { clientIp, limit, sameOrigin } from "@/lib/server/rateLimit";
import { sendPartnerSignInLink } from "@/lib/server/partnerAuth";
import { logError } from "@/lib/server/log";
import { publicUrl } from "@/lib/server/urls";

// Partner dashboard: email me a sign-in link. Always says "sent", whether or not the address is a partner's.
export async function POST(req: Request) {
  const back = (q: string) => NextResponse.redirect(`${publicUrl()}/partner/signin?${q}`, { status: 303 });
  if (!sameOrigin(req, publicUrl())) return back("error=1");
  const email = String((await req.formData()).get("email") ?? "").trim().slice(0, 120);
  if (!/^\S+@\S+\.\S+$/.test(email)) return back("error=1");
  if (!limit("partner-signin", clientIp(req), 8, 60 * 60_000) || !limit("partner-signin-email", email.toLowerCase(), 4, 60 * 60_000)) return back("slow=1");
  try {
    await sendPartnerSignInLink(email);
  } catch (e) {
    await logError("partner.signin", e, {});
  }
  return back("sent=1");
}
