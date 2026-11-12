import { NextResponse } from "next/server";
import { getOrder } from "@/lib/server/db";
import { canCancel } from "@/lib/server/fulfil";

export async function GET(_: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const o = await getOrder(id);
  if (!o) return NextResponse.json({ error: "not found" }, { status: 404 });
  const { status, renderFile, renderInfo, total, currency, region, shipping, printProviderOrderId, designId, holdUntil, refunded, shipments } = o;
  return NextResponse.json(
    { status, renderFile, renderInfo, total, currency, region, shipping, printProviderOrderId, designId, holdUntil, refunded, shipments, canCancel: canCancel(o) },
    { headers: { "cache-control": "no-store" } },
  );
}
