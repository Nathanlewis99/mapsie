import { NextResponse } from "next/server";
import Stripe from "stripe";
import { nanoid } from "nanoid";
import { saveGiftCard, type GiftCard } from "@/lib/server/db";
import { giftToken } from "@/lib/server/giftcards";
import { validEmail } from "@/lib/server/password";
import { clientIp, limit, sameOrigin, tooMany } from "@/lib/server/rateLimit";
import { publicUrl } from "@/lib/server/urls";
import { getRegion } from "@/lib/products";
import { GIFT_MAX, GIFT_MIN } from "@/lib/giftcards";

const clean = (v: unknown, max: number) => (typeof v === "string" ? v.replace(/[\u0000-\u001f]/g, " ").trim().slice(0, max) : "");

/** Start paying for a gift card. POST { amount, region, buyerEmail, fromName, recipientName, message, recipientEmail?, sendOn? } */
export async function POST(req: Request) {
  if (!sameOrigin(req, publicUrl())) return NextResponse.json({ error: "Not allowed" }, { status: 403 });
  if (!limit("gift-checkout", clientIp(req), 15, 60 * 60_000)) return tooMany("Too many attempts. Please wait a few minutes.", 600);
  const b = (await req.json().catch(() => ({}))) as Record<string, unknown>;
  const region = getRegion(typeof b.region === "string" ? (b.region as never) : "GB");
  const amount = Math.round(Number(b.amount));
  if (!Number.isFinite(amount) || amount < GIFT_MIN || amount > GIFT_MAX) return NextResponse.json({ error: `Choose an amount between ${region.symbol}${GIFT_MIN} and ${region.symbol}${GIFT_MAX}.` }, { status: 400 });
  const buyerEmail = clean(b.buyerEmail, 200);
  if (!validEmail(buyerEmail)) return NextResponse.json({ error: "Please enter your email address." }, { status: 400 });
  const recipientEmail = clean(b.recipientEmail, 200);
  if (recipientEmail && !validEmail(recipientEmail)) return NextResponse.json({ error: "That recipient email doesn't look right." }, { status: 400 });
  const sendOn = clean(b.sendOn, 10);
  const today = new Date().toISOString().slice(0, 10);
  const maxDate = new Date(Date.now() + 365 * 24 * 3600_000).toISOString().slice(0, 10);
  if (sendOn && (!/^\d{4}-\d{2}-\d{2}$/.test(sendOn) || sendOn < today || sendOn > maxDate)) return NextResponse.json({ error: "Choose a send date within the next year." }, { status: 400 });

  const g: GiftCard = {
    id: `gc_${nanoid(12)}`,
    status: "pending_payment",
    amount,
    currency: region.currency,
    region: region.id,
    buyerEmail,
    fromName: clean(b.fromName, 60),
    recipientName: clean(b.recipientName, 60),
    message: clean(b.message, 300),
    ...(recipientEmail ? { recipientEmail, ...(sendOn ? { sendOn } : {}) } : {}),
    createdAt: new Date().toISOString(),
  };
  await saveGiftCard(g);
  const base = publicUrl();
  if (!process.env.STRIPE_SECRET_KEY) return NextResponse.json({ error: "Payments aren't set up yet." }, { status: 503 });
  const session = await new Stripe(process.env.STRIPE_SECRET_KEY).checkout.sessions.create({
    mode: "payment",
    customer_email: buyerEmail,
    line_items: [{
      quantity: 1,
      price_data: {
        currency: region.currency,
        unit_amount: amount * 100,
        product_data: { name: `Mapsie gift card ${region.symbol}${amount}`, description: g.recipientName ? `For ${g.recipientName}` : "A custom map print of their trip" },
      },
    }],
    metadata: { giftCardId: g.id },
    payment_intent_data: { description: `Mapsie gift card ${g.id}`, metadata: { giftCardId: g.id } },
    branding_settings: {
      display_name: "Mapsie",
      background_color: "#fbf6ee",
      button_color: "#ff6b4a",
      border_style: "rounded",
      font_family: "nunito",
      icon: { type: "url", url: `${base}/apple-icon.png` },
      logo: { type: "url", url: `${base}/brand/mapsie-logo.png` },
    },
    success_url: `${base}/gift/thanks/${g.id}?k=${giftToken(g.id)}`,
    cancel_url: `${base}/gift`,
  });
  await saveGiftCard({ ...g, stripeSessionId: session.id });
  return NextResponse.json({ url: session.url });
}
