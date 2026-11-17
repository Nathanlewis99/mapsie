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
