import { NextResponse, after } from "next/server";
import Stripe from "stripe";
import { fulfilOrder, markPaymentFailed } from "@/lib/server/fulfil";
import { issueGiftCard, settleGiftCards } from "@/lib/server/giftcards";
import { creditPartnerCode } from "@/lib/server/partners";

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
    // A gift card: create its code and send it.
    const giftCardId = s.metadata?.giftCardId;
    if (giftCardId && s.payment_status === "paid") after(() => issueGiftCard(giftCardId, s.id));
    const orderId = s.metadata?.orderId;
    const ship = s.collected_information?.shipping_details;
    // Digital files have no delivery address.
    // "no_payment_required": a gift card or discount covered the whole order.
    const settled = s.payment_status === "paid" || s.payment_status === "no_payment_required";
    if (orderId && settled && (ship?.address || !s.shipping_address_collection)) {
      const a = ship?.address;
      after(() =>
        fulfilOrder(orderId, a ? {
          name: ship!.name,
          line1: a.line1 ?? "",
          line2: a.line2 ?? undefined,
          city: a.city ?? "",
          state: a.state ?? undefined,
          postcode: a.postal_code ?? "",
          country: a.country ?? "GB",
        } : undefined, {
          stripePaymentIntent: typeof s.payment_intent === "string" ? s.payment_intent : s.payment_intent?.id,
          // What Stripe actually charged (after any discount code), for the order record.
          ...(s.amount_total != null ? { total: s.amount_total / 100 } : {}),
        }),
      );
      // If a gift card paid for some of it: mark it used, and send any balance as a new code.
      if (s.total_details?.amount_discount) {
        after(() => settleGiftCards(s.id, orderId, s.customer_details?.email ?? s.customer_email ?? ""));
        // A partner's discount code: credit that partner.
        after(() => creditPartnerCode(s.id, orderId));
      }
    }
  }
  if (event.type === "checkout.session.async_payment_failed") {
    const orderId = (event.data.object as Stripe.Checkout.Session).metadata?.orderId;
    if (orderId) after(() => markPaymentFailed(orderId));
  }
  return NextResponse.json({ received: true });
}
