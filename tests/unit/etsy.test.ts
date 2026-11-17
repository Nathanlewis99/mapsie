import { describe, expect, it } from "vitest";
import { etsyToken, etsyTokenValid, matchPrint, samePostcode } from "../../src/lib/server/etsy";
import { ETSY_FINISHES, ETSY_VARIATIONS } from "../../src/lib/etsyOptions";

describe("Etsy: what was bought", () => {
  it("reads our SKUs, old and new", () => {
    expect(matchPrint("MAPSIE-A3-NONE")).toMatchObject({ productId: "a3", frame: "none", paper: "ema", mount: "none", matched: true });
    expect(matchPrint("MAPSIE-A3-HGE")).toMatchObject({ productId: "a3", frame: "none", paper: "hge", matched: true });
    expect(matchPrint("mapsie-50x70-oak")).toMatchObject({ productId: "50x70", frame: "oak", mount: "none", matched: true });
    expect(matchPrint("MAPSIE-A2-BLACK-MOUNT")).toMatchObject({ productId: "a2", frame: "black", paper: "ema", mount: "white", matched: true });
    expect(matchPrint("MAPSIE-A1-DIGITAL")).toMatchObject({ productId: "a1", format: "digital", matched: true });
    expect(ETSY_VARIATIONS.every((v) => matchPrint(v.sku).matched)).toBe(true);
  });
  it("uses the website's prices, and only valid pairings", () => {
    const a3 = (code: string) => ETSY_VARIATIONS.find((v) => v.sku === `MAPSIE-A3-${code}`)!.price;
    expect([a3("EMA"), a3("HGE"), a3("BLACK"), a3("BLACK-MOUNT"), a3("DIGITAL")]).toEqual([44, 59, 79, 86, 19]);
    // Specialist papers are never framed; framed prints are matte art.
    expect(ETSY_FINISHES.filter((f) => f.frame !== "none").every((f) => f.paper === "ema")).toBe(true);
    expect(Math.max(...ETSY_FINISHES.map((f) => f.label.length))).toBeLessThanOrEqual(20);
  });
  it("falls back to the variation names", () => {
    expect(matchPrint(null, [{ formatted_name: "Size", formatted_value: "A2" }, { formatted_name: "Finish", formatted_value: "Black + mount" }])).toMatchObject({ productId: "a2", frame: "black", mount: "white", matched: true });
    expect(matchPrint("", [{ formatted_name: "Size", formatted_value: "50 × 70 cm" }, { formatted_name: "Finish", formatted_value: "Unframed: Cotton rag" }])).toMatchObject({ productId: "50x70", frame: "none", paper: "hpr", matched: true });
    expect(matchPrint("", [{ formatted_name: "Size", formatted_value: "A4" }, { formatted_name: "Finish", formatted_value: "Digital file" }])).toMatchObject({ format: "digital", matched: true });
  });
  it("says when it had to guess", () => {
    expect(matchPrint("SOMETHING-ELSE", [{ formatted_name: "Colour", formatted_value: "Blue" }])).toMatchObject({ productId: "a3", frame: "none", matched: false });
  });
});

describe("Etsy: buyer links", () => {
  it("tokens are per order and checked", () => {
    const t = etsyToken("ord_etsy_abc");
    expect(etsyTokenValid("ord_etsy_abc", t)).toBe(true);
    expect(etsyTokenValid("ord_etsy_abd", t)).toBe(false);
    expect(etsyTokenValid("ord_etsy_abc", undefined)).toBe(false);
    expect(etsyTokenValid("ord_etsy_abc", t.slice(0, -1) + (t.endsWith("a") ? "b" : "a"))).toBe(false);
  });
  it("compares postcodes loosely", () => {
    expect(samePostcode("SW1A 1AA", "sw1a1aa")).toBe(true);
    expect(samePostcode("90210", " 90210 ")).toBe(true);
    expect(samePostcode("SW1A 1AA", "SW1A 1AB")).toBe(false);
  });
});

