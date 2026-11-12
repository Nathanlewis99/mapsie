import { NextResponse } from "next/server";
import { searchPlaces } from "@/lib/server/geocode";

export async function GET(req: Request) {
  const u = new URL(req.url);
  const results = await searchPlaces(u.searchParams.get("q") ?? "", u.searchParams.get("full") === "1");
  return NextResponse.json(results, { headers: { "cache-control": "public, max-age=86400" } });
}
