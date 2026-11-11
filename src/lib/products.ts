import type { FrameId, Orientation } from "./types";

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
// `prodigiSku` values are placeholders: check them against the Prodigi
// catalogue (and their real costs) before going live.
export interface Product {
  id: string;
  label: string;
  widthCm: number; // portrait width
  heightCm: number; // portrait height
  price: Record<RegionId, number>;
  framePrice: Record<RegionId, number>;
  prodigiSku: string;
  prodigiFramedSku: string;
}

export const PRODUCTS: Product[] = [
  { id: "a4", label: "A4", widthCm: 21, heightCm: 29.7, price: { GB: 34, US: 45, AU: 65 }, framePrice: { GB: 25, US: 35, AU: 49 }, prodigiSku: "GLOBAL-FAP-A4", prodigiFramedSku: "GLOBAL-CFP-A4" },
  { id: "a3", label: "A3", widthCm: 29.7, heightCm: 42, price: { GB: 44, US: 59, AU: 85 }, framePrice: { GB: 35, US: 45, AU: 65 }, prodigiSku: "GLOBAL-FAP-A3", prodigiFramedSku: "GLOBAL-CFP-A3" },
  { id: "a2", label: "A2", widthCm: 42, heightCm: 59.4, price: { GB: 59, US: 79, AU: 115 }, framePrice: { GB: 55, US: 69, AU: 99 }, prodigiSku: "GLOBAL-FAP-A2", prodigiFramedSku: "GLOBAL-CFP-A2" },
  { id: "50x70", label: "50 × 70 cm", widthCm: 50, heightCm: 70, price: { GB: 69, US: 89, AU: 129 }, framePrice: { GB: 65, US: 79, AU: 115 }, prodigiSku: "GLOBAL-FAP-50X70", prodigiFramedSku: "GLOBAL-CFP-50X70" },
  { id: "a1", label: "A1", widthCm: 59.4, heightCm: 84.1, price: { GB: 84, US: 109, AU: 159 }, framePrice: { GB: 80, US: 99, AU: 145 }, prodigiSku: "GLOBAL-FAP-A1", prodigiFramedSku: "GLOBAL-CFP-A1" },
];

export const FRAMES: { id: FrameId; label: string; color: string; prodigiColor?: string }[] = [
  { id: "none", label: "No frame", color: "transparent" },
  { id: "black", label: "Black", color: "#1b1b1b", prodigiColor: "black" },
  { id: "white", label: "White", color: "#f4f4f2", prodigiColor: "white" },
  { id: "oak", label: "Natural oak", color: "#c49a6c", prodigiColor: "natural" },
];

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

export function itemPrice(productId: string, frame: FrameId, region: RegionId) {
  const p = getProduct(productId);
  return p.price[region] + (frame !== "none" ? p.framePrice[region] : 0);
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
