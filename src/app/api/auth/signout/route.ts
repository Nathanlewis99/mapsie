import { NextResponse } from "next/server";
import { endSession } from "@/lib/server/auth";
import { publicUrl } from "@/lib/server/urls";

export async function POST() {
  await endSession();
  return NextResponse.redirect(`${publicUrl()}/`, { status: 303 });
}
