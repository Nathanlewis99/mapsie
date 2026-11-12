import { NextResponse } from "next/server";
import Stripe from "stripe";
import { getOrder, updateOrder } from "@/lib/server/db";
import { canCancel } from "@/lib/server/fulfil";
import { logError } from "@/lib/server/log";
import { sendOrderEmail } from "@/lib/server/email";

/** Customer cancels within the hold window: full refund, never sent to print. */
export async function POST(_: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const o = await getOrder(id);
  if (!o) return NextResponse.json({ error: "Order not found" }, { status: 404 });
  if (!canCancel(o)) return NextResponse.json({ error: "Sorry, this order has already gone to print and can't be cancelled." }, { status: 409 });

  let refunded = false;
  if (process.env.STRIPE_SECRET_KEY && o.stripePaymentIntent) {
    try {
      await new Stripe(process.env.STRIPE_SECRET_KEY).refunds.create({ payment_intent: o.stripePaymentIntent });
      refunded = true;
    } catch (e) {
      void logError("order.refund", e, { orderId: id });
      return NextResponse.json({ error: "We couldn't process the refund automatically. Please email us and we'll sort it." }, { status: 502 });
    }
  }
  await updateOrder(id, { status: "cancelled", cancelledAt: new Date().toISOString(), refunded });
  await sendOrderEmail(id, "cancelled");
  return NextResponse.json({ ok: true, refunded });
}
