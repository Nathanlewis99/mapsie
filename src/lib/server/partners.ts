// Partner programme storage and money: partners live in one key-value record (there are
// tens, not thousands). See ../partners.ts for what a partner is.
import Stripe from "stripe";
import { nanoid } from "nanoid";
import { getKv, listOrders, listGiftCards, putKv, updateOrder, type GiftCard, type Order } from "./db";
import { activate } from "./giftcards";
import { logError } from "./log";
import { commissionFor, PARTNER_ID, tradePrice, type Partner } from "../partners";
import { SHIPPING, getRegion, type RegionId } from "../products";

const KV = "partners";
const stripe = () => new Stripe(process.env.STRIPE_SECRET_KEY!);

export async function listPartners(): Promise<Partner[]> {
  return (await getKv<Partner[]>(KV))?.value ?? [];
}
export async function getPartner(id: string): Promise<Partner | null> {
  if (!PARTNER_ID.test(id)) return null;
  return (await listPartners()).find((p) => p.id === id) ?? null;
}
export async function savePartner(p: Partner) {
  if (!PARTNER_ID.test(p.id)) throw new Error("Partner id must be 3–40 lowercase letters, numbers or dashes");
  const all = await listPartners();
  const i = all.findIndex((x) => x.id === p.id);
  await putKv(KV, i < 0 ? [...all, p] : all.map((x, j) => (j === i ? p : x)));
}

/** The partner an order should be credited to at checkout: from the design's link, or the visit's partner UTM tag. */
export async function partnerForCheckout(designRef?: string, attribution?: { source?: string; medium?: string }) {
  const id = designRef ?? (attribution?.medium === "partner" ? attribution.source : undefined);
  const p = id ? await getPartner(id) : null;
  return p?.active ? p : null;
}

/** A customer discount code for a partner (e.g. COASTCYCLES10): a Stripe coupon and promotion code. */
export async function createPartnerCode(p: Partner, code: string, pct: number): Promise<Partner> {
  const s = stripe();
  const coupon = await s.coupons.create({ percent_off: pct, duration: "once", name: `${p.name} ${pct}% off`, metadata: { partnerId: p.id } }, { idempotencyKey: `partner-coupon-${p.id}-${code}-${pct}` });
  const promo = await s.promotionCodes.create({ promotion: { type: "coupon", coupon: coupon.id }, code: code.toUpperCase(), metadata: { partnerId: p.id } });
  const next = { ...p, discountPct: pct, promoCode: promo.code, promoId: promo.id, couponId: coupon.id };
  await savePartner(next);
  return next;
}

/** After an order is paid: credit the partner whose discount code was used (if not already credited by link). */
export async function creditPartnerCode(sessionId: string, orderId: string) {
  try {
    const s = stripe();
    const session = await s.checkout.sessions.retrieve(sessionId, { expand: ["total_details.breakdown"] });
    for (const d of session.total_details?.breakdown?.discounts ?? []) {
      const pc = d.discount.promotion_code;
      if (!pc) continue;
      const promo = typeof pc === "string" ? await s.promotionCodes.retrieve(pc) : pc;
      const id = promo.metadata?.partnerId;
      if (!id || promo.code?.startsWith("GIFT-")) continue;
      if (await getPartner(id)) await updateOrder(orderId, { partnerId: id, partnerVia: "code" });
      return;
    }
  } catch (e) {
    await logError("partner.code", e, { orderId });
  }
}

/** Prepaid trade codes: `count` gift-card codes worth `value` each, made for a partner to hand out. */
export async function issueTradeCodes(p: Partner, count: number, value: number, region: RegionId): Promise<{ batch: string; cards: GiftCard[] }> {
  if (count < 1 || count > 500) throw new Error("Between 1 and 500 codes at a time");
  if (!(value >= 5 && value <= 500)) throw new Error("Each code should be worth between 5 and 500");
  const batch = `tb_${nanoid(8)}`;
  const r = getRegion(region);
  const cards: GiftCard[] = [];
  for (let i = 0; i < count; i++) {
    cards.push(
      await activate({
        id: `gc_${batch.slice(3)}_${i + 1}`,
        status: "pending_payment",
        amount: value,
        currency: r.currency,
        region: r.id,
        buyerEmail: p.contactEmail ?? "",
        fromName: p.name,
        recipientName: "",
        message: "",
        partnerId: p.id,
        tradeBatch: batch,
        createdAt: new Date().toISOString(),
      }),
    );
  }
  return { batch, cards };
}

