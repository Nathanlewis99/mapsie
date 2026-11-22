import { NextResponse } from "next/server";
import { getPartner } from "@/lib/server/partners";
import { publicPartner } from "@/lib/partners";

// Public: a partner's name, welcome line and routes, for the designer to start from.
export async function GET(_req: Request, { params }: { params: Promise<{ id: string }> }) {
  const p = await getPartner((await params).id);
  if (!p?.active) return NextResponse.json({ error: "Not found" }, { status: 404 });
  return NextResponse.json(publicPartner(p), { headers: { "cache-control": "public, max-age=300" } });
}
