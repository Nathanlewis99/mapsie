import { getDesign, getOrder, updateOrder, type Address } from "./db";
import { renderDesign } from "./render";
import { submitPrintOrder } from "./prodigi";

/** After payment: render the print file, then hand it to the print company. */
export async function fulfilOrder(orderId: string, address: Address) {
  const order = await updateOrder(orderId, { status: "paid", address });
  try {
    const design = await getDesign(order.designId);
    if (!design) throw new Error("design missing");
    await updateOrder(orderId, { status: "rendering" });
    const r = await renderDesign(design, `${order.id}.png`);
    await updateOrder(orderId, { renderFile: r.file, renderInfo: { width: r.width, height: r.height, dpi: r.dpi } });
    // The print company downloads the file from this URL, so APP_URL must be public in production.
    const assetUrl = `${process.env.APP_URL ?? "http://localhost:3000"}/api/renders/${r.file}`;
    const sent = await submitPrintOrder((await getOrder(orderId))!, design, address, assetUrl);
    await updateOrder(orderId, { status: "submitted", printProviderOrderId: sent.id });
  } catch (e) {
    console.error("[fulfil]", e);
    await updateOrder(orderId, { status: "failed", error: String(e) });
  }
}
