import { NextResponse } from "next/server";
import { disconnectEtsy, syncEtsyOrders } from "@/lib/server/etsy";
import { getOrder } from "@/lib/server/db";
import { sendEtsyDesignEmail } from "@/lib/server/email";
import { publicUrl } from "@/lib/server/urls";

// Admin only (middleware). Form posts from /admin/etsy.
export async function POST(req: Request) {
  const f = await req.formData();
  const action = String(f.get("action"));
  let q = "";
  try {
    if (action === "sync") q = `synced=${await syncEtsyOrders()}`;
    if (action === "disconnect") {
      await disconnectEtsy();
      q = "disconnected=1";
    }
    if (action === "resend") {
      const o = await getOrder(String(f.get("orderId")));
      if (o) await sendEtsyDesignEmail(o, "invite", true);
      q = "resent=1";
    }
  } catch (e) {
    q = `error=${encodeURIComponent(String(e).slice(0, 200))}`;
  }
  return NextResponse.redirect(`${publicUrl()}/admin/etsy?${q}`, { status: 303 });
}
