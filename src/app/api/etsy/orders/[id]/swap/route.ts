import { NextResponse } from "next/server";
import { getDesign, getOrder } from "@/lib/server/db";
import { etsyTokenValid, requestSwap } from "@/lib/server/etsy";
import { etsyFinishFor, etsyPrice, etsyPrintLabel, etsySku } from "@/lib/etsyOptions";
import { PRODUCTS } from "@/lib/products";

/** Where buyers buy the replacement print. Set ETSY_LISTING_URL on Render. */
const listingUrl = () => process.env.ETSY_LISTING_URL || process.env.ETSY_SHOP_URL || "https://www.etsy.com/your/purchases";

/**
 * An Etsy buyer wants a different print. They buy it on Etsy (with the switch code in
 * the personalisation box) and we refund the first order in full. See requestSwap.
 */
export async function POST(req: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const b = (await req.json().catch(() => ({}))) as { k?: string; designId?: string; to?: Record<string, string> };
  if (!etsyTokenValid(id, b.k)) return NextResponse.json({ error: "This link isn't valid." }, { status: 404 });
  const o = await getOrder(id);
  if (!o?.print || o.status !== "awaiting_design") return NextResponse.json({ error: "This order has already been sent to print, so it can't be switched." }, { status: 409 });
  const t = b.to ?? {};
  const to = {
    productId: String(t.productId ?? ""),
    frame: String(t.frame ?? "none"),
    paper: (t.paper ?? "ema") as NonNullable<typeof o.print.paper>,
    mount: (t.mount ?? "none") as NonNullable<typeof o.print.mount>,
    format: t.format === "digital" ? ("digital" as const) : ("print" as const),
  };
  const finish = etsyFinishFor(to);
  if (!PRODUCTS.some((p) => p.id === to.productId) || !finish) return NextResponse.json({ error: "That combination isn't sold on Etsy. Please pick another." }, { status: 400 });
  const designId = b.designId && (await getDesign(b.designId)) ? b.designId : undefined;
  const code = await requestSwap(id, to, designId);
  if (!code) return NextResponse.json({ error: "This order can't be switched." }, { status: 409 });
  return NextResponse.json({
    code,
    sku: etsySku(to.productId, finish.code),
    size: PRODUCTS.find((p) => p.id === to.productId)!.label,
    finish: finish.label,
    label: etsyPrintLabel(to),
    price: etsyPrice(to.productId, finish), // the listing is priced in pounds; Etsy converts for the buyer
    paid: o.total,
    currency: o.currency,
    listingUrl: listingUrl(),
  });
}
