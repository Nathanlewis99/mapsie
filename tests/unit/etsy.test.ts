import { describe, expect, it } from "vitest";
import { ALL_SKUS, etsySku, etsyToken, etsyTokenValid, matchPrint, samePostcode } from "../../src/lib/server/etsy";

describe("Etsy: what was bought", () => {
  it("reads our SKUs", () => {
    expect(matchPrint("MAPSIE-A3-NONE")).toEqual({ productId: "a3", frame: "none", matched: true });
    expect(matchPrint("mapsie-50x70-oak")).toEqual({ productId: "50x70", frame: "oak", matched: true });
    expect(matchPrint(etsySku("a1", "darkgrey"))).toEqual({ productId: "a1", frame: "darkgrey", matched: true });
    expect(ALL_SKUS.every((s) => matchPrint(s.sku).matched)).toBe(true);
  });
  it("falls back to the variation names", () => {
    expect(matchPrint(null, [{ formatted_name: "Size", formatted_value: "A2 (42 x 59.4 cm)" }, { formatted_name: "Frame", formatted_value: "Black frame" }])).toEqual({ productId: "a2", frame: "black", matched: true });
    expect(matchPrint("", [{ formatted_name: "Size", formatted_value: "50 × 70 cm" }, { formatted_name: "Frame", formatted_value: "Unframed" }])).toEqual({ productId: "50x70", frame: "none", matched: true });
    expect(matchPrint("", [{ formatted_name: "Size", formatted_value: "A4" }, { formatted_name: "Frame", formatted_value: "Natural oak" }])).toMatchObject({ frame: "oak", matched: true });
  });
  it("says when it had to guess", () => {
    expect(matchPrint("SOMETHING-ELSE", [{ formatted_name: "Colour", formatted_value: "Blue" }])).toEqual({ productId: "a3", frame: "none", matched: false });
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
