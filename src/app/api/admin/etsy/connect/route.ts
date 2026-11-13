import { NextResponse } from "next/server";
import { cookies } from "next/headers";
import { etsyConfigured, startConnect } from "@/lib/server/etsy";

// Admin only (see middleware): send the shop owner to Etsy to allow Mapsie to read orders.
export async function GET() {
  if (!etsyConfigured()) return NextResponse.json({ error: "Set ETSY_API_KEY and ETSY_SHARED_SECRET first" }, { status: 400 });
  const { url, state, verifier } = startConnect();
  const jar = await cookies();
  const opts = { httpOnly: true, secure: process.env.NODE_ENV === "production", sameSite: "lax" as const, path: "/api/etsy", maxAge: 600 };
  jar.set("etsy_state", state, opts);
  jar.set("etsy_verifier", verifier, opts);
  return NextResponse.redirect(url);
}
