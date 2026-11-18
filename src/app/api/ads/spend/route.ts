import { NextResponse } from "next/server";
import { adsImportKeyValid, importScriptRows } from "@/lib/server/adSpend";

/**
 * Daily numbers from the Google Ads Script (shown on /admin/channels).
 * POST { channel: "google_ads", rows: [{ day, cost, currency, impressions, clicks, conversions, value }] }
 * with header x-mapsie-key.
 */
export async function POST(req: Request) {
  if (!adsImportKeyValid(req.headers.get("x-mapsie-key"))) return NextResponse.json({ error: "Not authorised" }, { status: 401 });
  const b = (await req.json().catch(() => ({}))) as { channel?: string; rows?: unknown };
  if (b.channel !== "google_ads" || !Array.isArray(b.rows)) return NextResponse.json({ error: "Expected { channel: 'google_ads', rows: [...] }" }, { status: 400 });
  const rows = b.rows.map((r: Record<string, unknown>) => ({
    day: String(r.day ?? ""),
    cost: Number(r.cost),
    currency: typeof r.currency === "string" ? r.currency : undefined,
    impressions: Number(r.impressions ?? 0),
    clicks: Number(r.clicks ?? 0),
    conversions: Number(r.conversions ?? 0),
    value: Number(r.value ?? 0),
  }));
  return NextResponse.json({ ok: true, saved: await importScriptRows("google_ads", rows) });
}
