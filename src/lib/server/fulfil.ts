import { claimOrder, getDesign, getOrder, listOrdersByStatus, recordEvent, updateOrder, type Address, type Order } from "./db";
import { normalizeDesign } from "../types";
import { renderDesign, FALLBACK } from "./render";
import { publicUrl } from "./urls";
import { submitPrintOrder } from "./prodigi";
import { logError } from "./log";
import { alertAdmin, sendOrderEmail } from "./email";

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
export async function fulfilOrder(orderId: string, address: Address, extra: Partial<Order> = {}) {
  const now = new Date();
  await updateOrder(orderId, {
    status: "paid",
    address,
    error: undefined,
    paidAt: now.toISOString(),
    holdUntil: new Date(now.getTime() + HOLD_MINUTES * 60_000).toISOString(),
    ...extra,
  });
  const paid = await getOrder(orderId);
  if (paid?.visitId) await recordEvent(paid.visitId, "paid", { total: paid.total, currency: paid.currency }).catch(() => {});
  await sendOrderEmail(orderId, "confirmed");
  if (ROLE !== "web") void processPaidOrders();
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
    if (HOLD_MINUTES <= 0) await sendToPrint(orderId);
  } catch (e) {
    await logError("order.render", e, { orderId });
    await alertAdmin(`Order ${orderId}: print file failed`, `The print file for order ${orderId} couldn't be made.\n\n${String(e).slice(0, 1500)}\n\nRetry it from the admin page.`);
    await updateOrder(orderId, { status: "failed", error: String(e) });
  }
}

/** Hand a ready order to the print company. */
export async function sendToPrint(orderId: string) {
  const order = await getOrder(orderId);
  if (!order || order.status !== "ready" || !order.renderFile || !order.address) return;
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
