// Live check of the gift card Stripe path, run as a Render one-off job:
//   npx -y tsx@4.20.3 scripts/gift-selftest.ts
// Creates a £1 test card (coupon + single-use code), checks it in Stripe, then
// deactivates the code and deletes the coupon, so nothing usable is left behind.
import Stripe from "stripe";
import { nanoid } from "nanoid";
import { getGiftCard, saveGiftCard, updateGiftCard } from "../src/lib/server/db";

(async () => {
  const id = `gc_selftest_${nanoid(6)}`;
  await saveGiftCard({ id, status: "pending_payment", amount: 1, currency: "gbp", region: "GB", buyerEmail: "admin@mapsie.shop", fromName: "Self-test", recipientName: "Self-test", message: "", createdAt: new Date().toISOString() });
  // issueGiftCard emails the buyer: point it at our own inbox, then clean up.
  const { issueGiftCard } = await import("../src/lib/server/giftcards");
  await issueGiftCard(id, "selftest");
  const g = await getGiftCard(id);
  const s = new Stripe(process.env.STRIPE_SECRET_KEY!);
  const promo = g?.promoId ? await s.promotionCodes.retrieve(g.promoId) : null;
  console.log("SELFTEST", JSON.stringify({ status: g?.status, code: g?.code, promoActive: promo?.active, maxRedemptions: promo?.max_redemptions, expires: g?.expiresAt?.slice(0, 10), couponOff: g?.couponId ? (await s.coupons.retrieve(g.couponId)).amount_off : null }));
  if (g?.promoId) await s.promotionCodes.update(g.promoId, { active: false });
  if (g?.couponId) await s.coupons.del(g.couponId);
  await updateGiftCard(id, { status: "expired" });
  console.log("SELFTEST cleaned up");
  process.exit(0);
})().catch((e) => {
  console.log("SELFTEST ERROR", e?.message);
  process.exit(1);
});
