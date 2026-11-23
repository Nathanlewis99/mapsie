import { NextResponse } from "next/server";
import { finishApplication } from "@/lib/server/partnerApply";
import { logError } from "@/lib/server/log";
import { publicUrl } from "@/lib/server/urls";

// Partner sign-up, step 2: the confirmation link.
export async function GET(req: Request) {
  try {
    const r = await finishApplication(new URL(req.url).searchParams.get("t") ?? "");
    return NextResponse.redirect(`${publicUrl()}/partners/join?${r.ok ? "sent=1" : "expired=1"}`, { status: 303 });
  } catch (e) {
    await logError("partner.verify", e, {});
    return NextResponse.redirect(`${publicUrl()}/partners/join?error=1`, { status: 303 });
  }
}
