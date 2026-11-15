import { NextResponse, after } from "next/server";
import Stripe from "stripe";
import { fulfilOrder, markPaymentFailed } from "@/lib/server/fulfil";

export async function POST(req: Request) {
  const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!);
  const sig = req.headers.get("stripe-signature") ?? "";
  let event: Stripe.Event;
  try {
    event = stripe.webhooks.constructEvent(await req.text(), sig, process.env.STRIPE_WEBHOOK_SECRET!);
  } catch {
    return NextResponse.json({ error: "bad signature" }, { status: 400 });
  }
  // Fulfil only once the money is actually in: card payments are paid at "completed";
  // delayed methods (bank debits, some pay-later) finish later with "async_payment_succeeded".
  if (event.type === "checkout.session.completed" || event.type === "checkout.session.async_payment_succeeded") {
    const s = event.data.object as Stripe.Checkout.Session;
    const orderId = s.metadata?.orderId;
    const ship = s.collected_information?.shipping_details;
    if (orderId && ship?.address && s.payment_status === "paid") {
      const a = ship.address;
      after(() =>
        fulfilOrder(orderId, {
          name: ship.name,
          line1: a.line1 ?? "",
          line2: a.line2 ?? undefined,
          city: a.city ?? "",
          state: a.state ?? undefined,
          postcode: a.postal_code ?? "",
          country: a.country ?? "GB",
        }, {
          stripePaymentIntent: typeof s.payment_intent === "string" ? s.payment_intent : s.payment_intent?.id,
          // What Stripe actually charged (after any discount code), for the order record.
          ...(s.amount_total != null ? { total: s.amount_total / 100 } : {}),
        }),
      );
    }
  }
  if (event.type === "checkout.session.async_payment_failed") {
    const orderId = (event.data.object as Stripe.Checkout.Session).metadata?.orderId;
    if (orderId) after(() => markPaymentFailed(orderId));
  }
  return NextResponse.json({ received: true });
}
