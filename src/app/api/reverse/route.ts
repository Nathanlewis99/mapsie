import { NextResponse } from "next/server";
import { clientIp, limit, tooMany } from "@/lib/server/rateLimit";
import { reversePlace } from "@/lib/server/geocode";

export async function GET(req: Request) {
  if (!limit("reverse", clientIp(req), 60, 60_000)) return tooMany("Too many requests. Please wait a moment.", 30);
  const u = new URL(req.url);
  const lng = Number(u.searchParams.get("lng"));
  const lat = Number(u.searchParams.get("lat"));
  if (!Number.isFinite(lng) || !Number.isFinite(lat)) return NextResponse.json({ error: "bad coordinates" }, { status: 400 });
  return NextResponse.json({ name: await reversePlace(lng, lat) }, { headers: { "cache-control": "public, max-age=86400" } });
}
