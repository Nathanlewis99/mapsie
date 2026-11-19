import { NextResponse } from "next/server";
import { randomBytes } from "node:crypto";
import { gadsAuthUrl, gadsMissing } from "@/lib/server/googleAds";
import { publicUrl } from "@/lib/server/urls";

// Admin only (middleware): send the owner to Google to allow Mapsie to manage the ads account.
export async function GET() {
  const missing = gadsMissing().filter((m) => m === "GOOGLE_ADS_CLIENT_ID" || m === "GOOGLE_ADS_CLIENT_SECRET");
  if (missing.length) return NextResponse.redirect(`${publicUrl()}/admin/channels?google=missing`, { status: 303 });
  const state = randomBytes(18).toString("base64url");
  const res = NextResponse.redirect(gadsAuthUrl(state), { status: 303 });
  res.cookies.set("gads_state", state, { httpOnly: true, secure: true, sameSite: "lax", path: "/api/admin/google-ads", maxAge: 600 });
  return res;
}
