import { NextResponse } from "next/server";
import { nanoid } from "nanoid";
import { saveDesign } from "@/lib/server/db";
import type { Design } from "@/lib/types";

export async function POST(req: Request) {
  const text = await req.text();
  if (text.length > 15_000_000) return NextResponse.json({ error: "Design too large" }, { status: 413 });
  const design = JSON.parse(text) as Design;
  if (!Array.isArray(design.stops) || !design.view) return NextResponse.json({ error: "Invalid design" }, { status: 400 });
  // Every order gets its own frozen snapshot of the design.
  const saved = { ...design, id: nanoid(12) };
  await saveDesign(saved);
  return NextResponse.json({ id: saved.id });
}
