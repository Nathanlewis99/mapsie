import { NextResponse } from "next/server";
import { disconnectEtsy, etsySku, importReceipt, setEtsyListingUrl, syncEtsyOrders } from "@/lib/server/etsy";
import { ETSY_FINISHES } from "@/lib/etsyOptions";
import { listOrdersByEtsyReceipt } from "@/lib/server/db";
import { PRODUCTS } from "@/lib/products";
import { getOrder, updateOrder } from "@/lib/server/db";
import { sendEtsyDesignEmail } from "@/lib/server/email";
import { publicUrl } from "@/lib/server/urls";

// Admin only (middleware). Form posts from /admin/etsy.
export async function POST(req: Request) {
  const f = await req.formData();
  const action = String(f.get("action"));
  let q = "";
  try {
    if (action === "sync") q = `synced=${await syncEtsyOrders()}`;
    if (action === "manual") {
      // An Etsy order typed in by hand (when the Etsy connection isn't available).
      const v = (k: string) => String(f.get(k) ?? "").trim();
      const receipt = v("receipt").replace(/[^\d]/g, "");
      const productId = v("productId");
      const finish = ETSY_FINISHES.find((x) => x.code === v("finish"));
      const qty = Math.min(10, Math.max(1, Number(v("quantity")) || 1));
      if (!receipt) throw new Error("Enter the Etsy order number.");
      if (!PRODUCTS.some((p) => p.id === productId) || !finish) throw new Error("Choose a size and finish.");
      if (!v("name") || !v("line1") || !v("city") || !v("postcode") || !/^[A-Z]{2}$/i.test(v("country"))) throw new Error("Fill in the full delivery address (country as a 2-letter code, e.g. GB).");
      if ((await listOrdersByEtsyReceipt(receipt)).length) throw new Error(`Etsy order ${receipt} is already on Mapsie.`);
      const price = Number(v("price"));
      const made = await importReceipt({
        receipt_id: Number(receipt),
        buyer_email: v("email") || null,
        name: v("name"),
        first_line: v("line1"),
        second_line: v("line2") || null,
        city: v("city"),
        state: v("state") || null,
        zip: v("postcode"),
        country_iso: v("country").toUpperCase(),
        is_paid: true,
        created_timestamp: Math.floor(Date.now() / 1000),
        transactions: [{
          transaction_id: Number(receipt),
          title: "Custom travel map (added by hand)",
          quantity: qty,
          sku: etsySku(productId, finish.code),
          price: price > 0 ? { amount: Math.round((price / qty) * 100), divisor: 100, currency_code: v("currency") || "GBP" } : undefined,
          shipping_upgrade: f.get("express") ? "Express" : null,
          variations: v("personal") ? [{ formatted_name: "Personalisation", formatted_value: v("personal") }] : [],
        }],
      });
      q = `added=${made}&receipt=${receipt}`;
    }
    if (action === "disconnect") {
      await disconnectEtsy();
      q = "disconnected=1";
    }
    if (action === "listingUrl") {
      await setEtsyListingUrl(String(f.get("url") ?? ""));
      q = "saved=1";
    }
    if (action === "refunded") {
      const o = await getOrder(String(f.get("orderId")));
      if (o?.etsy?.refundDue) await updateOrder(o.id, { etsy: { ...o.etsy, refunded: true } });
      q = "refunded=1";
    }
    if (action === "resend") {
      const o = await getOrder(String(f.get("orderId")));
      if (o) await sendEtsyDesignEmail(o, "invite", true);
      q = "resent=1";
    }
  } catch (e) {
    q = `error=${encodeURIComponent(String((e as Error).message ?? e).slice(0, 200))}`;
  }
  return NextResponse.redirect(`${publicUrl()}/admin/etsy?${q}`, { status: 303 });
}
