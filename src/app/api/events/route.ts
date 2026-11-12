import { NextResponse } from "next/server";
import { recordEvent } from "@/lib/server/db";
import { EXTRA_EVENTS, FUNNEL } from "@/lib/funnel";

const ALLOWED = new Set<string>([...FUNNEL.map((f) => f.id), ...EXTRA_EVENTS]);

/** Anonymous analytics events from the browser (see src/lib/track.ts). */
export async function POST(req: Request) {
  const b = (await req.json().catch(() => ({}))) as { v?: string; name?: string; props?: Record<string, unknown> };
  // "paid" only ever comes from our own server, after Stripe confirms payment.
  if (!b.v || !/^[a-z0-9]{8,40}$/.test(b.v) || !b.name || !ALLOWED.has(b.name) || b.name === "paid") return new NextResponse(null, { status: 400 });
  const props = b.props && typeof b.props === "object" ? Object.fromEntries(Object.entries(b.props).slice(0, 8).map(([k, v]) => [k.slice(0, 30), String(v).slice(0, 80)])) : undefined;
  await recordEvent(b.v, b.name, props).catch(() => {});
  return new NextResponse(null, { status: 204 });
}