/** Send the partner a Stripe invoice for a batch of trade codes (Stripe emails it, payable by card or bank transfer). */
export async function invoiceTradeBatch(p: Partner, batch: string) {
  if (!p.contactEmail) throw new Error("Add the partner's contact email first");
  const cards = (await listGiftCards(5000)).filter((g) => g.tradeBatch === batch);
  if (!cards.length) throw new Error("No codes in that batch");
  const { amount, currency } = cards[0];
  const unit = tradePrice(amount, cards.length);
  const s = stripe();
  const existing = await s.customers.list({ email: p.contactEmail, limit: 1 });
  const customer = existing.data[0] ?? (await s.customers.create({ email: p.contactEmail, name: p.name, metadata: { partnerId: p.id } }));
  const invoice = await s.invoices.create(
    { customer: customer.id, collection_method: "send_invoice", days_until_due: 14, currency, metadata: { partnerId: p.id, tradeBatch: batch }, description: `${cards.length} Mapsie print codes worth ${amount} each, for ${p.name}.` },
    { idempotencyKey: `trade-invoice-${batch}` },
  );
  await s.invoiceItems.create(
    { customer: customer.id, invoice: invoice.id, currency, amount: Math.round(unit * 100) * cards.length, description: `${cards.length} × Mapsie print code (${amount} value) at trade price ${unit.toFixed(2)} each` },
    { idempotencyKey: `trade-item-${batch}` },
  );
  const final = await s.invoices.finalizeInvoice(invoice.id!);
  await s.invoices.sendInvoice(final.id!);
  return { url: final.hosted_invoice_url, total: (final.total ?? 0) / 100, currency };
}

export interface PartnerStats {
  orders: number;
  /** Per currency: what customers paid (less delivery) and the commission earned. */
  byCurrency: Record<string, { sales: number; commission: number; paidOut: number }>;
  tradeCodes: { issued: number; redeemed: number; batches: { batch: string; count: number; value: number; currency: string; redeemed: number; at: string }[] };
  recent: Order[];
}

const PAID: Order["status"][] = ["paid", "rendering", "ready", "submitted", "shipped", "delivered"];

export async function partnerStats(p: Partner, orders?: Order[], cards?: GiftCard[]): Promise<PartnerStats> {
  const mine = (orders ?? (await listOrders())).filter((o) => o.partnerId === p.id && PAID.includes(o.status));
  const byCurrency: PartnerStats["byCurrency"] = {};
  for (const o of mine) {
    const c = (byCurrency[o.currency] ??= { sales: 0, commission: 0, paidOut: 0 });
    const delivery = o.digital ? 0 : (SHIPPING.find((s) => s.id === o.shipping)?.price[o.region] ?? 0);
    c.sales += Math.max(0, o.total - delivery);
    // Orders paid with a prepaid trade code earn nothing more: the partner bought the code at trade price.
    if (o.partnerVia !== "trade") c.commission += commissionFor(p, o.total, delivery);
  }
  for (const pay of p.payouts ?? []) (byCurrency[pay.currency] ??= { sales: 0, commission: 0, paidOut: 0 }).paidOut += pay.amount;
  for (const c of Object.values(byCurrency)) for (const k of ["sales", "commission", "paidOut"] as const) c[k] = Math.round(c[k] * 100) / 100;
  const trade = (cards ?? (await listGiftCards(5000))).filter((g) => g.partnerId === p.id && g.tradeBatch);
  const batches = new Map<string, PartnerStats["tradeCodes"]["batches"][number]>();
  for (const g of trade) {
    const b = batches.get(g.tradeBatch!) ?? { batch: g.tradeBatch!, count: 0, value: g.amount, currency: g.currency, redeemed: 0, at: g.createdAt };
    b.count++;
    if (g.status === "redeemed") b.redeemed++;
    batches.set(g.tradeBatch!, b);
  }
  return {
    orders: mine.length,
    byCurrency,
    tradeCodes: { issued: trade.length, redeemed: trade.filter((g) => g.status === "redeemed").length, batches: [...batches.values()].sort((a, b) => b.at.localeCompare(a.at)) },
    recent: mine.slice(0, 20),
  };
}
