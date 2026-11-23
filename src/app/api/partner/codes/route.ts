import { listGiftCards } from "@/lib/server/db";
import { currentPartner } from "@/lib/server/partnerAuth";
import { giftCardUrl } from "@/lib/server/giftcards";

// Partner dashboard: one of their trade code batches as a CSV.
export async function GET(req: Request) {
  const u = new URL(req.url);
  const s = await currentPartner(u.searchParams.get("p"));
  if (!s) return new Response("Please sign in", { status: 401 });
  const batch = u.searchParams.get("batch") ?? "";
  const cards = (await listGiftCards(5000)).filter((g) => g.partnerId === s.partner.id && g.tradeBatch === batch).sort((a, b) => a.id.localeCompare(b.id, undefined, { numeric: true }));
  if (!cards.length) return new Response("Not found", { status: 404 });
  const q = (x: string) => `"${x.replace(/"/g, '""')}"`;
  const rows = [["code", "value", "currency", "valid_until", "printable_card", "status"], ...cards.map((g) => [g.code ?? "", String(g.amount), g.currency.toUpperCase(), (g.expiresAt ?? "").slice(0, 10), giftCardUrl(g.id), g.status === "redeemed" ? "used" : "unused"])];
  return new Response(rows.map((r) => r.map(q).join(",")).join("\n"), {
    headers: { "content-type": "text/csv; charset=utf-8", "content-disposition": `attachment; filename="mapsie-codes-${s.partner.id}-${batch}.csv"` },
  });
}
