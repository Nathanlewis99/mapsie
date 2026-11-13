import { NextResponse } from "next/server";
import { cookies } from "next/headers";
import { getSession } from "@/lib/server/auth";
import { adminMfaValid } from "@/lib/session";
import { finishConnect } from "@/lib/server/etsy";
import { publicUrl } from "@/lib/server/urls";
import { logError } from "@/lib/server/log";

// Etsy sends the shop owner back here after they allow access.
export async function GET(req: Request) {
  const url = new URL(req.url);
  const jar = await cookies();
  const state = jar.get("etsy_state")?.value;
  const verifier = jar.get("etsy_verifier")?.value;
  jar.delete({ name: "etsy_state", path: "/api/etsy" });
  jar.delete({ name: "etsy_verifier", path: "/api/etsy" });
  const back = (q: string) => NextResponse.redirect(`${publicUrl()}/admin/etsy?${q}`);
  // Only an admin who started the connection here can finish it.
  if (!adminMfaValid(await getSession())) return NextResponse.redirect(`${publicUrl()}/admin/2fa?next=/admin/etsy`);
  if (url.searchParams.get("error")) return back("error=cancelled");
  const code = url.searchParams.get("code");
  if (!code || !state || !verifier || url.searchParams.get("state") !== state) return back("error=expired");
  try {
    const shop = await finishConnect(code, verifier);
    return back(`connected=${encodeURIComponent(shop)}`);
  } catch (e) {
    await logError("etsy.connect", e);
    return back("error=failed");
  }
}
