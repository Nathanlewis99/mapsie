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
