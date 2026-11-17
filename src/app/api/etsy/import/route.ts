import { NextResponse } from "next/server";
import { timingSafeEqual } from "node:crypto";
import { etsySku, importReceipt, type Receipt } from "@/lib/server/etsy";
import { logError } from "@/lib/server/log";
import { FRAMES, PRODUCTS } from "@/lib/products";

/**
 * New Etsy orders pushed in by an automation service (Make.com or Zapier) that has
 * Etsy access, for shops whose own Etsy API app isn't approved.
 *
 * POST /api/etsy/import with header `x-mapsie-key: <ETSY_IMPORT_SECRET>` and Etsy's
 * receipt as JSON (field names as in Etsy's API: receipt_id, buyer_email, name,
 * first_line, second_line, city, state, zip, country_iso, transactions[] with
 * transaction_id, quantity, sku, title, variations[], price). Automation tools often
 * send `transactions` as a JSON string, or flatten a single item into `sku` and
 * `quantity`: both are accepted. Importing the same order twice does nothing.
 */
export async function POST(req: Request) {
  const want = process.env.ETSY_IMPORT_SECRET ?? "";
  const got = req.headers.get("x-mapsie-key") ?? "";
  if (want.length < 20 || got.length !== want.length || !timingSafeEqual(Buffer.from(got), Buffer.from(want))) {
    return NextResponse.json({ error: "Not authorised" }, { status: 401 });
  }
  let b: Record<string, unknown>;
  try {
    b = (await req.json()) as Record<string, unknown>;
  } catch {
    return NextResponse.json({ error: "Send the Etsy order as JSON" }, { status: 400 });
  }
  // Some tools wrap the order: { receipt: {...} } or { data: {...} }.
  const r = (typeof b.receipt === "object" && b.receipt) || (typeof b.data === "object" && b.data) || b;
  const o = r as Record<string, unknown>;
  const str = (v: unknown) => (v == null ? "" : String(v)).trim();
  const receiptId = Number(str(o.receipt_id).replace(/[^\d]/g, ""));
  if (!receiptId) return NextResponse.json({ error: "receipt_id is missing" }, { status: 400 });
  if (o.is_paid === false || str(o.is_paid) === "false") return NextResponse.json({ ok: true, skipped: "not paid yet" });

  let txs: unknown = o.transactions;
  if (typeof txs === "string") {
    try {
      txs = JSON.parse(txs);
    } catch {
      txs = undefined;
    }
  }
  let transactions: Receipt["transactions"] = Array.isArray(txs)
    ? txs.map((t: Record<string, unknown>, i: number) => ({
        transaction_id: Number(t.transaction_id) || receiptId * 10 + i,
        title: str(t.title) || undefined,
        quantity: Math.max(1, Number(t.quantity) || 1),
        sku: str(t.sku) || null,
        variations: Array.isArray(t.variations) ? (t.variations as Receipt["transactions"][number]["variations"]) : [],
        price: typeof t.price === "object" ? (t.price as Receipt["transactions"][number]["price"]) : undefined,
        shipping_upgrade: str(t.shipping_upgrade) || null,
      }))
    : [];
  if (!transactions.length) {
    // A single flattened item: sku, or size + frame, plus quantity.
    const size = PRODUCTS.find((p) => p.id === str(o.size).toLowerCase())?.id;
    const frame = FRAMES.find((f) => f.id === str(o.frame).toLowerCase())?.id;
    transactions = [{
      transaction_id: receiptId,
      quantity: Math.max(1, Number(o.quantity) || 1),
      sku: str(o.sku) || (size && frame ? etsySku(size, frame) : null),
      variations: str(o.variations) ? [{ formatted_name: "Options", formatted_value: str(o.variations) }] : [],
    }];
  }

  try {
    const made = await importReceipt({
      receipt_id: receiptId,
      buyer_email: str(o.buyer_email) || null,
      name: str(o.name),
      first_line: str(o.first_line),
      second_line: str(o.second_line) || null,
      city: str(o.city),
      state: str(o.state) || null,
      zip: str(o.zip),
      country_iso: str(o.country_iso) || "GB",
      is_paid: true,
      created_timestamp: Number(o.created_timestamp) || Math.floor(Date.now() / 1000),
      transactions,
    });
    return NextResponse.json({ ok: true, created: made });
  } catch (e) {
    await logError("etsy.import", e, { receiptId });
    return NextResponse.json({ error: "Couldn't import that order" }, { status: 500 });
  }
}
