import { NextResponse } from "next/server";
import { finishPartnerSignIn } from "@/lib/server/partnerAuth";
import { publicUrl } from "@/lib/server/urls";

// The link from the sign-in email.
export async function GET(req: Request) {
  const t = new URL(req.url).searchParams.get("t") ?? "";
  const ok = await finishPartnerSignIn(t);
  return NextResponse.redirect(`${publicUrl()}${ok ? "/partner" : "/partner/signin?expired=1"}`, { status: 303 });
}
