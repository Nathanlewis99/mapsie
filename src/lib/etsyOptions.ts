// The Etsy listing's options, mirroring mapsie.shop: Etsy allows only two variations,
// so the listing has "Size" and "Finish", where Finish combines paper, frame and mount
// (only valid pairings: specialist papers are unframed; framed prints are matte art,
// with or without a white mount, as Prodigi makes them).
import { describeOptions, DIGITAL_PRICE, FRAMES, itemPrice, PAPERS, PRODUCTS, type RegionId } from "./products";
import type { FrameId, MountId, PaperId } from "./types";

export interface EtsyPrint {
  format?: "print" | "digital";
  productId: string;
  frame: FrameId | string;
  paper?: PaperId;
  mount?: MountId;
}

const SHORT_PAPER: Record<PaperId, string> = { ema: "Matte art", hpr: "Cotton rag", hge: "Etching", lpp: "Lustre" };
const SHORT_FRAME: Record<string, string> = {
  black: "Black", white: "White", oak: "Natural wood", brown: "Brown", darkgrey: "Dark grey", lightgrey: "Light grey", gold: "Antique gold", silver: "Antique silver",
};

/** Every Finish option, in listing order. Labels fit Etsy's 20-character limit. */
export const ETSY_FINISHES: { code: string; label: string; frame: string; paper: PaperId; mount: MountId; digital?: boolean }[] = [
  ...PAPERS.map((p) => ({ code: p.id.toUpperCase(), label: `Unframed: ${SHORT_PAPER[p.id]}`, frame: "none", paper: p.id, mount: "none" as MountId })),
  ...FRAMES.filter((f) => f.id !== "none").flatMap((f) => [
    { code: f.id.toUpperCase(), label: `${SHORT_FRAME[f.id] ?? f.label} frame`.replace("Antique silver frame", "Silver frame").replace("Antique gold frame", "Gold frame"), frame: f.id, paper: "ema" as PaperId, mount: "none" as MountId },
    { code: `${f.id.toUpperCase()}-MOUNT`, label: `${(SHORT_FRAME[f.id] ?? f.label).replace("Antique ", "")} + mount`, frame: f.id, paper: "ema" as PaperId, mount: "white" as MountId },
  ]),
  { code: "DIGITAL", label: "Digital file", frame: "none", paper: "ema", mount: "none", digital: true },
];

const sizeCode = (productId: string) => productId.toUpperCase();
export const etsySku = (productId: string, finishCode: string) => `MAPSIE-${sizeCode(productId)}-${finishCode}`;

/** Price on Etsy for a size and finish: the same as mapsie.shop (UK prices, shipping included). */
export const etsyPrice = (productId: string, f: { frame: string; paper: PaperId; mount: MountId; digital?: boolean }, region: RegionId = "GB") =>
  f.digital ? DIGITAL_PRICE[region] : itemPrice({ productId, frame: f.frame as FrameId, paper: f.paper, mount: f.mount, glaze: "perspex" } as never, region);

/** All size × finish combinations for the listing, with SKU and price. */
export const ETSY_VARIATIONS = PRODUCTS.flatMap((p) =>
  ETSY_FINISHES.map((f) => ({ sku: etsySku(p.id, f.code), size: p.label, finish: f.label, price: etsyPrice(p.id, f), productId: p.id, ...f })),
);

/** What a SKU means. Also reads the first-version SKUs (MAPSIE-A3-NONE, MAPSIE-A3-BLACK). */
export function printFromSku(sku: string | null | undefined): EtsyPrint | null {
  const m = /^MAPSIE-([A-Z0-9]+)-([A-Z]+(?:-MOUNT)?)$/i.exec((sku ?? "").trim());
  if (!m) return null;
  const p = PRODUCTS.find((x) => sizeCode(x.id) === m[1].toUpperCase());
  const code = m[2].toUpperCase() === "NONE" ? "EMA" : m[2].toUpperCase();
  const f = ETSY_FINISHES.find((x) => x.code === code);
  return p && f ? { productId: p.id, frame: f.frame, paper: f.paper, mount: f.mount, ...(f.digital ? { format: "digital" as const } : {}) } : null;
}

/** "A3 · Black frame + white mount" style label for the buyer. */
export const etsyPrintLabel = (pr: EtsyPrint) =>
  describeOptions({ format: pr.format, productId: pr.productId, frame: pr.frame as FrameId, paper: pr.paper ?? "ema", mount: pr.mount ?? "none", glaze: "perspex" } as never);

/** The Etsy Finish option for a print, or undefined if Etsy doesn't sell that combination. */
export function etsyFinishFor(pr: EtsyPrint) {
  if (pr.format === "digital") return ETSY_FINISHES.find((f) => f.digital);
  return ETSY_FINISHES.find((f) => !f.digital && f.frame === pr.frame && f.paper === (pr.paper ?? "ema") && f.mount === (pr.mount ?? "none"));
}

/** A switch code looks like MPS-7KQ2XD; buyers paste it into Etsy's personalisation box. */
export const SWAP_CODE = /\bMPS-?([A-Z0-9]{6})\b/i;
