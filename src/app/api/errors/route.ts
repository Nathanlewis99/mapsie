import { NextResponse } from "next/server";
import { logError } from "@/lib/server/log";

// Errors reported by customers' browsers. Rate-limited per address so a broken
// page in a loop can't flood the table.
const hits = new Map<string, { n: number; t: number }>();

export async function POST(req: Request) {
  const ip = req.headers.get("x-forwarded-for")?.split(",")[0].trim() ?? "?";
  const now = Date.now();
  const h = hits.get(ip);
  if (h && now - h.t < 60_000 && h.n >= 20) return new NextResponse(null, { status: 429 });
  hits.set(ip, h && now - h.t < 60_000 ? { n: h.n + 1, t: h.t } : { n: 1, t: now });
  if (hits.size > 5000) hits.clear();

  const b = (await req.json().catch(() => ({}))) as { message?: string; stack?: string; url?: string; kind?: string };
  if (!b.message) return new NextResponse(null, { status: 400 });
  const e = new Error(String(b.message).slice(0, 500));
  e.stack = String(b.stack ?? "").slice(0, 4000) || undefined;
  await logError(`browser.${b.kind ?? "error"}`, e, { url: String(b.url ?? "").slice(0, 300), ua: req.headers.get("user-agent")?.slice(0, 200) }, "client");
  return new NextResponse(null, { status: 204 });
}
