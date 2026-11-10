import { NextResponse, after } from "next/server";
import { getOrder, type Address } from "@/lib/server/db";
import { fulfilOrder } from "@/lib/server/fulfil";

// Test checkout, only available while Stripe isn't configured.
export async function POST(req: Request, { params }: { params: Promise<{ id: string }> }) {
  if (process.env.STRIPE_SECRET_KEY) return NextResponse.json({ error: "disabled" }, { status: 404 });
  const { id } = await params;
  const order = await getOrder(id);
  if (!order || order.status !== "pending_payment") return NextResponse.json({ error: "Order not payable" }, { status: 400 });
  const address = (await req.json()) as Address;
  after(() => fulfilOrder(id, { ...address, country: "GB" }));
  return NextResponse.json({ ok: true });
}
