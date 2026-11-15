import { NextResponse } from "next/server";
import { refund, reprint, setTicketStatus, staffReply } from "@/lib/server/support";
import { publicUrl } from "@/lib/server/urls";
import type { TicketStatus } from "@/lib/server/db";

const STATUSES: TicketStatus[] = ["open", "waiting", "resolved"];

// Admin only (middleware). Form posts from /admin/support/[id].
export async function POST(req: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const f = await req.formData();
  const action = String(f.get("action"));
  const status = STATUSES.includes(f.get("status") as TicketStatus) ? (f.get("status") as TicketStatus) : "waiting";
  let note = "";
  try {
    if (action === "reply") {
      await staffReply(id, String(f.get("text") ?? "").slice(0, 10000), status);
      note = "sent";
    } else if (action === "status") {
      await setTicketStatus(id, status);
      note = "status";
    } else if (action === "reprint") {
      note = `reprint=${await reprint(id)}`;
    } else if (action === "refund") {
      await refund(id);
      note = "refunded";
    }
  } catch (e) {
    note = `error=${encodeURIComponent(String((e as Error).message ?? e).slice(0, 300))}`;
  }
  return NextResponse.redirect(`${publicUrl()}/admin/support/${id}?${note}`, { status: 303 });
}
