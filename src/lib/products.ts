import type { FrameId, GlazeId, MountId, Orientation, PaperId } from "./types";

// ---------------------------------------------------------------- regions
export type RegionId = "GB" | "US" | "AU";

export interface Region {
  id: RegionId;
  label: string;
  flag: string;
  currency: "gbp" | "usd" | "aud";
  symbol: string;
  shipTo: string[]; // ISO-2 countries Stripe should accept
}

export const REGIONS: Region[] = [
  { id: "GB", label: "United Kingdom", flag: "🇬🇧", currency: "gbp", symbol: "£", shipTo: ["GB"] },
  { id: "US", label: "United States", flag: "🇺🇸", currency: "usd", symbol: "$", shipTo: ["US"] },
  { id: "AU", label: "Australia", flag: "🇦🇺", currency: "aud", symbol: "A$", shipTo: ["AU"] },
];

export const getRegion = (id: string | undefined) => REGIONS.find((r) => r.id === id) ?? REGIONS[0];

/** Best guess at the shopper's region from their browser. */
export function guessRegion(): RegionId {
  if (typeof navigator === "undefined") return "GB";
  const tz = Intl.DateTimeFormat().resolvedOptions().timeZone ?? "";
  if (tz.startsWith("Australia")) return "AU";
  if (tz.startsWith("America/") && navigator.language === "en-US") return "US";
  return "GB";
}

export const money = (region: RegionId, amount: number) => {
  const r = getRegion(region);
  return `${r.symbol}${Number.isInteger(amount) ? amount : amount.toFixed(2)}`;
};

// ---------------------------------------------------------------- products
// Prodigi SKUs are built from a product range and a size code, e.g.
// GLOBAL-FAP-A3 (fine art print) or GLOBAL-CFPM-A3 (classic frame with mount).
// /api/admin/prodigi-check verifies every combination against Prodigi's catalogue.
export interface Product {
  id: string;
  label: string;
  widthCm: number; // portrait width
  heightCm: number; // portrait height
  price: Record<RegionId, number>;
  framePrice: Record<RegionId, number>;
  sizeCode: string; // Prodigi size part of the SKU
}

export const PRODUCTS: Product[] = [
  { id: "a4", label: "A4", widthCm: 21, heightCm: 29.7, price: { GB: 34, US: 45, AU: 65 }, framePrice: { GB: 25, US: 35, AU: 49 }, sizeCode: "A4" },
  { id: "a3", label: "A3", widthCm: 29.7, heightCm: 42, price: { GB: 44, US: 59, AU: 85 }, framePrice: { GB: 35, US: 45, AU: 65 }, sizeCode: "A3" },
  { id: "a2", label: "A2", widthCm: 42, heightCm: 59.4, price: { GB: 59, US: 79, AU: 115 }, framePrice: { GB: 55, US: 69, AU: 99 }, sizeCode: "A2" },
  { id: "50x70", label: "50 × 70 cm", widthCm: 50, heightCm: 70, price: { GB: 69, US: 89, AU: 129 }, framePrice: { GB: 65, US: 79, AU: 115 }, sizeCode: "50X70" },
  { id: "a1", label: "A1", widthCm: 59.4, heightCm: 84.1, price: { GB: 84, US: 109, AU: 159 }, framePrice: { GB: 80, US: 99, AU: 145 }, sizeCode: "A1" },
];

/** Prodigi's papers for unframed prints. `extra` is the uplift on the print price. */
export const PAPERS: { id: PaperId; label: string; detail: string; code: string; extra: number }[] = [
  { id: "ema", label: "Matte art", detail: "Enhanced Matte Art, 200gsm. Smooth, no glare, rich colour.", code: "FAP", extra: 0 },
  { id: "hpr", label: "Cotton rag", detail: "Hahnemühle Photo Rag, 308gsm. Soft velvety matte, 100% cotton, museum grade.", code: "HPR", extra: 0.35 },
  { id: "hge", label: "Textured etching", detail: "Hahnemühle German Etching, 310gsm. A fine paper texture, like an art print.", code: "HGE", extra: 0.35 },
  { id: "lpp", label: "Lustre photo", detail: "Lustre photo paper, 240gsm. A gentle satin sheen and punchy colour.", code: "LPP", extra: 0.1 },
];

