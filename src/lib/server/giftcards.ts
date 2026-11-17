// Gift cards. The buyer pays on Stripe Checkout; once paid we create a Stripe coupon
// for the amount and a single-use promotion code (GIFT-XXXX-XXXX) the recipient enters
// at checkout. If an order uses less than the card's value, the rest comes back as a
// new code, so nothing is lost.
import { createHmac, randomInt, timingSafeEqual } from "node:crypto";
import Stripe from "stripe";
import { claimGiftCard, getGiftCard, getGiftCardByCode, listGiftCardsToSend, saveGiftCard, updateGiftCard, type GiftCard } from "./db";
import { sendGiftCardEmail } from "./email";
import { logError } from "./log";
import { publicUrl } from "./urls";
import { GIFT_VALID_YEARS } from "../giftcards";
import { nanoid } from "nanoid";

const stripe = () => new Stripe(process.env.STRIPE_SECRET_KEY!);
const secret = () => process.env.SESSION_SECRET ?? "dev-only-session-secret-change-me-0123456789";
export const giftToken = (id: string) => createHmac("sha256", secret()).update(`gift:${id}`).digest("base64url").slice(0, 22);
export function giftTokenValid(id: string, k: string | null | undefined) {
  const want = Buffer.from(giftToken(id));
  const got = Buffer.from(k ?? "");
  return got.length === want.length && timingSafeEqual(got, want);
}
export const giftCardUrl = (id: string) => `${publicUrl()}/gift/card/${id}?k=${giftToken(id)}`;

// No 0/O, 1/I/L, so codes are easy to read out and type.
const ALPHABET = "ABCDEFGHJKMNPQRSTUVWXYZ23456789";
const block = () => Array.from({ length: 4 }, () => ALPHABET[randomInt(ALPHABET.length)]).join("");
export const newGiftCode = () => `GIFT-${block()}-${block()}`;

/** Create the Stripe coupon and code for a paid (or balance) card, and mark it active. */
async function activate(g: GiftCard): Promise<GiftCard> {
  const s = stripe();
  const symbol = { gbp: "£", usd: "$", aud: "A$" }[g.currency] ?? "";
  const coupon = await s.coupons.create(
    { amount_off: Math.round(g.amount * 100), currency: g.currency, duration: "once", name: `Gift card ${symbol}${g.amount}`, metadata: { giftCardId: g.id } },
    { idempotencyKey: `gift-coupon-${g.id}` },
  );
  const expires = new Date();
  expires.setFullYear(expires.getFullYear() + GIFT_VALID_YEARS);
  let promo: Stripe.PromotionCode | null = null;
  for (let attempt = 0; attempt < 5 && !promo; attempt++) {
    try {
      promo = await s.promotionCodes.create({
        promotion: { type: "coupon", coupon: coupon.id },
        code: newGiftCode(),
        max_redemptions: 1,
        expires_at: Math.floor(expires.getTime() / 1000),
        metadata: { giftCardId: g.id },
      });
    } catch (e) {
      if (attempt === 4) throw e; // a clash with an existing code is the only expected failure
    }
  }
  const active: GiftCard = { ...g, status: "active", code: promo!.code, couponId: coupon.id, promoId: promo!.id, expiresAt: expires.toISOString() };
  await saveGiftCard(active);
  return active;
}

/** From the Stripe webhook: a gift card was paid for. Exactly once. */
export async function issueGiftCard(id: string, sessionId?: string) {
  const g = await claimGiftCard(id, "pending_payment", "active");
  if (!g) return;
  try {
    const card = await activate({ ...g, stripeSessionId: sessionId ?? g.stripeSessionId });
    await sendGiftCardEmail(card, "buyer");
    await sendDueGiftCards();
  } catch (e) {
    await updateGiftCard(id, { status: "pending_payment" }); // so a webhook retry tries again
    await logError("gift.issue", e, { giftCardId: id });
    throw e;
  }
}

/**
 * After an order is paid: if it used a gift code, mark that card used, and if the order
 * cost less than the card, send the rest as a new code.
 */
export async function settleGiftCards(sessionId: string, orderId: string, email: string) {
  try {
    const session = await stripe().checkout.sessions.retrieve(sessionId, { expand: ["total_details.breakdown.discounts.discount.promotion_code"] });
    for (const d of session.total_details?.breakdown?.discounts ?? []) {
      const pc = d.discount.promotion_code;
      const code = typeof pc === "string" ? null : pc?.code;
      if (!code?.startsWith("GIFT-")) continue;
      const found = await getGiftCardByCode(code);
      // Exactly once, even if Stripe sends the payment event twice.
      const card = found && (await claimGiftCard(found.id, "active", "redeemed"));
      if (!card) continue;
      const used = d.amount / 100;
      await updateGiftCard(card.id, { redeemedOrderId: orderId });
      const left = Math.round((card.amount - used) * 100) / 100;
      if (left >= 1) {
        const rest = await activate({
          id: `gc_${nanoid(12)}`,
          status: "pending_payment",
          amount: left,
          currency: card.currency,
          region: card.region,
          buyerEmail: email,
          fromName: card.fromName,
          recipientName: card.recipientName,
          message: "",
          parentId: card.id,
          createdAt: new Date().toISOString(),
        });
        await sendGiftCardEmail(rest, "balance");
      }
    }
  } catch (e) {
    await logError("gift.settle", e, { orderId });
  }
}

/** Cards to send straight to the recipient, on the chosen day (from 8am UK time). */
export async function sendDueGiftCards() {
  const ukDate = new Intl.DateTimeFormat("en-CA", { timeZone: "Europe/London", year: "numeric", month: "2-digit", day: "2-digit" }).format(new Date());
  const ukHour = Number(new Intl.DateTimeFormat("en-GB", { timeZone: "Europe/London", hour: "2-digit", hour12: false }).format(new Date()));
  for (const g of await listGiftCardsToSend()) {
    const due = !g.sendOn || g.sendOn < ukDate || (g.sendOn === ukDate && ukHour >= 8);
    if (!due) continue;
    await updateGiftCard(g.id, { sentToRecipientAt: new Date().toISOString() }); // first, so never twice
    try {
      await sendGiftCardEmail((await getGiftCard(g.id))!, "recipient");
    } catch (e) {
      await updateGiftCard(g.id, { sentToRecipientAt: undefined });
      await logError("gift.send", e, { giftCardId: g.id });
    }
  }
}
