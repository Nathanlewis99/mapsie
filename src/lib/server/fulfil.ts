import { getDesign, getOrder, updateOrder, type Address } from "./db";
import { normalizeDesign } from "../types";
import { renderDesign, FALLBACK } from "./render";
import { publicUrl } from "./urls";
import { submitPrintOrder } from "./prodigi";

/** After payment: render the print file, then hand it to the print company. */
export async function fulfilOrder(orderId: string, address: Address) {
  const order = await updateOrder(orderId, { status: "paid", address, error: undefined });
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
    await updateOrder(orderId, { renderFile: r.file, renderInfo: { width: r.width, height: r.height, dpi: r.dpi, mapDpi: r.mapDpi } });
    // The print company downloads the file from this URL, so it must be public in production.
    const assetUrl = `${publicUrl()}/api/renders/${r.file}`;
    const sent = await submitPrintOrder((await getOrder(orderId))!, design, address, assetUrl);
    await updateOrder(orderId, { status: "submitted", printProviderOrderId: sent.id });
  } catch (e) {
    console.error("[fulfil]", e);
    await updateOrder(orderId, { status: "failed", error: String(e) });
  }
}
