import { NextResponse } from "next/server";
import { clientIp, limit, tooMany } from "@/lib/server/rateLimit";
import { currentUser } from "@/lib/server/auth";
import { listSavedDesigns, upsertSavedDesign } from "@/lib/server/db";
import type { Design } from "@/lib/types";

const MAX_BYTES = 15_000_000;

export async function GET() {
  const user = await currentUser();
  if (!user) return NextResponse.json({ error: "Sign in first" }, { status: 401 });
  return NextResponse.json((await listSavedDesigns(user.id)).map(({ design: _d, ...meta }) => meta)); // eslint-disable-line @typescript-eslint/no-unused-vars
}

/** Save a design to the account. Body: { design, id? } (id updates an existing one). */
export async function POST(req: Request) {
  if (!limit("account-save", clientIp(req), 120, 60 * 60_000)) return tooMany("You've saved a lot of maps in the last hour. Please try again later.", 600);
  const user = await currentUser();
  if (!user) return NextResponse.json({ error: "Sign in first" }, { status: 401 });
  const text = await req.text();
  if (text.length > MAX_BYTES) return NextResponse.json({ error: "Design too large" }, { status: 413 });
  const { design, id, name } = JSON.parse(text) as { design: Design; id?: string; name?: string };
  if (!design || !Array.isArray(design.stops)) return NextResponse.json({ error: "Invalid design" }, { status: 400 });
  return NextResponse.json({ id: await upsertSavedDesign(user.id, design, id, typeof name === "string" ? name : undefined) });
}
