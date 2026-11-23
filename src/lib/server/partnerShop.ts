// What partners buy from their dashboard, paid by card on Stripe Checkout at trade prices:
//  - prints of a map they designed, in bulk, delivered to them (to hand out or sell);
//  - gift card codes for their customers to design their own maps.
import Stripe from "stripe";
import { nanoid } from "nanoid";
import { getDesign, getKv, putKv, saveDesign, saveOrder, type Order } from "./db";
import { issueTradeCodes, getPartner } from "./partners";
import { sendEmail } from "./email";
import { logError } from "./log";
import { publicUrl } from "./urls";
import { normalizeDesign } from "../types";
import { describeOptions, FRAMES, getRegion, itemPrice, PRODUCTS, type RegionId } from "../products";
import { tradeDiscountPct, tradePrice, type Partner } from "../partners";

const stripe = () => new Stripe(process.env.STRIPE_SECRET_KEY!);
const cents = (n: number) => Math.round(n * 100);
const branding = (base: string) => ({
  display_name: "Mapsie",
  background_color: "#fbf6ee",
  button_color: "#ff6b4a",
  border_style: "rounded" as const,
  font_family: "nunito" as const,
  icon: { type: "url" as const, url: `${base}/apple-icon.png` },
  logo: { type: "url" as const, url: `${base}/brand/mapsie-logo.png` },
});

export const MAX_COPIES = 250;
export const MAX_CODES = 250;

/** A quote for bulk prints of one of the partner's designs. */
export async function quotePrints(p: Partner, designId: string, productId: string, frame: string, copies: number) {
  if (!(p.designs ?? []).some((d) => d.id === designId)) throw new Error("That map isn't in your account");
  const raw = await getDesign(designId);
  if (!raw) throw new Error("That map couldn't be found");
  const n = Math.floor(copies);
  if (!(n >= 1 && n <= MAX_COPIES)) throw new Error(`Between 1 and ${MAX_COPIES} prints per order`);
  const region = getRegion((p.region ?? "GB") as RegionId);
  const design = normalizeDesign({
    ...raw,
    id: nanoid(10),
    format: "print",
    productId: PRODUCTS.some((x) => x.id === productId) ? productId : raw.productId,
    frame: FRAMES.some((x) => x.id === frame) ? (frame as typeof raw.frame) : raw.frame,
    partnerRef: p.id,
  });
  const retail = itemPrice(design, region.id);
  const unit = tradePrice(retail, n);
  return { design, region, retail, unit, copies: n, total: Math.round(unit * n * 100) / 100, discountPct: tradeDiscountPct(n) };
}

/** Bulk prints: an ordinary order (so it's rendered, printed and tracked as usual) with several copies. */
export async function checkoutPrints(p: Partner, buyerEmail: string, designId: string, productId: string, frame: string, copies: number) {
  const q = await quotePrints(p, designId, productId, frame, copies);
  await saveDesign(q.design);
  const order: Order = {
    id: `ord_${nanoid(10)}`,
    designId: q.design.id,
    email: buyerEmail,
    shipping: "standard",
    region: q.region.id,
    currency: q.region.currency,
    total: q.total,
    copies: q.copies,
    status: "pending_payment",
    partnerId: p.id,
    partnerVia: "trade",
    channel: "partners",
    createdAt: new Date().toISOString(),
  };
  await saveOrder(order);
  const base = publicUrl();
  if (!process.env.STRIPE_SECRET_KEY) return `${base}/checkout/test/${order.id}`;
  const session = await stripe().checkout.sessions.create({
    mode: "payment",
    customer_email: buyerEmail,
    line_items: [
      {
        quantity: q.copies,
        price_data: {
          currency: q.region.currency,
          unit_amount: cents(q.unit),
          product_data: { name: `Mapsie print: ${q.design.title}`, description: `${describeOptions(q.design)}. Trade price (${q.discountPct}% off).` },
        },
      },
    ],
    shipping_address_collection: { allowed_countries: q.region.shipTo as Stripe.Checkout.SessionCreateParams.ShippingAddressCollection.AllowedCountry[] },
    shipping_options: [{ shipping_rate_data: { type: "fixed_amount", display_name: "Free delivery (3–5 working days)", fixed_amount: { amount: 0, currency: q.region.currency } } }],
    metadata: { orderId: order.id, partnerId: p.id },
    payment_intent_data: { description: `Mapsie partner order ${order.id} (${p.name})`, metadata: { orderId: order.id, partnerId: p.id } },
    invoice_creation: { enabled: true, invoice_data: { description: `${q.copies} Mapsie prints for ${p.billing?.company ?? p.name}`, metadata: { partnerId: p.id } } },
    branding_settings: branding(base),
    success_url: `${base}/partner?p=${p.id}&msg=${encodeURIComponent("Thank you! Your prints are being made: we'll email you when they ship.")}`,
    cancel_url: `${base}/partner?p=${p.id}#maps`,
  });
  return session.url!;
}