export const FRAMES: { id: FrameId; label: string; color: string; finish?: string; prodigiColor?: string }[] = [
  { id: "none", label: "No frame", color: "transparent" },
  { id: "black", label: "Black", color: "#1b1b1b", prodigiColor: "black" },
  { id: "white", label: "White", color: "#f4f4f2", prodigiColor: "white" },
  { id: "oak", label: "Natural", color: "#c49a6c", finish: "linear-gradient(135deg, #d4ab7b, #b98a59 40%, #c99e6d 70%, #a97b4c)", prodigiColor: "natural" },
  { id: "brown", label: "Brown", color: "#5a3b26", finish: "linear-gradient(135deg, #6b4630, #4e3220 45%, #5f3e29 75%, #43291a)", prodigiColor: "brown" },
  { id: "darkgrey", label: "Dark grey", color: "#4a4d52", prodigiColor: "dark grey" },
  { id: "lightgrey", label: "Light grey", color: "#b9bcbf", prodigiColor: "light grey" },
  { id: "gold", label: "Antique gold", color: "#b8954f", finish: "linear-gradient(135deg, #d9bd78, #a8823f 35%, #cfae66 60%, #8f6c30)", prodigiColor: "gold" },
  { id: "silver", label: "Antique silver", color: "#a9a9a6", finish: "linear-gradient(135deg, #dcdcd8, #9a9a96 35%, #c9c9c5 60%, #85857f)", prodigiColor: "silver" },
];

export const MOUNTS: { id: MountId; label: string; color: string; prodigi?: string }[] = [
  { id: "none", label: "No mount", color: "transparent" },
  { id: "white", label: "Snow white", color: "#fbfbf9", prodigi: "Snow white" },
  { id: "offwhite", label: "Off-white", color: "#f1ebdd", prodigi: "Off-white" },
  { id: "black", label: "Black", color: "#1d1d1d", prodigi: "Black" },
];
const MOUNT_EXTRA = 0.2; // of the frame price

export const GLAZES: { id: GlazeId; label: string; detail: string; extra: number; prodigi: string }[] = [
  { id: "perspex", label: "Perspex", detail: "Light and shatterproof. Our standard.", extra: 0, prodigi: "Perspex" },
  { id: "glass", label: "Float glass", detail: "Crystal clear glass.", extra: 0.2, prodigi: "Float glass" },
  { id: "motheye", label: "Anti-reflective", detail: "Moth-eye glazing: almost no reflections, great opposite windows.", extra: 0.6, prodigi: "Motheye" },
];

export interface PrintOptions {
  productId: string;
  frame: FrameId;
  paper?: PaperId;
  mount?: MountId;
  glaze?: GlazeId;
}

/** Each part of the price, so checkout can show the breakdown. */
export function priceLines(o: PrintOptions, region: RegionId) {
  const p = getProduct(o.productId);
  const framed = o.frame !== "none";
  const lines: { label: string; amount: number }[] = [];
  const paper = PAPERS.find((x) => x.id === (o.paper ?? "ema")) ?? PAPERS[0];
  const print = p.price[region];
  lines.push({ label: `${p.label} print`, amount: print });
  if (!framed && paper.extra) lines.push({ label: `${paper.label} paper`, amount: Math.round(print * paper.extra) });
  if (framed) {
    const f = FRAMES.find((x) => x.id === o.frame)!;
    const fp = p.framePrice[region];
    lines.push({ label: `${f.label} frame`, amount: fp });
    if (o.mount && o.mount !== "none") lines.push({ label: `${MOUNTS.find((m) => m.id === o.mount)!.label} mount`, amount: Math.round(fp * MOUNT_EXTRA) });
    const g = GLAZES.find((x) => x.id === (o.glaze ?? "perspex")) ?? GLAZES[0];
    if (g.extra) lines.push({ label: `${g.label} glazing`, amount: Math.round(fp * g.extra) });
  }
  return lines;
}

