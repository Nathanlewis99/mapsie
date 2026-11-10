import { NextResponse } from "next/server";
import { nanoid } from "nanoid";
import Stripe from "stripe";
import { getDesign, saveOrder } from "@/lib/server/db";
import { getProduct, SHIPPING, type ShippingId } from "@/lib/products";

export async function POST(req: Request) {
  const { designId, email, shipping } = (await req.json()) as { designId: string; email: string; shipping: ShippingId };
  const design = await getDesign(designId);
  if (!design) return NextResponse.json({ error: "Design not found" }, { status: 404 });
  if (!/^\S+@\S+\.\S+$/.test(email ?? "")) return NextResponse.json({ error: "Please enter a valid email" }, { status: 400 });
  const product = getProduct(design.productId);
  const ship = SHIPPING.find((s) => s.id === shipping) ?? SHIPPING[0];
  const order = {
    id: `ord_${nanoid(10)}`,
    designId,
    email,
    shipping: ship.id,
    totalGbp: product.priceGbp + ship.priceGbp,
    status: "pending_payment" as const,
    createdAt: new Date().toISOString(),
  };
  await saveOrder(order);

  const base = process.env.APP_URL ?? new URL(req.url).origin;
  if (!process.env.STRIPE_SECRET_KEY) {
    // No Stripe keys yet: use the built-in test checkout.
    return NextResponse.json({ url: `${base}/checkout/test/${order.id}` });
  }

  const stripe = new Stripe(process.env.STRIPE_SECRET_KEY);
  const session = await stripe.checkout.sessions.create({
    mode: "payment",
    customer_email: email,
    line_items: [
      {
        quantity: 1,
        price_data: {
          currency: "gbp",
          unit_amount: product.priceGbp * 100,
          product_data: { name: `Mapsie print — ${design.title}`, description: `${product.label} ${design.orientation} art print` },
        },
      },
    ],
    shipping_address_collection: { allowed_countries: ["GB"] },
    shipping_options: SHIPPING.map((s) => ({
      shipping_rate_data: { type: "fixed_amount", display_name: s.label, fixed_amount: { amount: Math.round(s.priceGbp * 100), currency: "gbp" } },
    })),
    metadata: { orderId: order.id },
    success_url: `${base}/order/${order.id}`,
    cancel_url: `${base}/checkout/${designId}`,
  });
  return NextResponse.json({ url: session.url });
}
