import { NextResponse } from "next/server";
import { nanoid } from "nanoid";
import { claimOrder, getDesign, saveDesign, updateOrder } from "@/lib/server/db";
import { etsyTokenValid } from "@/lib/server/etsy";
import { fulfilOrder } from "@/lib/server/fulfil";
import { normalizeDesign } from "@/lib/types";
import { validEmail } from "@/lib/server/password";

/**
 * An Etsy buyer presses "Send to print". Their design is copied with the size and
 * frame they paid for, and the order joins the normal queue (render, hold, Prodigi).
 */
export async function POST(req: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const body = (await req.json().catch(() => ({}))) as { k?: string; designId?: string; email?: string };
  if (!etsyTokenValid(id, body.k)) return NextResponse.json({ error: "This link isn't valid." }, { status: 404 });
  const raw = body.designId ? await getDesign(body.designId) : null;
  if (!raw) return NextResponse.json({ error: "We couldn't find your design. Please go back and try again." }, { status: 400 });
  // Only one submission wins, even if the button is pressed twice.
  const order = await claimOrder(id, "awaiting_design", "pending_payment");
  if (!order?.print || !order.address) return NextResponse.json({ error: "This map has already been sent to print." }, { status: 409 });
  try {
    const design = { ...normalizeDesign(raw), id: nanoid(10), productId: order.print.productId, frame: order.print.frame, paper: "ema", mount: "none", glaze: "perspex" } as ReturnType<typeof normalizeDesign>;
    await saveDesign(design);
    const email = typeof body.email === "string" && validEmail(body.email.trim()) ? body.email.trim() : order.email;
    await fulfilOrder(id, order.address, { designId: design.id, email });
    return NextResponse.json({ ok: true, url: `/order/${id}` });
  } catch (e) {
    await updateOrder(id, { status: "awaiting_design" });
    throw e;
  }
}
