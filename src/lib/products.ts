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
  // Links can choose the country (e.g. ads for US searches use ?region=US).
  const asked = typeof location !== "undefined" ? new URLSearchParams(location.search).get("region")?.toUpperCase() : null;
  if (asked && REGIONS.some((r) => r.id === asked)) return asked as RegionId;
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
  /** Large sizes, shown under "More sizes". */
  more?: boolean;
  /** Prodigi doesn't frame it at a sensible cost everywhere: posters only. */
  unframed?: boolean;
  /** Papers Prodigi prints at this size (default: all). */
  papers?: PaperId[];
}

export const PRODUCTS: Product[] = [
  { id: "a4", label: "A4", widthCm: 21, heightCm: 29.7, price: { GB: 34, US: 45, AU: 65 }, framePrice: { GB: 35, US: 65, AU: 49 }, sizeCode: "A4" },
  { id: "a3", label: "A3", widthCm: 29.7, heightCm: 42, price: { GB: 44, US: 59, AU: 85 }, framePrice: { GB: 45, US: 69, AU: 65 }, sizeCode: "A3" },
  { id: "a2", label: "A2", widthCm: 42, heightCm: 59.4, price: { GB: 59, US: 79, AU: 115 }, framePrice: { GB: 55, US: 69, AU: 99 }, sizeCode: "A2" },
  { id: "50x70", label: "50 × 70 cm", widthCm: 50, heightCm: 70, price: { GB: 69, US: 89, AU: 129 }, framePrice: { GB: 65, US: 79, AU: 115 }, sizeCode: "20X28" },
  { id: "a1", label: "A1", widthCm: 59.4, heightCm: 84.1, price: { GB: 84, US: 109, AU: 159 }, framePrice: { GB: 80, US: 99, AU: 145 }, sizeCode: "A1" },
  // Large sizes. Priced from Prodigi's price sheets (print + standard delivery) to keep our usual
  // margins (~70% unframed, ~50% framed); only papers and frames Prodigi makes at a sensible cost.
  { id: "60x90", label: "60 × 90 cm", widthCm: 60, heightCm: 90, price: { GB: 89, US: 129, AU: 169 }, framePrice: { GB: 82, US: 89, AU: 179 }, sizeCode: "24X36", more: true, papers: ["ema", "hge"] },
  { id: "70x100", label: "70 × 100 cm", widthCm: 70, heightCm: 100, price: { GB: 99, US: 139, AU: 199 }, framePrice: { GB: 0, US: 0, AU: 0 }, sizeCode: "28X40", more: true, unframed: true, papers: ["ema", "hge"] },
  { id: "a0", label: "A0", widthCm: 84.1, heightCm: 118.9, price: { GB: 119, US: 169, AU: 229 }, framePrice: { GB: 0, US: 0, AU: 0 }, sizeCode: "A0", more: true, unframed: true, papers: ["ema", "hge"] },
  { id: "80x120", label: "80 × 120 cm", widthCm: 80, heightCm: 120, price: { GB: 129, US: 189, AU: 239 }, framePrice: { GB: 0, US: 0, AU: 0 }, sizeCode: "32X48", more: true, unframed: true, papers: ["ema", "hge"] },
  { id: "90x120", label: "90 × 120 cm", widthCm: 90, heightCm: 120, price: { GB: 139, US: 199, AU: 259 }, framePrice: { GB: 0, US: 0, AU: 0 }, sizeCode: "36X48", more: true, unframed: true, papers: ["ema", "hge"] },
  { id: "100x150", label: "100 × 150 cm", widthCm: 100, heightCm: 150, price: { GB: 169, US: 229, AU: 279 }, framePrice: { GB: 0, US: 0, AU: 0 }, sizeCode: "40X60", more: true, unframed: true, papers: ["ema", "hge"] },
];

/** Prodigi's papers for unframed prints. `extra` is the uplift on the print price. */
export const PAPERS: { id: PaperId; label: string; detail: string; bestFor: string; spec: string; code: string; extra: number }[] = [
  {
    id: "ema",
    label: "Matte art",
    spec: "Enhanced Matte Art · 200gsm · matte",
    detail: "A smooth, bright white art paper with a flat, glare-free finish. Colours are rich and the map's fine lines stay crisp, and it looks good from any angle.",
    bestFor: "Most maps. Our standard and the paper used in our frames.",
    code: "FAP",
    extra: 0,
  },
  {
    id: "hpr",
    label: "Cotton rag",
    spec: "Hahnemühle Photo Rag · 308gsm · 100% cotton · matte",
    detail: "A thick, museum-grade paper made from cotton by Hahnemühle, a German mill since 1584. It has a soft, velvety surface, deep blacks and is acid-free, so it won't yellow for generations.",
    bestFor: "Heirloom gifts and a gallery feel.",
    code: "HPR",
    extra: 0.35,
  },
  {
    id: "hge",
    label: "Textured etching",
    spec: "Hahnemühle German Etching · 310gsm · textured matte",
    detail: "A heavyweight fine art paper with a gentle, visible texture, like a traditional etching or engraving. It gives vintage and hand-drawn styles real character.",
    bestFor: "Vintage, Explorer and Nautical styles.",
    code: "HGE",
    extra: 0.35,
  },
  {
    id: "lpp",
    label: "Lustre photo",
    spec: "Lustre photo paper · 240gsm · satin",
    detail: "A photographic paper with a soft satin sheen between matte and gloss. Colours are punchy and the surface is tough, but it can catch the light opposite a window.",
    bestFor: "Bold, colourful styles and maps with photos.",
    code: "PAP",
    extra: 0.1,
  },
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
  { id: "white", label: "White mount", color: "#fbfbf9", prodigi: "Snow white" },
];
// Prodigi's price sheets list Snow white mounts for the A-size classic frames.
const MOUNT_EXTRA = 0.2; // of the frame price

