import { describe, expect, it } from "vitest";
import { describeOptions, itemPrice, priceLines, prodigiItem, PRODUCTS, PAPERS, FRAMES } from "@/lib/products";

describe("prices", () => {
  it("adds paper, frame and mount on top of the print", () => {
    expect(itemPrice({ productId: "a3", frame: "none" }, "GB")).toBe(44);
    expect(itemPrice({ productId: "a3", frame: "none", paper: "hpr" }, "GB")).toBe(44 + Math.round(44 * 0.35));
    expect(itemPrice({ productId: "a3", frame: "black" }, "GB")).toBe(44 + 35);
    expect(itemPrice({ productId: "a3", frame: "black", mount: "white" }, "GB")).toBe(44 + 35 + 7);
  });
  it("ignores the paper choice on framed prints", () => {
    expect(itemPrice({ productId: "a2", frame: "oak", paper: "hpr" }, "US")).toBe(itemPrice({ productId: "a2", frame: "oak" }, "US"));
  });
  it("totals match the itemised lines", () => {
    for (const p of PRODUCTS)
      for (const region of ["GB", "US", "AU"] as const) {
        const o = { productId: p.id, frame: "black" as const, mount: "white" as const };
        expect(priceLines(o, region).reduce((a, l) => a + l.amount, 0)).toBe(itemPrice(o, region));
      }
  });
});

describe("Prodigi SKUs", () => {
  it("uses Prodigi's codes for each paper and size", () => {
    expect(prodigiItem({ productId: "a3", frame: "none" }).sku).toBe("GLOBAL-FAP-A3");
    expect(prodigiItem({ productId: "a3", frame: "none", paper: "lpp" }).sku).toBe("GLOBAL-PAP-A3");
    expect(prodigiItem({ productId: "50x70", frame: "none", paper: "hge" }).sku).toBe("GLOBAL-HGE-20X28");
  });
  it("uses classic frames, with a mount when chosen", () => {
    expect(prodigiItem({ productId: "a1", frame: "gold" })).toEqual({ sku: "GLOBAL-CFP-A1", attributes: { color: "gold", glaze: "Perspex" } });
    expect(prodigiItem({ productId: "a4", frame: "darkgrey", mount: "white" }).sku).toBe("GLOBAL-CFPM-A4");
  });
  it("maps every frame to a Prodigi colour", () => {
    for (const f of FRAMES.filter((x) => x.id !== "none")) expect(f.prodigiColor).toBeTruthy();
    expect(PAPERS.map((p) => p.code)).toEqual(["FAP", "HPR", "HGE", "PAP"]);
  });
});

it("describes options for receipts", () => {
  expect(describeOptions({ productId: "a3", frame: "none", paper: "hpr", orientation: "portrait" })).toBe("A3 portrait, cotton rag paper");
  expect(describeOptions({ productId: "a3", frame: "black", mount: "white" })).toBe("A3, black frame, white mount");
});
