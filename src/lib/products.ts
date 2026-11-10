import type { Orientation } from "./types";

// Print sizes we sell. `prodigiSku` values are placeholders: check them
// against the Prodigi product catalogue before going live.
export interface Product {
  id: string;
  label: string;
  widthCm: number; // portrait width
  heightCm: number; // portrait height
  priceGbp: number;
  prodigiSku: string;
}

export const PRODUCTS: Product[] = [
  { id: "a4", label: "A4", widthCm: 21, heightCm: 29.7, priceGbp: 34, prodigiSku: "GLOBAL-FAP-A4" },
  { id: "a3", label: "A3", widthCm: 29.7, heightCm: 42, priceGbp: 44, prodigiSku: "GLOBAL-FAP-A3" },
  { id: "a2", label: "A2", widthCm: 42, heightCm: 59.4, priceGbp: 59, prodigiSku: "GLOBAL-FAP-A2" },
  { id: "50x70", label: "50 × 70 cm", widthCm: 50, heightCm: 70, priceGbp: 69, prodigiSku: "GLOBAL-FAP-50X70" },
  { id: "a1", label: "A1", widthCm: 59.4, heightCm: 84.1, priceGbp: 84, prodigiSku: "GLOBAL-FAP-A1" },
];

export const SHIPPING = [
  { id: "standard", label: "Free UK delivery", detail: "3–5 working days", priceGbp: 0, prodigiMethod: "Standard" },
  { id: "express", label: "Express", detail: "Next working day", priceGbp: 9.95, prodigiMethod: "Express" },
] as const;

export type ShippingId = (typeof SHIPPING)[number]["id"];

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
