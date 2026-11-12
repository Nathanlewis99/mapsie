import { getKv, putKv } from "./db";
import { FRAMES, PAPERS, PRODUCTS, REGIONS, SHIPPING, itemPrice, prodigiItem, type PrintOptions, type RegionId } from "../products";

// What each product costs us. Prodigi publishes its full price sheets (the same
// files as "Download price sheet" in their dashboard), per printing region.
// Prices exclude VAT. We keep just the rows for the SKUs we sell.
const SHEET = (category: string, region: string) =>
  `https://prodigipricingpublic.blob.core.windows.net/public/live/prodigi-${category}-${region}.csv`;
const CATEGORIES = ["prints-%26-posters-art-prints", "prints-%26-posters-photo-prints", "wall-art-framed-prints"];
const SHEET_REGION: Record<RegionId, string> = { GB: "gb", US: "us", AU: "au" };

export interface SkuCost {
  product: number;
  currency: string;
  shipping: Record<string, number>; // method -> first-item price
}
export type CostTable = Record<RegionId, Record<string, SkuCost>>;
const KV_KEY = "prodigi-costs";

function parseLine(line: string): string[] {
  const out: string[] = [];
  let cur = "", q = false;
  for (let i = 0; i < line.length; i++) {
    const ch = line[i];
    if (q) {
      if (ch === '"' && line[i + 1] === '"') (cur += '"'), i++;
      else if (ch === '"') q = false;
      else cur += ch;
    } else if (ch === '"') q = true;
    else if (ch === ",") out.push(cur), (cur = "");
    else cur += ch;
  }
  out.push(cur);
  return out.map((x) => x.trim());
}

/** All the SKUs our options can produce. */
function ourSkus() {
  const skus = new Set<string>();
  for (const p of PRODUCTS) {
    for (const paper of PAPERS) skus.add(prodigiItem({ productId: p.id, frame: "none", paper: paper.id }).sku);
    skus.add(prodigiItem({ productId: p.id, frame: "black" }).sku);
    skus.add(prodigiItem({ productId: p.id, frame: "black", mount: "white" }).sku);
  }
  return skus;
}

/** Download Prodigi's price sheets and keep the rows for our products. Takes ~30s (the framed sheet is large). */
export async function refreshCosts(): Promise<CostTable> {
  const wanted = ourSkus();
  const table = { GB: {}, US: {}, AU: {} } as CostTable;
  for (const region of REGIONS.map((r) => r.id)) {
    for (const cat of CATEGORIES) {
      const r = await fetch(SHEET(cat, SHEET_REGION[region]));
      if (!r.ok || !r.body) throw new Error(`Price sheet ${cat}-${region}: ${r.status}`);
      const reader = r.body.pipeThrough(new TextDecoderStream()).getReader();
      let buf = "", header: string[] | null = null;
      const handle = (line: string) => {
        if (!line.trim()) return;
        if (!header) return void (header = parseLine(line));
        // Cheap filter before parsing: only lines for one of our SKUs.
        const m = /"(GLOBAL-[A-Z]+-[0-9A-Z]+)"/.exec(line);
        if (!m || !wanted.has(m[1])) return;
        const f = parseLine(line);
        const col = (name: string) => f[header!.indexOf(name)];
        if (col("Destination country") !== region) return;
        const color = col("Color");
        if (color && color !== "black") return; // frame colours all cost the same; keep one
        const sku = col("SKU");
        const e = (table[region][sku] ??= { product: Number(col("Product price")), currency: col("Product currency"), shipping: {} });
        e.shipping[col("Shipping method")] = Number(col("Shipping price"));
      };
      for (;;) {
        const { value, done } = await reader.read();
        if (done) break;
        buf += value;
        const lines = buf.split("\n");
        buf = lines.pop() ?? "";
        lines.forEach(handle);
      }
      handle(buf);
    }
  }
  await putKv(KV_KEY, table);
  return table;
}

export async function getCosts() {
  return getKv<CostTable>(KV_KEY);
}

// Card fees: Stripe UK pricing (domestic cards; international cards cost more, plus
// 2% when we convert USD/AUD to GBP). Rough but on the cautious side.
const stripeFee = (amount: number, region: RegionId) => (region === "GB" ? amount * 0.015 + 0.2 : amount * (0.0325 + 0.02) + 0.3);

export interface MarginRow {
  label: string;
  price: number;
  cost: number | null; // product + standard shipping, in the region's currency
  fee: number;
  margin: number | null;
  vat: number; // VAT included in the price if we're VAT registered (UK only)
}

/** Our price vs Prodigi's cost for every size and the main options, per region. */
export function marginTable(costs: CostTable, region: RegionId): { product: string; rows: MarginRow[] }[] {
  const ship = SHIPPING[0].prodigiMethod; // our free delivery
  const options: { label: string; o: Omit<PrintOptions, "productId"> }[] = [
    ...PAPERS.map((p) => ({ label: `Print · ${p.label}`, o: { frame: "none" as const, paper: p.id } })),
    { label: `Framed (${FRAMES[1].label.toLowerCase()} etc.)`, o: { frame: "black" as const } },
    { label: "Framed + mount", o: { frame: "black" as const, mount: "white" as const } },
  ];
  return PRODUCTS.map((p) => ({
    product: p.label,
    rows: options.map(({ label, o }) => {
      const opts = { productId: p.id, ...o };
      const price = itemPrice(opts, region);
      const c = costs[region]?.[prodigiItem(opts).sku];
      const cost = c ? c.product + (c.shipping[ship] ?? c.shipping.Standard ?? 0) : null;
      const fee = stripeFee(price, region);
      return { label, price, cost, fee, margin: cost === null ? null : price - cost - fee, vat: region === "GB" ? price / 6 : 0 };
    }),
  }));
}
