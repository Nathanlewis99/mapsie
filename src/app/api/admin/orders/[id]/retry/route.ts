import { NextResponse, after } from "next/server";
import { getOrder } from "@/lib/server/db";
import { fulfilOrder } from "@/lib/server/fulfil";

/** Re-run rendering + print submission for an order (e.g. after a failure). */
export async function POST(_: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const o = await getOrder(id);
  if (!o?.address) return NextResponse.json({ error: "Order has no address yet" }, { status: 400 });
  after(() => fulfilOrder(id, o.address!));
  return NextResponse.json({ ok: true });
}
