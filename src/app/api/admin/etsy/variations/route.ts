import { etsyVariations } from "@/lib/etsyOptions";

/** Admin only (middleware): a listing's variations as CSV, for setting up Etsy. ?listing=US for the US listing. */
export async function GET(req: Request) {
  const us = new URL(req.url).searchParams.get("listing")?.toUpperCase() === "US";
  const q = (s: string | number) => `"${String(s).replace(/"/g, '""')}"`;
  const rows = [["Size", "Finish", "SKU", "Price (GBP)"], ...etsyVariations(us ? "US" : "GB").map((v) => [v.size, v.finish, v.sku, v.price])];
  return new Response(rows.map((r) => r.map(q).join(",")).join("\n") + "\n", {
    headers: { "content-type": "text/csv; charset=utf-8", "content-disposition": `attachment; filename="mapsie-etsy-variations${us ? "-us" : ""}.csv"` },
  });
}
