import { NextResponse } from "next/server";
import { customerReply, ticketTokenValid } from "@/lib/server/support";

/** The customer adds a message (and photos) on their support page. */
export async function POST(req: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const b = (await req.json().catch(() => ({}))) as { k?: string; text?: string; photos?: unknown };
  if (!ticketTokenValid(id, b.k)) return NextResponse.json({ error: "This link isn't valid." }, { status: 404 });
  const text = String(b.text ?? "").trim().slice(0, 5000);
  if (!text && !(Array.isArray(b.photos) && b.photos.length)) return NextResponse.json({ error: "Write a message or add a photo." }, { status: 400 });
  await customerReply(id, text, b.photos);
  return NextResponse.json({ ok: true });
}
