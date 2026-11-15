import { getSupportFile } from "@/lib/server/db";
import { ticketTokenValid } from "@/lib/server/support";
import { getSession } from "@/lib/server/auth";
import { adminMfaValid } from "@/lib/session";

/** A support photo: for the customer (with their ticket link's token) or an admin. */
export async function GET(req: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const f = await getSupportFile(id);
  const k = new URL(req.url).searchParams.get("k");
  if (!f || !(ticketTokenValid(f.ticketId, k) || adminMfaValid(await getSession()))) return new Response("Not found", { status: 404 });
  return new Response(Buffer.from(f.data, "base64"), {
    headers: { "content-type": f.mime, "cache-control": "private, max-age=86400", "x-content-type-options": "nosniff" },
  });
}
