import { NextResponse } from "next/server";
import { getOrder } from "@/lib/server/db";
import { etsyTokenValid } from "@/lib/server/etsy";
import { getProduct, FRAMES } from "@/lib/products";

/** For the editor: what an Etsy buyer paid for (needs the token from their link). */
export async function GET(req: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const k = new URL(req.url).searchParams.get("k");
  const o = await getOrder(id);
  if (!o?.etsy || !o.print || !etsyTokenValid(id, k)) return NextResponse.json({ error: "Not found" }, { status: 404 });
  return NextResponse.json({
    id: o.id,
    status: o.status,
    receiptId: o.etsy.receiptId,
    unit: o.etsy.unit,
    of: o.etsy.of,
    productId: o.print.productId,
    frame: o.print.frame,
    label: `${getProduct(o.print.productId).label} · ${FRAMES.find((f) => f.id === o.print!.frame)?.label ?? "No frame"}`,
    designId: o.designId || null,
  }, { headers: { "cache-control": "no-store" } });
}
