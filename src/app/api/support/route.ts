import { NextResponse } from "next/server";
import { createTicket, ticketUrl } from "@/lib/server/support";
import { recordFailure, tooManyAttempts, validEmail } from "@/lib/server/password";
import { REASONS, reasonFor, type SupportReason } from "@/lib/support";

const ip = (req: Request) => req.headers.get("x-forwarded-for")?.split(",")[0]?.trim() || "unknown";

/** A new support request from /support. */
export async function POST(req: Request) {
  const b = (await req.json().catch(() => ({}))) as Record<string, unknown>;
  const email = String(b.email ?? "").trim().slice(0, 254);
  const message = String(b.message ?? "").trim().slice(0, 5000);
  const reason = String(b.reason ?? "") as SupportReason;
  const photos = Array.isArray(b.photos) ? b.photos : [];
  if (!validEmail(email)) return NextResponse.json({ error: "Please enter the email address you used for your order." }, { status: 400 });
  if (!REASONS.some((r) => r.id === reason)) return NextResponse.json({ error: "Please choose what you need help with." }, { status: 400 });
  if (message.length < 5) return NextResponse.json({ error: "Please tell us a little about the problem." }, { status: 400 });
  if (reasonFor(reason).photos === "required" && !photos.length)
    return NextResponse.json({ error: "Please add at least one photo, so we can see the problem and put it right quickly." }, { status: 400 });
  // Limits spam: a few requests per email, and per connection.
  if (tooManyAttempts(`support:${email}`, ip(req))) return NextResponse.json({ error: "You've sent a few requests already. We'll be in touch soon, or email us directly." }, { status: 429 });
  recordFailure(`support:${email}`, ip(req));
  const t = await createTicket({
    email,
    name: typeof b.name === "string" ? b.name.slice(0, 80) : undefined,
    orderRef: String(b.orderRef ?? "").slice(0, 60),
    reason,
    message,
    photos,
  });
  return NextResponse.json({ id: t.id, url: ticketUrl(t.id).replace(/^https?:\/\/[^/]+/, "") });
}
