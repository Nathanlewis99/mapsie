import { NextResponse } from "next/server";
import { currentPartner } from "@/lib/server/partnerAuth";

// For the designer: is a partner signed in on this browser? (Shows "Save to <partner>".)
export async function GET() {
  const s = await currentPartner();
  if (!s) return NextResponse.json({ partner: null }, { headers: { "cache-control": "no-store" } });
  return NextResponse.json({ partner: { id: s.partner.id, name: s.partner.name }, all: s.all.map((p) => ({ id: p.id, name: p.name })) }, { headers: { "cache-control": "no-store" } });
}
