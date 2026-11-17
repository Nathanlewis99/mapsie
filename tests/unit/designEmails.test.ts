import { describe, expect, it } from "vitest";
import { addDesignEmail, countDesignEmails, isOptedOut, listDueReminders, markReminded, optOut, orderedSince, saveOrder } from "../../src/lib/server/db";
import { unsubscribeToken, unsubscribeTokenValid } from "../../src/lib/server/email";

const past = new Date(Date.now() - 3600_000).toISOString();
const future = new Date(Date.now() + 3600_000).toISOString();

describe("design emails and reminders", () => {
  it("only lists reminders people asked for, once", async () => {
    const yes = await addDesignEmail("Ada@Example.com", "d1", true);
    await addDesignEmail("bob@example.com", "d2", false);
    const due = await listDueReminders(past, future);
    expect(due.map((r) => r.email)).toEqual(["ada@example.com"]);
    await markReminded(yes.id);
    expect(await listDueReminders(past, future)).toEqual([]);
    expect(await countDesignEmails("ADA@example.com", past)).toBe(1);
  });
  it("knows who unsubscribed and who has ordered since", async () => {
    expect(await isOptedOut("c@example.com")).toBe(false);
    await optOut("C@example.com");
    expect(await isOptedOut("c@example.com")).toBe(true);
    await saveOrder({ id: "ord_t1", designId: "d1", email: "D@example.com", shipping: "standard", region: "GB", currency: "gbp", total: 44, status: "paid", createdAt: new Date().toISOString() } as never);
    expect(await orderedSince("d@example.com", past)).toBe(true);
    expect(await orderedSince("d@example.com", future)).toBe(false);
  });
  it("signs unsubscribe links per address", () => {
    expect(unsubscribeTokenValid("Ada@example.com", unsubscribeToken("ada@example.com"))).toBe(true);
    expect(unsubscribeTokenValid("eve@example.com", unsubscribeToken("ada@example.com"))).toBe(false);
  });
});
