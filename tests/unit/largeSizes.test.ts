import { describe, expect, it } from "vitest";
import { allowedOptions, itemPrice, printDpi, printPixels, prodigiItem, PRODUCTS } from "@/lib/products";

// Prodigi cost (print + standard delivery) from their price sheets, Nov 2026, in each region's currency.
const COST: Record<string, { GB: number; US: number; AU: number }> = {
  "60x90": { GB: 24, US: 39, AU: 52 },
  "70x100": { GB: 26, US: 43, AU: 62 },
  a0: { GB: 32, US: 52, AU: 69 },
  "80x120": { GB: 32, US: 56, AU: 69 },
  "90x120": { GB: 37, US: 54, AU: 76 },
  "100x150": { GB: 47, US: 68, AU: 79 },
};

describe("large sizes", () => {
  it("keep a healthy margin on matte paper in every region", () => {
    for (const [id, cost] of Object.entries(COST)) {
      for (const r of ["GB", "US", "AU"] as const) {
        const price = itemPrice({ productId: id, frame: "none", paper: "ema" } as never, r);
        expect(1 - cost[r] / price, `${id} ${r}`).toBeGreaterThan(0.62);
      }
    }
  });
  it("can't be framed (except 60 × 90) or printed on papers Prodigi doesn't offer at that size", () => {
    expect(allowedOptions({ productId: "a0", frame: "black", paper: "hpr" } as never)).toMatchObject({ frame: "none", paper: "ema" });
    expect(prodigiItem({ productId: "a0", frame: "black" } as never).sku).toBe("GLOBAL-FAP-A0");
    expect(prodigiItem({ productId: "60x90", frame: "black" } as never).sku).toBe("GLOBAL-CFP-24X36");
    expect(itemPrice({ productId: "a0", frame: "black", paper: "ema" } as never, "GB")).toBe(119);
  });
  it("print large posters at a resolution the renderer can handle", () => {
    expect(printDpi("a4")).toBe(300);
    expect(printDpi("a1")).toBe(300);
    expect(printDpi("a0")).toBeGreaterThanOrEqual(150);
    const px = printPixels("100x150", "portrait");
    expect(px.width * px.height).toBeLessThan(75e6);
    expect(PRODUCTS.filter((p) => p.more).length).toBe(6);
  });
});
