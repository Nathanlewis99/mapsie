import { NextResponse, after } from "next/server";
import Stripe from "stripe";
import { fulfilOrder } from "@/lib/server/fulfil";

export async function POST(req: Request) {
  const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!);
  const sig = req.headers.get("stripe-signature") ?? "";
  let event: Stripe.Event;
  try {
    event = stripe.webhooks.constructEvent(await req.text(), sig, process.env.STRIPE_WEBHOOK_SECRET!);
  } catch {
    return NextResponse.json({ error: "bad signature" }, { status: 400 });
  }
  if (event.type === "checkout.session.completed") {
    const s = event.data.object as Stripe.Checkout.Session;
    const orderId = s.metadata?.orderId;
    const ship = s.collected_information?.shipping_details;
    if (orderId && ship?.address) {
      const a = ship.address;
      after(() =>
        fulfilOrder(orderId, {
          name: ship.name,
          line1: a.line1 ?? "",
          line2: a.line2 ?? undefined,
          city: a.city ?? "",
          postcode: a.postal_code ?? "",
          country: a.country ?? "GB",
        }),
      );
    }
  }
  return NextResponse.json({ received: true });
}
