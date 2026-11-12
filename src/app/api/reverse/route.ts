import { NextResponse } from "next/server";
import { reversePlace } from "@/lib/server/geocode";

export async function GET(req: Request) {
  const u = new URL(req.url);
  const lng = Number(u.searchParams.get("lng"));
  const lat = Number(u.searchParams.get("lat"));
  if (!Number.isFinite(lng) || !Number.isFinite(lat)) return NextResponse.json({ error: "bad coordinates" }, { status: 400 });
  return NextResponse.json({ name: await reversePlace(lng, lat) }, { headers: { "cache-control": "public, max-age=86400" } });
}
