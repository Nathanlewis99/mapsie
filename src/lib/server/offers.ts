// Personal "Save your map" codes: SAVE_OFFER.pct% off, one use, expiring an hour after they're issued.
import Stripe from "stripe";
import { createHash, randomInt } from "node:crypto";
import { getKv, putKv } from "./db";
import { SAVE_OFFER, BLACK_FRIDAY } from "../offers";

const stripe = () => new Stripe(process.env.STRIPE_SECRET_KEY!);
const COUPON = `mapsie-save${SAVE_OFFER.pct}`;
const ALPHABET = "ABCDEFGHJKMNPQRSTUVWXYZ23456789";
const block = () => Array.from({ length: 5 }, () => ALPHABET[randomInt(ALPHABET.length)]).join("");

async function ensureCoupon(id: string, pct: number, name: string) {
  const s = stripe();
  try {
    return await s.coupons.retrieve(id);
  } catch {
    return s.coupons.create({ id, percent_off: pct, duration: "once", name });
  }
}

/** One offer per email address per week, so it can't be farmed. Returns null if they've had one. */
export async function issueSaveOffer(email: string): Promise<{ code: string; pct: number; expiresAt: string } | null> {
  const key = `offer:${createHash("sha256").update(email.trim().toLowerCase()).digest("hex").slice(0, 24)}`;
  const prev = await getKv<{ at: string }>(key);
  if (prev && Date.now() - Date.parse(prev.value.at) < 7 * 24 * 3600_000) return null;
  await ensureCoupon(COUPON, SAVE_OFFER.pct, `Save your map: ${SAVE_OFFER.pct}% off`);
  const expires = Math.floor(Date.now() / 1000) + SAVE_OFFER.minutes * 60;
  const promo = await stripe().promotionCodes.create({
    promotion: { type: "coupon", coupon: COUPON },
    code: `SAVE${SAVE_OFFER.pct}-${block()}`,
    max_redemptions: 1,
    expires_at: expires,
    metadata: { kind: "save-offer" },
  });
  await putKv(key, { at: new Date().toISOString() });
  return { code: promo.code, pct: SAVE_OFFER.pct, expiresAt: new Date(expires * 1000).toISOString() };
}

/** A code the browser asks us to apply at checkout: only if it's live and unexpired. */
export async function liveCode(code: string): Promise<string | null> {
  if (!/^[A-Z0-9-]{4,30}$/.test(code)) return null;
  const r = await stripe().promotionCodes.list({ code, active: true, limit: 1 });
  const p = r.data[0];
  if (!p || (p.expires_at && p.expires_at * 1000 < Date.now()) || (p.max_redemptions && p.times_redeemed >= p.max_redemptions)) return null;
  return p.id;
}

/** Create the Black Friday code (idempotent). Run once: see scripts/offers/black-friday.ts. */
export async function ensureBlackFriday() {
  const s = stripe();
  await ensureCoupon("mapsie-blackfriday10", BLACK_FRIDAY.pct, `Black Friday ${BLACK_FRIDAY.pct}% off`);
  const existing = await s.promotionCodes.list({ code: BLACK_FRIDAY.code, limit: 1 });
  if (existing.data[0]) return existing.data[0];
  return s.promotionCodes.create({
    promotion: { type: "coupon", coupon: "mapsie-blackfriday10" },
    code: BLACK_FRIDAY.code,
    expires_at: Math.floor(Date.parse(BLACK_FRIDAY.ends) / 1000),
    metadata: { kind: "black-friday" },
  });
}
