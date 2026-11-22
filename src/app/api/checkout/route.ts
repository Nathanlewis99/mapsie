import { NextResponse } from "next/server";
import { clientIp, limit, tooMany } from "@/lib/server/rateLimit";
import { adConsentFrom } from "@/lib/server/conversions";
import { classifyChannel, cleanAttribution } from "@/lib/channels";
import { nanoid } from "nanoid";
import Stripe from "stripe";
import { getDesign, saveDesign, saveOrder, type Order } from "@/lib/server/db";
import { describeOptions, FRAMES, GLAZES, getRegion, itemPrice, MOUNTS, PAPERS, PRODUCTS, SHIPPING, type PrintOptions, type RegionId, type ShippingId } from "@/lib/products";
import { normalizeDesign } from "@/lib/types";
import { currentUser } from "@/lib/server/auth";
import { partnerForCheckout } from "@/lib/server/partners";

export async function POST(req: Request) {
  if (!limit("checkout", clientIp(req), 20, 60 * 60_000)) return tooMany("Too many checkout attempts. Please wait a few minutes.", 600);
  const body = (await req.json()) as { designId: string; email: string; shipping: ShippingId; region: RegionId; options?: Partial<PrintOptions>; visitId?: string };
  const raw = await getDesign(body.designId);
  if (!raw) return NextResponse.json({ error: "Design not found" }, { status: 404 });
  if (!/^\S+@\S+\.\S+$/.test(body.email ?? "")) return NextResponse.json({ error: "Please enter a valid email" }, { status: 400 });
  let design = normalizeDesign(raw);
  // Size, frame and paper can still be changed at checkout. Only known values are accepted.
  const o = body.options ?? {};
  const pick = <T extends { id: string }>(list: T[], v: unknown, fallback: T["id"]) => (list.some((x) => x.id === v) ? (v as T["id"]) : fallback);
  const chosen = {
    format: o.format === "digital" ? ("digital" as const) : ("print" as const),
    productId: pick(PRODUCTS, o.productId, design.productId),
    frame: pick(FRAMES, o.frame, design.frame),
    paper: pick(PAPERS, o.paper, design.paper),
    mount: pick(MOUNTS, o.mount, design.mount),
    glaze: pick(GLAZES, o.glaze, design.glaze),
  };
  if (Object.entries(chosen).some(([k, v]) => (design[k as keyof typeof chosen] ?? (k === "format" ? "print" : undefined)) !== v)) {
    // Keep shared snapshots unchanged: the order gets its own copy.
    design = { ...design, ...chosen, id: nanoid(10) };
    await saveDesign(design);
  }
  const region = getRegion(body.region);
  const ship = SHIPPING.find((s) => s.id === body.shipping) ?? SHIPPING[0];
  // Prices are always worked out on the server, never trusted from the browser.
  const item = itemPrice(design, region.id);
  const order: Order = {
    id: `ord_${nanoid(10)}`,
    designId: design.id,
    userId: (await currentUser())?.id,
    email: body.email,
    shipping: ship.id,
    region: region.id,
    currency: region.currency,
    total: item + (design.format === "digital" ? 0 : ship.price[region.id]),
    ...(design.format === "digital" ? { digital: true } : {}),
    status: "pending_payment",
    visitId: typeof body.visitId === "string" && /^[a-z0-9]{8,40}$/.test(body.visitId) ? body.visitId : undefined,
    adConsent: adConsentFrom(req, clientIp(req)),
    ...(await (async () => {
      const attribution = cleanAttribution((body as { attribution?: unknown }).attribution);
      // Started from a partner's link (or arrived on one): credit that partner.
      const partner = await partnerForCheckout(design.partnerRef, attribution);
      return { attribution, channel: partner ? ("partners" as const) : classifyChannel(attribution), ...(partner ? { partnerId: partner.id, partnerVia: "link" as const } : {}) };
    })()),
    createdAt: new Date().toISOString(),
  };
  await saveOrder(order);

  const base = process.env.APP_URL ?? process.env.RENDER_EXTERNAL_URL ?? new URL(req.url).origin;
  if (!process.env.STRIPE_SECRET_KEY) {
    // No Stripe keys yet: use the built-in test checkout.
    return NextResponse.json({ url: `${base}/checkout/test/${order.id}` });
  }

  const stripe = new Stripe(process.env.STRIPE_SECRET_KEY);
  const cents = (n: number) => Math.round(n * 100);
  // Stripe Tax: switch on (STRIPE_TAX=on) once registered for VAT or sales tax somewhere and the
  // registration is added in Stripe. Prices stay tax-inclusive, so customers see the same totals.
  const tax = process.env.STRIPE_TAX === "on";
  const session = await stripe.checkout.sessions.create({
    mode: "payment",
    // Discount codes are created in the Stripe dashboard (Products > Coupons > promotion codes).
    allow_promotion_codes: true,
    customer_email: body.email,
    line_items: [
      {
        quantity: 1,
        price_data: {
          currency: region.currency,
          unit_amount: cents(item),
          ...(tax ? { tax_behavior: "inclusive" as const } : {}),
          product_data: {
            ...(tax ? { tax_code: "txcd_99999999" } : {}), // general tangible goods (printed posters)
            name: `Mapsie print: ${design.title}`,
            description: `Art print: ${describeOptions(design)}`,
          },
        },
      },
    ],
    // A digital file has nothing to post: no address or delivery options.
    ...(design.format === "digital" ? {} : {
    shipping_address_collection: { allowed_countries: region.shipTo as Stripe.Checkout.SessionCreateParams.ShippingAddressCollection.AllowedCountry[] },
    shipping_options: [
      {
        shipping_rate_data: {
          type: "fixed_amount",
          display_name: `${ship.label} (${ship.detail})`,
          fixed_amount: { amount: cents(ship.price[region.id]), currency: region.currency },
          ...(tax ? { tax_behavior: "inclusive" as const, tax_code: "txcd_92010001" } : {}), // shipping
        },
      },
    ],
    }),
    metadata: { orderId: order.id },
    // Stripe's payment page in Mapsie's colours, font, icon and wordmark.
    branding_settings: {
      display_name: "Mapsie",
      background_color: "#fbf6ee",
      button_color: "#ff6b4a",
      border_style: "rounded",
      font_family: "nunito",
      icon: { type: "url", url: `${base}/apple-icon.png` },
      logo: { type: "url", url: `${base}/brand/mapsie-logo.png` },
    },
    // Shown on the payment in the Stripe dashboard, so payments and orders are easy to match up.
    payment_intent_data: { description: `Mapsie order ${order.id}`, metadata: { orderId: order.id } },
    ...(tax ? { automatic_tax: { enabled: true } } : {}),
    success_url: `${base}/order/${order.id}`,
    cancel_url: `${base}/checkout/${body.designId}`,
  });
  return NextResponse.json({ url: session.url });
}
