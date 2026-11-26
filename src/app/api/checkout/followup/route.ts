import { NextResponse } from "next/server";
import { getDesign, setCheckoutFollowup } from "@/lib/server/db";
import { validEmail } from "@/lib/server/password";
import { clientIp, limit, sameOrigin, tooMany } from "@/lib/server/rateLimit";
import { publicUrl } from "@/lib/server/urls";

/** The checkout tickbox "email me a link if I don't finish": POST { designId, email, on }. One email, an hour later. */
export async function POST(req: Request) {
  if (!sameOrigin(req, publicUrl())) return NextResponse.json({ error: "Not allowed" }, { status: 403 });
  if (!limit("checkout-followup", clientIp(req), 20, 60 * 60_000)) return tooMany("Please try again later.", 600);
  const b = (await req.json().catch(() => ({}))) as { designId?: unknown; email?: unknown; on?: unknown };
  const email = typeof b.email === "string" ? b.email.trim() : "";
  if (!validEmail(email)) return NextResponse.json({ error: "Please enter a valid email address." }, { status: 400 });
  if (typeof b.designId !== "string" || !(await getDesign(b.designId))) return NextResponse.json({ error: "Unknown map" }, { status: 400 });
  await setCheckoutFollowup(email, b.designId, b.on === true);
  return NextResponse.json({ ok: true });
}
