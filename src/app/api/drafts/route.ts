import { NextResponse } from "next/server";
import { cookies } from "next/headers";
import { nanoid } from "nanoid";
import { getDesign, saveDraft } from "@/lib/server/db";
import { clientIp, limit, tooMany } from "@/lib/server/rateLimit";
import type { Design } from "@/lib/types";

/**
 * The map someone is working on, kept on our side under a first-party cookie (no sign-up), so it
 * survives the browser clearing its storage (Safari does after a week) and they can pick up later.
 * The cookie holds only a random id; the design is stored like any other.
 */
const COOKIE = "mapsie_draft";
const MAX = 4_000_000;
const valid = (id: string | undefined) => !!id && /^[A-Za-z0-9_-]{16}$/.test(id);

export async function GET() {
  const id = (await cookies()).get(COOKIE)?.value;
  if (!valid(id)) return NextResponse.json({ design: null });
  const d = await getDesign(`draft_${id}`);
  return NextResponse.json({ design: d?.stops?.length ? d : null }, { headers: { "cache-control": "no-store" } });
}

export async function POST(req: Request) {
  if (!limit("draft-save", clientIp(req), 240, 60 * 60_000)) return tooMany("Saving too often", 300);
  const text = await req.text();
  if (text.length > MAX) return NextResponse.json({ error: "Too large to keep a copy" }, { status: 413 });
  let design: Design;
  try {
    design = JSON.parse(text) as Design;
  } catch {
    return NextResponse.json({ error: "Invalid design" }, { status: 400 });
  }
  if (!Array.isArray(design.stops) || !design.view || !design.stops.length) return NextResponse.json({ error: "Invalid design" }, { status: 400 });
  const jar = await cookies();
  let id = jar.get(COOKIE)?.value;
  if (!valid(id)) id = nanoid(16);
  await saveDraft({ ...design, id: `draft_${id}` });
  const res = NextResponse.json({ ok: true });
  res.cookies.set(COOKIE, id!, { httpOnly: true, secure: true, sameSite: "lax", path: "/", maxAge: 90 * 24 * 3600 });
  return res;
}