export const GLAZES: { id: GlazeId; label: string; detail: string; extra: number; prodigi: string }[] = [
  { id: "perspex", label: "Perspex", detail: "Light, clear and shatterproof, so it's safe to post and to hang.", extra: 0, prodigi: "Perspex" },
];
// Prodigi only offers float glass and anti-reflective (moth-eye) glazing on inch-sized
// frames, not A sizes, so every A-size frame uses Perspex.

/** A personalised digital file (300 dpi PNG at the chosen size), instead of a print. */
export const DIGITAL_PRICE: Record<RegionId, number> = { GB: 19, US: 25, AU: 35 };

export interface PrintOptions {
  format?: "print" | "digital";
  productId: string;
  frame: FrameId;
  paper?: PaperId;
  mount?: MountId;
  glaze?: GlazeId;
}

/** The options as Prodigi can actually make them at this size (unframed-only sizes, papers per size). */
export function allowedOptions<T extends PrintOptions>(o: T): T {
  const p = getProduct(o.productId);
  let next = o;
  if (p.unframed && o.frame !== "none") next = { ...next, frame: "none" };
  if (p.papers && !p.papers.includes((next.paper ?? "ema") as PaperId)) next = { ...next, paper: "ema" };
  return next;
}

/** Print resolution: 300 dpi, a little less for the biggest posters (still sharp at viewing distance). */
export function printDpi(productId: string) {
  const p = getProduct(productId);
  const sqIn = (p.widthCm / 2.54) * (p.heightCm / 2.54);
  return Math.min(PRINT_DPI, Math.floor(Math.sqrt(72e6 / sqIn) / 10) * 10);
}

/** Each part of the price, so checkout can show the breakdown. */
export function priceLines(o0: PrintOptions, region: RegionId) {
  const o = allowedOptions(o0);
  const p = getProduct(o.productId);
  const framed = o.frame !== "none";
  const lines: { label: string; amount: number }[] = [];
  if (o.format === "digital") return [{ label: `Digital file, ${p.label} at 300 dpi`, amount: DIGITAL_PRICE[region] }];
  const paper = PAPERS.find((x) => x.id === (o.paper ?? "ema")) ?? PAPERS[0];
  const print = p.price[region];
  lines.push({ label: `${p.label} print`, amount: print });
  if (!framed && paper.extra) lines.push({ label: `${paper.label} paper`, amount: Math.round(print * paper.extra) });
  if (framed) {
    const f = FRAMES.find((x) => x.id === o.frame)!;
    const fp = p.framePrice[region];
    lines.push({ label: `${f.label} frame`, amount: fp });
    if (o.mount && o.mount !== "none") lines.push({ label: MOUNTS.find((m) => m.id === o.mount)?.label ?? "Mount", amount: Math.round(fp * MOUNT_EXTRA) });
    const g = GLAZES.find((x) => x.id === (o.glaze ?? "perspex")) ?? GLAZES[0];
    if (g.extra) lines.push({ label: `${g.label} glazing`, amount: Math.round(fp * g.extra) });
  }
  return lines;
}

export function itemPrice(o: PrintOptions, region: RegionId) {
  return priceLines(o, region).reduce((a, l) => a + l.amount, 0);
}

/** The Prodigi SKU and attributes for these options. */
export function prodigiItem(o0: PrintOptions) {
  const o = allowedOptions(o0);
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
  if (o.format === "digital") return `${getProduct(o.productId).label} digital file (300 dpi)`;
  const p = getProduct(o.productId);
  const parts = [`${p.label}${o.orientation ? ` ${o.orientation}` : ""}`];
  if (o.frame === "none") parts.push(`${(PAPERS.find((x) => x.id === (o.paper ?? "ema")) ?? PAPERS[0]).label.toLowerCase()} paper`);
  else {
    parts.push(`${FRAMES.find((f) => f.id === o.frame)!.label.toLowerCase()} frame`);
    if (o.mount && o.mount !== "none") parts.push((MOUNTS.find((m) => m.id === o.mount)?.label ?? "mount").toLowerCase());
    if (o.glaze && o.glaze !== "perspex") parts.push(GLAZES.find((g) => g.id === o.glaze)?.label.toLowerCase() ?? "");
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
  const dpi = printDpi(productId);
  const px = (cm: number) => Math.round((cm / 2.54) * dpi);
  return { width: px(w), height: px(h) };
}
