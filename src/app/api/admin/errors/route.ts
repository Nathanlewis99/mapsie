import { NextResponse } from "next/server";
import { resolveError } from "@/lib/server/db";

/** Admin: mark an error group as dealt with (it reopens if it happens again). */
export async function POST(req: Request) {
  const { fingerprint } = (await req.json()) as { fingerprint?: string };
  if (!fingerprint) return NextResponse.json({ error: "fingerprint required" }, { status: 400 });
  await resolveError(fingerprint);
  return NextResponse.json({ ok: true });
}
