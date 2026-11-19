import { NextResponse } from "next/server";
import { cookies } from "next/headers";
import { gadsFinishConnect } from "@/lib/server/googleAds";
import { logError } from "@/lib/server/log";
import { publicUrl } from "@/lib/server/urls";

// Admin only (middleware): Google sends the owner back here after they allow access.
export async function GET(req: Request) {
  const url = new URL(req.url);
  const back = (s: string) => NextResponse.redirect(`${publicUrl()}/admin/channels?google=${s}`, { status: 303 });
  const jar = await cookies();
  const state = jar.get("gads_state")?.value;
  jar.delete("gads_state");
  if (url.searchParams.get("error")) return back("cancelled");
  const code = url.searchParams.get("code");
  if (!code || !state || url.searchParams.get("state") !== state) return back("failed");
  try {
    await gadsFinishConnect(code);
    return back("connected");
  } catch (e) {
    await logError("google-ads.connect", e);
    return back("failed");
  }
}
