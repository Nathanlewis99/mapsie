import { NextResponse } from "next/server";
import { clientIp, limit, sameOrigin } from "@/lib/server/rateLimit";
import { currentPartner } from "@/lib/server/partnerAuth";
import { checkoutGiftCodes, checkoutPrints } from "@/lib/server/partnerShop";
import { logError } from "@/lib/server/log";
import { publicUrl } from "@/lib/server/urls";

// Partner dashboard: pay for bulk prints of one of their maps, or for gift cards. Sends them to Stripe.
export async function POST(req: Request) {
  const f = await req.formData();
  const s = await currentPartner(String(f.get("p") ?? ""));
  if (!s) return NextResponse.redirect(`${publicUrl()}/partner/signin`, { status: 303 });
  const back = (msg: string, at: string) => NextResponse.redirect(`${publicUrl()}/partner?p=${s.partner.id}&msg=${encodeURIComponent(msg)}#${at}`, { status: 303 });
  const what = String(f.get("what") ?? "");
  if (!sameOrigin(req, publicUrl())) return back("Please try again", "maps");
  if (!limit("partner-buy", clientIp(req), 20, 60 * 60_000)) return back("Too many attempts: please wait a few minutes", what === "prints" ? "maps" : "codes");
  const email = s.partner.billing?.invoiceEmail ?? s.email;
  try {
    const url =
      what === "prints"
        ? await checkoutPrints(s.partner, email, String(f.get("design") ?? ""), String(f.get("product") ?? ""), String(f.get("frame") ?? ""), Number(f.get("copies")))
        : await checkoutGiftCodes(s.partner, email, Number(f.get("count")), Number(f.get("value")));
    return NextResponse.redirect(url, { status: 303 });
  } catch (e) {
    const msg = String((e as Error)?.message ?? e);
    if (!/^(Between|Each|That map)/.test(msg)) await logError("partner.buy", e, { partnerId: s.partner.id, what });
    return back(/^(Between|Each|That map)/.test(msg) ? msg : "Sorry, checkout couldn't start. Please try again.", what === "prints" ? "maps" : "codes");
  }
}
