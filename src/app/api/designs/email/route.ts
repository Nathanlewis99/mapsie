import { NextResponse } from "next/server";
import { addDesignEmail, countDesignEmails, getDesign } from "@/lib/server/db";
import { sendDesignLinkEmail } from "@/lib/server/email";
import { validEmail } from "@/lib/server/password";
import { clientIp, limit, sameOrigin, tooMany } from "@/lib/server/rateLimit";
import { publicUrl } from "@/lib/server/urls";
import { logError } from "@/lib/server/log";

/**
 * "Email me my design": sends a link to a saved snapshot of their design, and (only if
 * they ticked the box) one reminder a day later if they haven't ordered.
 * POST { designId, email, remind }
 */
export async function POST(req: Request) {
  if (!sameOrigin(req, publicUrl())) return NextResponse.json({ error: "Not allowed" }, { status: 403 });
  if (!limit("design-email", clientIp(req), 5, 60 * 60_000)) return tooMany("You've sent a few already. Please try again later.", 600);
  const b = (await req.json().catch(() => ({}))) as { designId?: unknown; email?: unknown; remind?: unknown };
  const email = typeof b.email === "string" ? b.email.trim() : "";
  if (!validEmail(email)) return NextResponse.json({ error: "Please enter a valid email address." }, { status: 400 });
  const design = typeof b.designId === "string" ? await getDesign(b.designId) : null;
  if (!design) return NextResponse.json({ error: "We couldn't save your design. Please try again." }, { status: 400 });
  // Stop anyone using this to flood someone else's inbox.
  if ((await countDesignEmails(email, new Date(Date.now() - 24 * 3600_000).toISOString())) >= 3)
    return tooMany("We've already sent a few designs to that address today.", 3600);
  const row = await addDesignEmail(email, design.id, b.remind === true);
  try {
    await sendDesignLinkEmail(row, design.title ?? "");
  } catch (e) {
    await logError("email.design", e);
    return NextResponse.json({ error: "We couldn't send the email just now. Please try again." }, { status: 502 });
  }
  return NextResponse.json({ ok: true });
}
