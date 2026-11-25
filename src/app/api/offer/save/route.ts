import { NextResponse } from "next/server";
import { addDesignEmail, countDesignEmails, getDesign } from "@/lib/server/db";
import { sendDesignLinkEmail } from "@/lib/server/email";
import { validEmail } from "@/lib/server/password";
import { clientIp, limit, sameOrigin, tooMany } from "@/lib/server/rateLimit";
import { issueSaveOffer } from "@/lib/server/offers";
import { publicUrl } from "@/lib/server/urls";
import { logError } from "@/lib/server/log";
import { saveOfferOn } from "@/lib/offers";

/**
 * "Save your map" (the pop-up in the designer): email them a link to their design and, while the trial
 * runs, a personal code that expires in an hour. POST { designId, email, remind }
 */
export async function POST(req: Request) {
  if (!sameOrigin(req, publicUrl())) return NextResponse.json({ error: "Not allowed" }, { status: 403 });
  if (!limit("save-offer", clientIp(req), 5, 60 * 60_000)) return tooMany("You've saved a few already. Please try again later.", 600);
  const b = (await req.json().catch(() => ({}))) as { designId?: unknown; email?: unknown; remind?: unknown };
  const email = typeof b.email === "string" ? b.email.trim() : "";
  if (!validEmail(email)) return NextResponse.json({ error: "Please enter a valid email address." }, { status: 400 });
  const design = typeof b.designId === "string" ? await getDesign(b.designId) : null;
  if (!design) return NextResponse.json({ error: "We couldn't save your map. Please try again." }, { status: 400 });
  if ((await countDesignEmails(email, new Date(Date.now() - 24 * 3600_000).toISOString())) >= 3)
    return tooMany("We've already sent a few maps to that address today.", 3600);
  let offer = null;
  if (saveOfferOn() && process.env.STRIPE_SECRET_KEY) {
    try {
      offer = await issueSaveOffer(email);
    } catch (e) {
      await logError("offer.issue", e); // still save the map
    }
  }
  const row = await addDesignEmail(email, design.id, b.remind === true);
  try {
    await sendDesignLinkEmail(row, design.title ?? "", offer ?? undefined);
  } catch (e) {
    await logError("email.design", e);
    return NextResponse.json({ error: "We couldn't send the email just now. Please try again." }, { status: 502 });
  }
  return NextResponse.json({ ok: true, offer });
}
