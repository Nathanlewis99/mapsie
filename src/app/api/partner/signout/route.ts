import { NextResponse } from "next/server";
import { partnerSignOut } from "@/lib/server/partnerAuth";
import { publicUrl } from "@/lib/server/urls";

export async function POST() {
  await partnerSignOut();
  return NextResponse.redirect(`${publicUrl()}/partner/signin`, { status: 303 });
}
