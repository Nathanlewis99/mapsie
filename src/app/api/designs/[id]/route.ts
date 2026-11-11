import { NextResponse } from "next/server";
import { getDesign } from "@/lib/server/db";

export async function GET(_: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const d = await getDesign(id);
  if (!d) return NextResponse.json({ error: "not found" }, { status: 404 });
  return NextResponse.json(d);
}
