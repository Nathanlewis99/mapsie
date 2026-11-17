import { claimOrder, getDesign, getOrder, listOrdersByStatus, recordEvent, updateOrder, type Address, type Order } from "./db";
import { sendPurchaseConversions } from "./conversions";
import { normalizeDesign } from "../types";
import { renderDesign, FALLBACK } from "./render";
import { publicUrl } from "./urls";
import { submitPrintOrder } from "./prodigi";
import { logError } from "./log";
import { alertAdmin, sendOrderEmail, sendSaleAlert } from "./email";

/** Minutes after payment during which the customer can cancel. */
export const HOLD_MINUTES = Number(process.env.ORDER_HOLD_MINUTES ?? 60);

export const canCancel = (o: Order) =>
  ["paid", "rendering", "ready"].includes(o.status) && !!o.holdUntil && new Date(o.holdUntil).getTime() > Date.now();

/** "web" serves the site only, "worker" renders and sends orders, "all" does both (one server). */
export const ROLE = (process.env.MAPSIE_ROLE ?? "all") as "web" | "worker" | "all";

/**
 * After payment: record it and queue the order. A worker (this server, or the
 * separate render worker when the site runs on several servers) makes the
 * print file, then holds the order until the cancellation window ends.
 */
export async function fulfilOrder(orderId: string, address: Address | undefined, extra: Partial<Order> = {}, from: Order["status"] = "pending_payment") {
  // Exactly once: payment webhooks can arrive more than once (retries, completed and
  // async_payment_succeeded), and a repeat must never re-queue an order already in progress.
  if (!(await claimOrder(orderId, from, "paid"))) return;
  const now = new Date();
  // Digital files are delivered as soon as they're made (the buyer agreed to that at checkout).
  const instant = (await getOrder(orderId))?.digital;
  await updateOrder(orderId, {
    status: "paid",
    address,
    error: undefined,
    paidAt: now.toISOString(),
    holdUntil: new Date(now.getTime() + (instant ? 0 : HOLD_MINUTES) * 60_000).toISOString(),
    ...extra,
  });
  const paid = await getOrder(orderId);
  if (paid?.visitId) await recordEvent(paid.visitId, "paid", { total: paid.total, currency: paid.currency }).catch(() => {});
  await sendOrderEmail(orderId, "confirmed");
  await sendSaleAlert(orderId);
  if (paid) await sendPurchaseConversions(paid);
  if (ROLE !== "web") void processPaidOrders();
}

/** A delayed payment (e.g. bank debit) failed after checkout: the order is never printed. */
export async function markPaymentFailed(orderId: string) {
  const o = await getOrder(orderId);
  if (o?.status !== "pending_payment") return;
  await updateOrder(orderId, { status: "cancelled", error: "Payment failed", cancelledAt: new Date().toISOString() });
}

let rendering = false;
/** Render every paid order, one at a time (rendering a big print is memory hungry). */
export async function processPaidOrders() {
  if (rendering) return;
  rendering = true;
  try {
    for (const o of await listOrdersByStatus("paid")) {
      const claimed = await claimOrder(o.id, "paid", "rendering");
      if (claimed) await renderOrder(claimed);
    }
  } finally {
    rendering = false;
  }
}

async function renderOrder(order: Order) {
  const orderId = order.id;
  try {
    const raw = await getDesign(order.designId);
    if (!raw) throw new Error("design missing");
    const design = normalizeDesign(raw);
    let r;
    try {
      r = await renderDesign(design, `${order.id}.png`);
    } catch (e) {
      // Usually memory pressure on a small machine: retry once with lighter settings.
      console.warn("[fulfil] render failed, retrying with lighter settings:", String(e).slice(0, 200));
      r = await renderDesign(design, `${order.id}.png`, FALLBACK);
    }
    // The customer may have cancelled (or, for Etsy, reopened the design) while we were rendering.
    if ((await getOrder(orderId))?.status !== "rendering") return;
    await updateOrder(orderId, {
      status: "ready",
      renderFile: r.file,
      renderInfo: { width: r.width, height: r.height, dpi: r.dpi, mapDpi: r.mapDpi },
    });
    if (HOLD_MINUTES <= 0 || order.digital) await sendToPrint(orderId);
  } catch (e) {
    await logError("order.render", e, { orderId });
    await alertAdmin(`Order ${orderId}: print file failed`, `The print file for order ${orderId} couldn't be made.\n\n${String(e).slice(0, 1500)}\n\nRetry it from the admin page.`);
    await updateOrder(orderId, { status: "failed", error: String(e) });
  }
}

/** Hand a ready order to the print company. */
export async function sendToPrint(orderId: string) {
  const order = await getOrder(orderId);
  if (!order || order.status !== "ready" || !order.renderFile) return;
  if (order.digital) {
    // A digital file: nothing to print. Deliver the download link.
    await updateOrder(orderId, { status: "delivered", error: undefined });
    await sendOrderEmail(orderId, "delivered");
    return;
  }
  if (!order.address) return;
  try {
    const raw = await getDesign(order.designId);
    if (!raw) throw new Error("design missing");
    // The print company downloads the file from this URL, so it must be public in production.
    const assetUrl = `${publicUrl()}/api/renders/${order.renderFile}`;
    const sent = await submitPrintOrder(order, normalizeDesign(raw), order.address, assetUrl);
    await updateOrder(orderId, { status: "submitted", printProviderOrderId: sent.id, error: undefined });
  } catch (e) {
    await logError("order.print", e, { orderId });
    await alertAdmin(`Order ${orderId}: couldn't send to the printer`, `Prodigi rejected or didn't accept order ${orderId}.\n\n${String(e).slice(0, 1500)}\n\nRetry it from the admin page.`);
    await updateOrder(orderId, { status: "failed", error: String(e) });
  }
}