/** Gift card codes: paid now, made by the webhook. */
export async function checkoutGiftCodes(p: Partner, buyerEmail: string, count: number, value: number) {
  const n = Math.floor(count);
  if (!(n >= 1 && n <= MAX_CODES)) throw new Error(`Between 1 and ${MAX_CODES} gift cards at a time`);
  if (!(value >= 10 && value <= 500)) throw new Error("Each gift card can be worth 10 to 500");
  const region = getRegion((p.region ?? "GB") as RegionId);
  const unit = tradePrice(value, n);
  const base = publicUrl();
  if (!process.env.STRIPE_SECRET_KEY) throw new Error("Payments aren't set up on this server");
  const session = await stripe().checkout.sessions.create({
    mode: "payment",
    customer_email: buyerEmail,
    line_items: [
      {
        quantity: n,
        price_data: {
          currency: region.currency,
          unit_amount: cents(unit),
          product_data: { name: `Mapsie gift card worth ${region.symbol}${value}`, description: `For ${p.name}'s customers to design their own map. Trade price (${tradeDiscountPct(n)}% off). Codes appear in your partner dashboard straight away.` },
        },
      },
    ],
    metadata: { partnerGift: "1", partnerId: p.id, count: String(n), value: String(value), region: region.id },
    payment_intent_data: { description: `Mapsie gift cards for ${p.name}`, metadata: { partnerId: p.id } },
    invoice_creation: { enabled: true, invoice_data: { description: `${n} Mapsie gift cards for ${p.billing?.company ?? p.name}`, metadata: { partnerId: p.id } } },
    branding_settings: branding(base),
    success_url: `${base}/partner?p=${p.id}&msg=${encodeURIComponent("Thank you! Your gift cards are ready below (refresh in a moment if not).")}#codes`,
    cancel_url: `${base}/partner?p=${p.id}#codes`,
  });
  return session.url!;
}

/** From the Stripe webhook: gift codes paid for. Exactly once per payment. */
export async function completeGiftPurchase(s: Stripe.Checkout.Session) {
  const m = s.metadata ?? {};
  try {
    if (await getKv(`pgift:${s.id}`)) return;
    await putKv(`pgift:${s.id}`, { at: new Date().toISOString() });
    const p = await getPartner(m.partnerId ?? "");
    if (!p) throw new Error(`Unknown partner ${m.partnerId}`);
    const { batch, cards } = await issueTradeCodes(p, Number(m.count), Number(m.value), (m.region ?? "GB") as RegionId);
    const total = (s.amount_total ?? 0) / 100;
    const fresh = (await getPartner(p.id)) ?? p;
    const { savePartner } = await import("./partners");
    await savePartner({ ...fresh, invoices: [...(fresh.invoices ?? []), { batch, url: null, total, currency: s.currency ?? "gbp", at: new Date().toISOString() }] });
    const to = s.customer_details?.email ?? s.customer_email;
    if (to)
      await sendEmail({
        to,
        subject: `Your ${cards.length} Mapsie gift cards are ready`,
        text: `Thank you! ${cards.length} gift cards for ${p.name} are ready.\n\nDownload the codes, or print them as cards to hand out, from your dashboard: ${publicUrl()}/partner?p=${p.id}#codes\n\nMapsie`,
        html: `<p>Thank you! <b>${cards.length} gift cards</b> for ${p.name.replace(/[<>&"]/g, "")} are ready.</p><p>Download the codes, or print them as cards to hand out, from <a href="${publicUrl()}/partner?p=${p.id}#codes">your dashboard</a>.</p><p>Mapsie</p>`,
      });
  } catch (e) {
    await logError("partner.gift", e, { session: s.id, partnerId: m.partnerId });
    const { alertAdmin } = await import("./email");
    await alertAdmin("Partner gift card purchase needs a look", `Stripe session ${s.id} for partner ${m.partnerId} was paid, but making the codes failed: ${String((e as Error)?.message ?? e)}. Make them by hand in /admin/partners (${m.count} × ${m.value}).`);
  }
}
