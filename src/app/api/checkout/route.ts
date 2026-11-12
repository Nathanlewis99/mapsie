import { NextResponse } from "next/server";
import { nanoid } from "nanoid";
import Stripe from "stripe";
import { getDesign, saveOrder, type Order } from "@/lib/server/db";
import { FRAMES, getProduct, getRegion, itemPrice, SHIPPING, type RegionId, type ShippingId } from "@/lib/products";
import { normalizeDesign } from "@/lib/types";

export async function POST(req: Request) {
  const body = (await req.json()) as { designId: string; email: string; shipping: ShippingId; region: RegionId };
  const raw = await getDesign(body.designId);
  if (!raw) return NextResponse.json({ error: "Design not found" }, { status: 404 });
  if (!/^\S+@\S+\.\S+$/.test(body.email ?? "")) return NextResponse.json({ error: "Please enter a valid email" }, { status: 400 });
  const design = normalizeDesign(raw);
  const region = getRegion(body.region);
  const product = getProduct(design.productId);
  const ship = SHIPPING.find((s) => s.id === body.shipping) ?? SHIPPING[0];
  // Prices are always worked out on the server, never trusted from the browser.
  const item = itemPrice(design.productId, design.frame, region.id);
  const order: Order = {
    id: `ord_${nanoid(10)}`,
    designId: design.id,
    email: body.email,
    shipping: ship.id,
    region: region.id,
    currency: region.currency,
    total: item + ship.price[region.id],
    status: "pending_payment",
    createdAt: new Date().toISOString(),
  };
  await saveOrder(order);

  const base = process.env.APP_URL ?? process.env.RENDER_EXTERNAL_URL ?? new URL(req.url).origin;
  if (!process.env.STRIPE_SECRET_KEY) {
    // No Stripe keys yet: use the built-in test checkout.
    return NextResponse.json({ url: `${base}/checkout/test/${order.id}` });
  }

  const frame = FRAMES.find((f) => f.id === design.frame);
  const stripe = new Stripe(process.env.STRIPE_SECRET_KEY);
  const cents = (n: number) => Math.round(n * 100);
  const session = await stripe.checkout.sessions.create({
    mode: "payment",
    customer_email: body.email,
    line_items: [
      {
        quantity: 1,
        price_data: {
          currency: region.currency,
          unit_amount: cents(item),
          product_data: {
            name: `Mapsie print: ${design.title}`,
            description: `${product.label} ${design.orientation} art print${design.frame !== "none" ? `, ${frame?.label.toLowerCase()} frame` : ""}`,
          },
        },
      },
    ],
    shipping_address_collection: { allowed_countries: region.shipTo as Stripe.Checkout.SessionCreateParams.ShippingAddressCollection.AllowedCountry[] },
    shipping_options: [
      {
        shipping_rate_data: {
          type: "fixed_amount",
          display_name: `${ship.label} (${ship.detail})`,
          fixed_amount: { amount: cents(ship.price[region.id]), currency: region.currency },
        },
      },
    ],
    metadata: { orderId: order.id },
    success_url: `${base}/order/${order.id}`,
    cancel_url: `${base}/checkout/${design.id}`,
  });
  return NextResponse.json({ url: session.url });
}
