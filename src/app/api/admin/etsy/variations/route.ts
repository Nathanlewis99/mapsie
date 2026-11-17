import { ETSY_VARIATIONS } from "@/lib/etsyOptions";

/** Admin only (middleware): the listing's variations as CSV, for setting up Etsy. */
export async function GET() {
  const q = (s: string | number) => `"${String(s).replace(/"/g, '""')}"`;
  const rows = [["Size", "Finish", "SKU", "Price (GBP)"], ...ETSY_VARIATIONS.map((v) => [v.size, v.finish, v.sku, v.price])];
  return new Response(rows.map((r) => r.map(q).join(",")).join("\n") + "\n", {
    headers: { "content-type": "text/csv; charset=utf-8", "content-disposition": 'attachment; filename="mapsie-etsy-variations.csv"' },
  });
}
