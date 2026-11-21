import { NextResponse } from "next/server";
import { nanoid } from "nanoid";
import { clientIp, limit, tooMany } from "@/lib/server/rateLimit";
import { currentUser } from "@/lib/server/auth";
import { getSavedDesign, upsertSavedDesign } from "@/lib/server/db";

/** Copy one of the user's saved maps (everything in place), so they can try changes on the copy. */
export async function POST(req: Request, { params }: { params: Promise<{ id: string }> }) {
  if (!limit("account-save", clientIp(req), 120, 60 * 60_000)) return tooMany("You've saved a lot of maps in the last hour. Please try again later.", 600);
  const user = await currentUser();
  if (!user) return NextResponse.json({ error: "Sign in first" }, { status: 401 });
  const src = await getSavedDesign(user.id, (await params).id);
  if (!src) return NextResponse.json({ error: "Not found" }, { status: 404 });
  // A new design id, so the copy's previews and orders never mix with the original's.
  const id = await upsertSavedDesign(user.id, { ...src.design, id: nanoid(10) }, undefined, `${src.title} (copy)`);
  return NextResponse.json({ id });
}
