import { describe, expect, it } from "vitest";
import { giftToken, giftTokenValid, newGiftCode } from "../../src/lib/server/giftcards";
import { claimGiftCard, getGiftCardByCode, listGiftCardsToSend, saveGiftCard } from "../../src/lib/server/db";
import { giftAmounts } from "../../src/lib/giftcards";

describe("gift cards", () => {
  it("makes readable, unambiguous codes", () => {
    for (let i = 0; i < 50; i++) expect(newGiftCode()).toMatch(/^GIFT-[A-HJKMNP-Z2-9]{4}-[A-HJKMNP-Z2-9]{4}$/);
  });
  it("signs card links", () => {
    expect(giftTokenValid("gc_1", giftToken("gc_1"))).toBe(true);
    expect(giftTokenValid("gc_2", giftToken("gc_1"))).toBe(false);
  });
  it("offers amounts that match what they buy", () => {
    expect(giftAmounts("GB").map((a) => a.amount)).toEqual([19, 44, 89, 125]);
  });
  it("is claimed once, found by code, and only sent once it has a code", async () => {
    const base = { id: "gc_t", status: "pending_payment" as const, amount: 50, currency: "gbp", region: "GB" as const, buyerEmail: "a@b.com", fromName: "A", recipientName: "B", message: "", recipientEmail: "b@c.com", createdAt: new Date().toISOString() };
    await saveGiftCard(base);
    expect(await claimGiftCard("gc_t", "pending_payment", "active")).toBeTruthy();
    expect(await claimGiftCard("gc_t", "pending_payment", "active")).toBeNull();
    expect(await listGiftCardsToSend()).toEqual([]); // active but no code yet
    await saveGiftCard({ ...base, status: "active", code: "GIFT-ABCD-EFGH" });
    expect((await getGiftCardByCode("gift-abcd-efgh"))?.id).toBe("gc_t");
    expect((await listGiftCardsToSend()).map((g) => g.id)).toEqual(["gc_t"]);
  });
});

describe("gift card balance after an order", () => {
  it("marks the card used and issues the rest as a new code", async () => {
    const { vi } = await import("vitest");
    const calls: { expand?: string[] }[] = [];
    const created: { amount_off: number }[] = [];
    vi.resetModules();
    vi.doMock("stripe", () => ({
      default: class {
        checkout = {
          sessions: {
            retrieve: async (_id: string, opts: { expand?: string[] }) => {
              calls.push(opts);
              // Stripe refuses expansions deeper than 4 levels.
              if (opts.expand?.some((e) => e.split(".").length > 4)) throw new Error("You cannot expand more than 4 levels of a property.");
              return { total_details: { breakdown: { discounts: [{ amount: 1900, discount: { promotion_code: "promo_x" } }] } } };
            },
          },
        };
        promotionCodes = {
          retrieve: async () => ({ code: "GIFT-BALA-NCE2" }),
          create: async (p: { code: string }) => ({ id: "promo_new", code: p.code }),
        };
        coupons = { create: async (p: { amount_off: number }) => (created.push(p), { id: "co_new" }) };
      },
    }));
    vi.doMock("../../src/lib/server/email", () => ({ sendGiftCardEmail: async () => {} }));
    const db = await import("../../src/lib/server/db");
    await db.saveGiftCard({ id: "gc_bal", status: "active", code: "GIFT-BALA-NCE2", amount: 25, currency: "gbp", region: "GB", buyerEmail: "a@b.com", fromName: "A", recipientName: "B", message: "", createdAt: new Date().toISOString() });
    const { settleGiftCards } = await import("../../src/lib/server/giftcards");
    await settleGiftCards("cs_x", "ord_x", "buyer@b.com");
    expect(calls[0].expand?.every((e) => e.split(".").length <= 4)).toBe(true);
    expect((await db.getGiftCard("gc_bal"))?.status).toBe("redeemed");
    expect(created).toEqual([expect.objectContaining({ amount_off: 600, currency: "gbp" })]);
    vi.doUnmock("stripe");
    vi.doUnmock("../../src/lib/server/email");
  });
});