export function itemPrice(o: PrintOptions, region: RegionId) {
  return priceLines(o, region).reduce((a, l) => a + l.amount, 0);
}

/** The Prodigi SKU and attributes for these options. */
export function prodigiItem(o: PrintOptions) {
  const p = getProduct(o.productId);
  if (o.frame === "none") {
    const paper = PAPERS.find((x) => x.id === (o.paper ?? "ema")) ?? PAPERS[0];
    return { sku: `GLOBAL-${paper.code}-${p.sizeCode}`, attributes: {} as Record<string, string> };
  }
  const frame = FRAMES.find((f) => f.id === o.frame)!;
  const mount = MOUNTS.find((m) => m.id === (o.mount ?? "none"));
  const glaze = GLAZES.find((g) => g.id === (o.glaze ?? "perspex")) ?? GLAZES[0];
  const withMount = !!mount && mount.id !== "none";
  return {
    sku: `GLOBAL-${withMount ? "CFPM" : "CFP"}-${p.sizeCode}`,
    attributes: { color: frame.prodigiColor!, ...(withMount ? { mountColor: mount.prodigi! } : {}), glaze: glaze.prodigi } as Record<string, string>,
  };
}

/** One-line description, e.g. "A3 portrait, cotton rag paper" or "A3, black frame, white mount". */
export function describeOptions(o: PrintOptions & { orientation?: string }) {
  const p = getProduct(o.productId);
  const parts = [`${p.label}${o.orientation ? ` ${o.orientation}` : ""}`];
  if (o.frame === "none") parts.push(`${(PAPERS.find((x) => x.id === (o.paper ?? "ema")) ?? PAPERS[0]).label.toLowerCase()} paper`);
  else {
    parts.push(`${FRAMES.find((f) => f.id === o.frame)!.label.toLowerCase()} frame`);
    if (o.mount && o.mount !== "none") parts.push(`${MOUNTS.find((m) => m.id === o.mount)!.label.toLowerCase()} mount`);
    if (o.glaze && o.glaze !== "perspex") parts.push(GLAZES.find((g) => g.id === o.glaze)!.label.toLowerCase());
  }
  return parts.join(", ");
}

// ---------------------------------------------------------------- shipping
export interface ShippingOption {
  id: "standard" | "express";
  label: string;
  detail: string;
  price: Record<RegionId, number>;
  prodigiMethod: string;
}

export const SHIPPING: ShippingOption[] = [
  { id: "standard", label: "Free delivery", detail: "3–5 working days", price: { GB: 0, US: 0, AU: 0 }, prodigiMethod: "Standard" },
  { id: "express", label: "Express", detail: "1–2 working days", price: { GB: 9.95, US: 14.95, AU: 19.95 }, prodigiMethod: "Express" },
];

export type ShippingId = ShippingOption["id"];

export const PRINT_DPI = 300;

export function getProduct(id: string): Product {
  return PRODUCTS.find((p) => p.id === id) ?? PRODUCTS[1];
}


/** height / width of the poster */
export function posterAspect(productId: string, orientation: Orientation) {
  const p = getProduct(productId);
  return orientation === "portrait" ? p.heightCm / p.widthCm : p.widthCm / p.heightCm;
}

/** Target pixel size for printing at PRINT_DPI. */
export function printPixels(productId: string, orientation: Orientation) {
  const p = getProduct(productId);
  const w = orientation === "portrait" ? p.widthCm : p.heightCm;
  const h = orientation === "portrait" ? p.heightCm : p.widthCm;
  const px = (cm: number) => Math.round((cm / 2.54) * PRINT_DPI);
  return { width: px(w), height: px(h) };
}
