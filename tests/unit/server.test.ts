import { describe, expect, it } from "vitest";
import { callbackToken, callbackTokenValid, printToken, printTokenValid } from "@/lib/server/printToken";
import { fingerprint } from "@/lib/server/log";
import * as db from "@/lib/server/db";

describe("tokens", () => {
  it("only accepts tokens we signed", () => {
    expect(printTokenValid("abc", printToken("abc"))).toBe(true);
    expect(printTokenValid("abc", printToken("abd"))).toBe(false);
    expect(printTokenValid("abc", undefined)).toBe(false);
    expect(callbackTokenValid("ord_1", callbackToken("ord_1"))).toBe(true);
    expect(callbackTokenValid("ord_1", "nope")).toBe(false);
  });
});

it("groups errors that differ only by ids and numbers", () => {
  expect(fingerprint("server", "order.render", "order ord_abc123 failed after 3 tries")).toBe(fingerprint("server", "order.render", "order ord_zz9 failed after 7 tries"));
  expect(fingerprint("server", "order.render", "a")).not.toBe(fingerprint("server", "order.print", "a"));
});

const order = (id: string): db.Order => ({ id, designId: "d1", email: "A@Example.com", shipping: "standard", region: "GB", currency: "gbp", total: 44, status: "paid", createdAt: new Date().toISOString() });

describe("database", () => {
  it("saves and updates orders", async () => {
    await db.saveOrder(order("ord_1"));
    await db.updateOrder("ord_1", { renderFile: "x.png" });
    expect(await db.getOrder("ord_1")).toMatchObject({ status: "paid", renderFile: "x.png" });
  });
  it("lets exactly one worker claim a job", async () => {
    await db.saveOrder(order("ord_2"));
    const [a, b] = await Promise.all([db.claimOrder("ord_2", "paid", "rendering"), db.claimOrder("ord_2", "paid", "rendering")]);
    expect([a, b].filter(Boolean)).toHaveLength(1);
    expect((await db.getOrder("ord_2"))?.status).toBe("rendering");
  });
  it("finds a customer's orders by account or (case-insensitive) email", async () => {
    const u = await db.upsertGoogleUser({ sub: "g1", email: "a@example.com", name: "A" });
    const mine = await db.listOrdersForUser(u);
    expect(mine.map((o) => o.id)).toContain("ord_1");
  });
  it("keeps saved designs per user", async () => {
    const u = await db.upsertGoogleUser({ sub: "g2", email: "b@example.com" });
    const id = await db.upsertSavedDesign(u.id, { id: "d", title: "Trip" } as never);
    expect((await db.listSavedDesigns(u.id)).map((s) => s.id)).toEqual([id]);
    await db.deleteSavedDesign(u.id, id);
    expect(await db.listSavedDesigns(u.id)).toEqual([]);
  });
  it("counts funnel events per distinct visit", async () => {
    const since = new Date(Date.now() - 1000).toISOString();
    await db.recordEvent("v1", "visit");
    await db.recordEvent("v1", "editor_open");
    await db.recordEvent("v2", "visit");
    expect(await db.eventCounts(since)).toMatchObject({ visit: 2, editor_open: 1 });
  });
  it("groups repeated errors", async () => {
    for (let i = 0; i < 3; i++) await db.recordError({ fingerprint: "f1", source: "server", scope: "t", message: "boom" });
    expect((await db.listErrors()).find((e) => e.fingerprint === "f1")?.count).toBe(3);
    await db.resolveError("f1");
    expect((await db.listErrors()).find((e) => e.fingerprint === "f1")).toBeUndefined();
  });
});

describe("order emails", () => {
  it("sends each email once, even if asked twice", async () => {
    const { sendOrderEmail } = await import("@/lib/server/email");
    const logs: string[] = [];
    const orig = console.log;
    console.log = (m: string) => void logs.push(String(m));
    try {
      await db.saveDesign({ id: "d-mail", title: "Our Trip", productId: "a3", orientation: "portrait", frame: "none" } as never);
      await db.saveOrder({ ...order("ord_mail"), designId: "d-mail", holdUntil: new Date(Date.now() + 3600_000).toISOString(), address: { name: "Sam Smith", line1: "1", city: "L", postcode: "N1", country: "GB" } });
      await sendOrderEmail("ord_mail", "confirmed");
      await sendOrderEmail("ord_mail", "confirmed");
    } finally {
      console.log = orig;
    }
    const sent = logs.filter((l) => l.includes("Your Mapsie order ord_mail"));
    expect(sent).toHaveLength(1);
    expect(sent[0]).toContain("Hi Sam");
    expect(sent[0]).toContain("cancel for a full refund until");
    expect((await db.getOrder("ord_mail"))?.emailsSent).toEqual(["confirmed"]);
  });
});
