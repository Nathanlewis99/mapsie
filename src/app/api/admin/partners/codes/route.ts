import { listGiftCards } from "@/lib/server/db";
import { getPartner } from "@/lib/server/partners";
import { giftCardUrl } from "@/lib/server/giftcards";

// Admin only (middleware): a batch of trade codes as a CSV, to send to the partner.
export async function GET(req: Request) {
  const u = new URL(req.url);
  const p = await getPartner(u.searchParams.get("id") ?? "");
  const batch = u.searchParams.get("batch") ?? "";
  if (!p) return new Response("Not found", { status: 404 });
  const cards = (await listGiftCards(5000)).filter((g) => g.partnerId === p.id && g.tradeBatch === batch).sort((a, b) => a.id.localeCompare(b.id, undefined, { numeric: true }));
  const q = (s: string) => `"${s.replace(/"/g, '""')}"`;
  const rows = [["code", "value", "currency", "valid_until", "printable_card", "status"], ...cards.map((g) => [g.code ?? "", String(g.amount), g.currency.toUpperCase(), (g.expiresAt ?? "").slice(0, 10), giftCardUrl(g.id), g.status])];
  return new Response(rows.map((r) => r.map(q).join(",")).join("\n"), {
    headers: { "content-type": "text/csv; charset=utf-8", "content-disposition": `attachment; filename="mapsie-codes-${p.id}-${batch}.csv"` },
  });
}
