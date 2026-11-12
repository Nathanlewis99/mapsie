import { NextResponse } from "next/server";
import { currentUser, googleConfigured } from "@/lib/server/auth";

/** Who is signed in (for client components). */
export async function GET() {
  const u = await currentUser();
  return NextResponse.json(
    { user: u ? { id: u.id, email: u.email, name: u.name, picture: u.picture } : null, googleEnabled: googleConfigured() },
    { headers: { "cache-control": "no-store" } },
  );
}
