import { describe, expect, it } from "vitest";
import { getOrder, reviewSummary, saveOrder, saveReview, setReviewStatus } from "../../src/lib/server/db";
import { reviewDueAt, reviewToken, reviewTokenValid, sendReviewRequests } from "../../src/lib/server/reviews";

const DAY = 24 * 3600_000;
const ago = (d: number) => new Date(Date.now() - d * DAY).toISOString();
const order = (id: string, extra: object) => ({ id, designId: "d", email: `${id}@example.com`, shipping: "standard", region: "GB", currency: "gbp", total: 44, createdAt: ago(20), ...extra }) as never;

describe("reviews", () => {
  it("asks a few days after delivery", () => {
    expect(reviewDueAt({ region: "GB", shippedAt: ago(0) } as never)).toBeGreaterThan(Date.now() + 5 * DAY);
    expect(reviewDueAt({ digital: true, paidAt: ago(0) } as never)).toBeLessThan(Date.now() + 4 * DAY);
    expect(reviewDueAt({ region: "GB" } as never)).toBeNull();
  });
  it("sends each request once, only when due", async () => {
    await saveOrder(order("ord_due", { status: "shipped", shippedAt: ago(7) }));
    await saveOrder(order("ord_early", { status: "shipped", shippedAt: ago(1) }));
    await saveOrder(order("ord_old", { status: "shipped", shippedAt: ago(60) }));
    await sendReviewRequests();
    await sendReviewRequests();
    expect((await getOrder("ord_due"))?.emailsSent).toEqual(["review-request"]);
    expect((await getOrder("ord_early"))?.emailsSent ?? []).toEqual([]);
    expect((await getOrder("ord_old"))?.emailsSent ?? []).toEqual([]);
  });
  it("signs links and only counts approved reviews", async () => {
    expect(reviewTokenValid("ord_due", reviewToken("ord_due"))).toBe(true);
    expect(reviewTokenValid("ord_x", reviewToken("ord_due"))).toBe(false);
    await saveReview({ id: "rv1", orderId: "ord_due", status: "pending", rating: 5, text: "Love it", name: "Sam", publish: true, source: "mapsie", createdAt: ago(0) });
    expect((await reviewSummary()).count).toBe(0);
    await setReviewStatus("rv1", "approved");
    expect(await reviewSummary()).toEqual({ count: 1, average: 5 });
  });
});
