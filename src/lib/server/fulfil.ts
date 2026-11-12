import { getDesign, getOrder, updateOrder, type Address, type Order } from "./db";
import { normalizeDesign } from "../types";
import { renderDesign, FALLBACK } from "./render";
import { publicUrl } from "./urls";
import { submitPrintOrder } from "./prodigi";

/** Minutes after payment during which the customer can cancel. */
export const HOLD_MINUTES = Number(process.env.ORDER_HOLD_MINUTES ?? 60);

export const canCancel = (o: Order) =>
  ["paid", "rendering", "ready"].includes(o.status) && !!o.holdUntil && new Date(o.holdUntil).getTime() > Date.now();

/**
 * After payment: make the print file straight away, then hold the order until
 * the cancellation window ends. The scheduler (scheduler.ts) sends it to print.
 */
export async function fulfilOrder(orderId: string, address: Address, extra: Partial<Order> = {}) {
  const now = new Date();
  const order = await updateOrder(orderId, {
    status: "paid",
    address,
    error: undefined,
    paidAt: now.toISOString(),
    holdUntil: new Date(now.getTime() + HOLD_MINUTES * 60_000).toISOString(),
    ...extra,
  });
  try {
    const raw = await getDesign(order.designId);
    if (!raw) throw new Error("design missing");
    const design = normalizeDesign(raw);
    await updateOrder(orderId, { status: "rendering" });
    let r;
    try {
      r = await renderDesign(design, `${order.id}.png`);
    } catch (e) {
      // Usually memory pressure on a small machine: retry once with lighter settings.
      console.warn("[fulfil] render failed, retrying with lighter settings:", String(e).slice(0, 200));
      r = await renderDesign(design, `${order.id}.png`, FALLBACK);
    }
    // The customer may have cancelled while we were rendering.
    if ((await getOrder(orderId))?.status === "cancelled") return;
    await updateOrder(orderId, {
      status: "ready",
      renderFile: r.file,
      renderInfo: { width: r.width, height: r.height, dpi: r.dpi, mapDpi: r.mapDpi },
    });
    if (HOLD_MINUTES <= 0) await sendToPrint(orderId);
  } catch (e) {
    console.error("[fulfil]", e);
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
    console.error("[print]", e);
    await updateOrder(orderId, { status: "failed", error: String(e) });
  }
}