describe("Etsy: switching to a different print", async () => {
  const { importReceipt, requestSwap, swapCode } = await import("../../src/lib/server/etsy");
  const { getOrder, listOrdersByEtsyReceipt } = await import("../../src/lib/server/db");
  const receipt = (id: number, sku: string, name = "Ada Lovelace", zip = "SW1A 1AA", personal = "") => ({
    receipt_id: id, name, first_line: "1 Road", city: "London", zip, country_iso: "GB", is_paid: true, created_timestamp: Math.floor(Date.now() / 1000),
    transactions: [{ transaction_id: id, quantity: 1, sku, price: { amount: 4400, divisor: 100, currency_code: "GBP" },
      variations: personal ? [{ formatted_name: "Personalisation", formatted_value: personal }] : [] }],
  });

  it("links the new order by its code, carries the design over and asks for a refund", async () => {
    await importReceipt(receipt(1001, "MAPSIE-A3-EMA"));
    const [old] = await listOrdersByEtsyReceipt("1001");
    const code = await requestSwap(old.id, { productId: "a2", frame: "black", paper: "ema", mount: "white" }, "draft123");
    expect(code).toBe(swapCode(old.id));
    expect(code).toMatch(/^MPS-[0-9A-F]{6}$/);
    // A different name and postcode, so only the code can match it.
    await importReceipt(receipt(1002, "MAPSIE-A2-BLACK-MOUNT", "A Lovelace", "E1 6AN", `my code is ${code!.toLowerCase()}`));
    const [fresh] = await listOrdersByEtsyReceipt("1002");
    expect(fresh.etsy).toMatchObject({ replaces: old.id, draftDesignId: "draft123" });
    expect(fresh.print).toMatchObject({ productId: "a2", frame: "black", mount: "white" });
    const after = await getOrder(old.id);
    expect(after?.status).toBe("cancelled");
    expect(after?.etsy).toMatchObject({ replacedBy: fresh.id, refundDue: { amount: 44, currency: "gbp" } });
  });

  it("matches by name and postcode when the code is missing, and leaves other orders alone", async () => {
    await importReceipt(receipt(2001, "MAPSIE-A4-EMA", "Grace Hopper", "NW1 2DB"));
    const [old] = await listOrdersByEtsyReceipt("2001");
    await requestSwap(old.id, { productId: "a3", frame: "none", paper: "ema", mount: "none" });
    await importReceipt(receipt(2002, "MAPSIE-A3-EMA", "Someone Else", "NW1 2DB"));
    expect((await getOrder(old.id))?.status).toBe("awaiting_design");
    await importReceipt(receipt(2003, "MAPSIE-A3-EMA", "grace hopper", "nw12db"));
    expect((await getOrder(old.id))?.etsy?.replacedBy).toBe((await listOrdersByEtsyReceipt("2003"))[0].id);
  });

  it("a plain repeat order from someone who never asked to switch isn't linked", async () => {
    await importReceipt(receipt(3001, "MAPSIE-A3-EMA", "Alan Turing", "M1 1AA"));
    await importReceipt(receipt(3002, "MAPSIE-A3-EMA", "Alan Turing", "M1 1AA"));
    expect((await listOrdersByEtsyReceipt("3001"))[0].status).toBe("awaiting_design");
    expect((await listOrdersByEtsyReceipt("3002"))[0].etsy?.replaces).toBeUndefined();
  });
});

describe("Etsy: listing link and buyer email", async () => {
  const { etsyListingUrl, setEtsyListingUrl, importReceipt } = await import("../../src/lib/server/etsy");
  const { listOrdersByEtsyReceipt } = await import("../../src/lib/server/db");
  it("keeps a clean listing link and refuses other sites", async () => {
    await setEtsyListingUrl("https://www.etsy.com/uk/listing/123456789/custom-travel-map?ref=shop_home&pro=1");
    expect(await etsyListingUrl()).toBe("https://www.etsy.com/uk/listing/123456789/custom-travel-map");
    await expect(setEtsyListingUrl("https://evil.example/listing/1")).rejects.toThrow();
  });
  it("takes the buyer's email from the personalisation when Etsy doesn't share it", async () => {
    await importReceipt({ receipt_id: 4001, name: "Mary Seacole", first_line: "1 Road", city: "Leeds", zip: "LS1 1AA", country_iso: "GB", is_paid: true, created_timestamp: 1,
      transactions: [{ transaction_id: 4001, quantity: 1, sku: "MAPSIE-A4-EMA", variations: [{ formatted_name: "Personalisation", formatted_value: "mary@Example.com thanks!" }] }] });
    expect((await listOrdersByEtsyReceipt("4001"))[0].email).toBe("mary@example.com");
  });
});
