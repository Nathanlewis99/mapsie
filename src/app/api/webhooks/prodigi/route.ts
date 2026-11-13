import { NextResponse } from "next/server";
import { getOrder, updateOrder } from "@/lib/server/db";
import { getProdigiOrder } from "@/lib/server/prodigi";
import { callbackTokenValid } from "@/lib/server/printToken";
import { logError } from "@/lib/server/log";
import { alertAdmin, sendOrderEmail } from "@/lib/server/email";
import { sendEtsyTracking } from "@/lib/server/etsy";

// Prodigi calls this when one of our orders changes (in production, shipped, etc.).
// The URL carries a signed token per order, and we re-read the order from
// Prodigi's API rather than trusting the callback body.
export async function POST(req: Request) {
  const url = new URL(req.url);
  const orderId = url.searchParams.get("o") ?? "";
  if (!callbackTokenValid(orderId, url.searchParams.get("t"))) return NextResponse.json({ error: "bad token" }, { status: 401 });
  const order = await getOrder(orderId);
  if (!order?.printProviderOrderId) return NextResponse.json({ ok: true });
  const p = await getProdigiOrder(order.printProviderOrderId).catch((e) => {
    void logError("prodigi.callback", e, { orderId });
    return null;
  });
  if (!p) return NextResponse.json({ ok: true });
  const shipments = (p.shipments ?? [])
    .filter((s) => s.tracking?.number || s.tracking?.url || s.dispatchDate)
    .map((s) => ({ carrier: s.carrier?.name, trackingNumber: s.tracking?.number, trackingUrl: s.tracking?.url, dispatchDate: s.dispatchDate }));
  const stage = p.status?.stage;
  await updateOrder(orderId, {
    printStage: stage,
    shipments,
    ...(stage === "Complete" || shipments.length ? { status: "shipped" as const } : {}),
    ...(stage === "Cancelled" ? { status: "failed" as const, error: "Cancelled by the printer" } : {}),
  });
  if (stage === "Complete" || shipments.length) {
    await sendOrderEmail(orderId, "shipped");
    if (order.etsy) await sendEtsyTracking(orderId);
  }
  if (stage === "Cancelled") await alertAdmin(`Order ${orderId} was cancelled by Prodigi`, `Prodigi order ${order.printProviderOrderId} is now Cancelled. Check the Prodigi dashboard and contact the customer (${order.email}).`);
  return NextResponse.json({ ok: true });
}
