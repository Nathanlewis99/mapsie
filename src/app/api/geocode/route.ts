import { NextResponse } from "next/server";
import { clientIp, limit, tooMany } from "@/lib/server/rateLimit";
import { searchPlaces } from "@/lib/server/geocode";

export async function GET(req: Request) {
  // Searches as you type: generous, but stops scripts using us as a free geocoder.
  if (!limit("geocode", clientIp(req), 120, 60_000)) return tooMany("Too many searches. Please wait a moment.", 30);
  const u = new URL(req.url);
  const results = await searchPlaces(u.searchParams.get("q") ?? "", u.searchParams.get("full") === "1");
  return NextResponse.json(results, { headers: { "cache-control": "public, max-age=86400" } });
}
