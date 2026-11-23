import { NextResponse } from "next/server";
import { nanoid } from "nanoid";
import { sameOrigin } from "@/lib/server/rateLimit";
import { currentPartner } from "@/lib/server/partnerAuth";
import { saveDesign } from "@/lib/server/db";
import { savePartner } from "@/lib/server/partners";
import { publicUrl } from "@/lib/server/urls";
import { normalizeDesign, type Design } from "@/lib/types";

// From the designer: save this map to the signed-in partner's account.
export async function POST(req: Request) {
  if (!sameOrigin(req, publicUrl())) return NextResponse.json({ error: "Bad request" }, { status: 400 });
  const text = await req.text();
  if (text.length > 15_000_000) return NextResponse.json({ error: "That map is too large" }, { status: 413 });
  const b = JSON.parse(text) as { design?: Design; partnerId?: string; name?: string };
  const s = await currentPartner(b.partnerId);
  if (!s) return NextResponse.json({ error: "Please sign in to your partner dashboard first" }, { status: 401 });
  if (!b.design || !Array.isArray(b.design.stops) || !b.design.view) return NextResponse.json({ error: "Invalid map" }, { status: 400 });
  if ((s.partner.designs ?? []).length >= 100) return NextResponse.json({ error: "You have 100 maps saved: remove some in your dashboard first" }, { status: 400 });
  // A fixed copy: customers who buy it from the partner's page credit the partner.
  const design = normalizeDesign({ ...b.design, id: nanoid(10), partnerRef: s.partner.id });
  await saveDesign(design);
  const name = (b.name ?? design.title ?? "Untitled map").trim().slice(0, 80) || "Untitled map";
  await savePartner({ ...s.partner, designs: [{ id: design.id, name, published: false, addedAt: new Date().toISOString() }, ...(s.partner.designs ?? [])] });
  return NextResponse.json({ ok: true, id: design.id, partner: s.partner.name });
}
