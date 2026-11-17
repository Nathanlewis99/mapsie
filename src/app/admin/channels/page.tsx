import Link from "next/link";
import Logo from "@/components/Logo";
import { getKv, listGiftCards, listOrders } from "@/lib/server/db";
import { CHANNELS, type ChannelId } from "@/lib/channels";

export const dynamic = "force-dynamic";
export const metadata = { title: "Sales by channel · Admin" };

// Rough conversion so all countries add up in pounds (good enough for comparing channels).
const TO_GBP: Record<string, number> = { gbp: 1, usd: 0.79, aud: 0.52 };
const PAID = new Set(["paid", "rendering", "ready", "submitted", "shipped", "delivered"]);

export default async function Channels({ searchParams }: { searchParams: Promise<{ days?: string }> }) {
  const days = [7, 30, 90].includes(Number((await searchParams).days)) ? Number((await searchParams).days) : 30;
  const since = new Date(Date.now() - days * 24 * 3600_000).toISOString();
  const spend = (await getKv<Record<string, number>>(`adspend:${days}`))?.value ?? {};
  const rows = new Map<ChannelId, { orders: number; revenue: number; gifts: number; giftRevenue: number }>();
  const row = (c: ChannelId) => rows.get(c) ?? rows.set(c, { orders: 0, revenue: 0, gifts: 0, giftRevenue: 0 }).get(c)!;
  for (const o of await listOrders()) {
    if (o.createdAt < since || !PAID.has(o.status) || o.reprintOf) continue;
    const r = row(o.source === "etsy" ? "etsy" : (o.channel ?? "direct"));
    r.orders++;
    r.revenue += o.total * (TO_GBP[o.currency] ?? 1);
  }
  for (const g of await listGiftCards(1000)) {
    if (g.createdAt < since || g.parentId || g.status === "pending_payment") continue;
    const r = row(g.channel ?? "direct");
    r.gifts++;
    r.giftRevenue += g.amount * (TO_GBP[g.currency] ?? 1);
  }
  const gbp = (n: number) => `£${n.toFixed(n >= 100 ? 0 : 2)}`;
  const totals = [...rows.values()].reduce((t, r) => ({ sales: t.sales + r.orders + r.gifts, revenue: t.revenue + r.revenue + r.giftRevenue }), { sales: 0, revenue: 0 });
  const totalSpend = Object.values(spend).reduce((a, b) => a + b, 0);
  return (
    <main className="max-w-6xl mx-auto px-6 py-10 space-y-6">
      <div>
        <Link href="/" className="font-display text-2xl font-extrabold"><Logo /></Link>
        <div className="flex items-baseline gap-4 mt-2">
          <h1 className="text-3xl font-extrabold">Sales by channel</h1>
          <Link href="/admin" className="text-sm font-bold text-coral-dark">← All orders</Link>
        </div>
        <p className="text-sm text-ink/60 mt-1">
          Which channel brought each sale, from the visit that placed it (UTM tags, ad click ids, referrer). Enter what you spent on each channel for the
          period to see cost per sale and return on ad spend. Revenue in pounds (other currencies converted roughly). Tag ad links with utm_source / utm_medium=paid / utm_campaign.
        </p>
        <div className="flex gap-2 mt-3">
          {[7, 30, 90].map((d) => (
            <Link key={d} href={`/admin/channels?days=${d}`} className={`rounded-full px-4 py-1.5 text-sm font-bold ${d === days ? "bg-ink text-white" : "bg-white border border-ink/10"}`}>Last {d} days</Link>
          ))}
        </div>
      </div>
      <form action="/api/admin/channels" method="post" className="rounded-3xl bg-white p-4 shadow-sm overflow-x-auto">
        <input type="hidden" name="days" value={days} />
        <table className="w-full text-sm">
          <thead className="text-left text-xs uppercase tracking-wider text-ink/50">
            <tr>{["Channel", "Orders", "Gift cards", "Revenue", "Avg order", "Ad spend (£)", "Cost per sale", "ROAS"].map((h) => <th key={h} className="px-2 py-2">{h}</th>)}</tr>
          </thead>
          <tbody>
            {CHANNELS.map((c) => {
              const r = rows.get(c.id) ?? { orders: 0, revenue: 0, gifts: 0, giftRevenue: 0 };
              const sales = r.orders + r.gifts;
              const revenue = r.revenue + r.giftRevenue;
              const s = spend[c.id] ?? 0;
              return (
                <tr key={c.id} className="border-t border-ink/5">
                  <td className="px-2 py-2 font-bold">{c.label}</td>
                  <td className="px-2 py-2">{r.orders}</td>
                  <td className="px-2 py-2">{r.gifts}</td>
                  <td className="px-2 py-2">{gbp(revenue)}</td>
                  <td className="px-2 py-2">{sales ? gbp(revenue / sales) : "–"}</td>
                  <td className="px-2 py-2"><input name={c.id} defaultValue={s || ""} inputMode="decimal" className="w-24 rounded-lg border border-ink/15 px-2 py-1" /></td>
                  <td className="px-2 py-2">{s && sales ? gbp(s / sales) : "–"}</td>
                  <td className={`px-2 py-2 font-bold ${s ? (revenue / s >= 2.5 ? "text-sea" : revenue / s < 1.5 ? "text-coral-dark" : "") : ""}`}>{s ? `${(revenue / s).toFixed(1)}×` : "–"}</td>
                </tr>
              );
            })}
            <tr className="border-t-2 border-ink/10 font-extrabold">
              <td className="px-2 py-2">Total</td>
              <td className="px-2 py-2" colSpan={2}>{totals.sales} sales</td>
              <td className="px-2 py-2">{gbp(totals.revenue)}</td>
              <td className="px-2 py-2">{totals.sales ? gbp(totals.revenue / totals.sales) : "–"}</td>
              <td className="px-2 py-2">{totalSpend ? gbp(totalSpend) : ""}</td>
              <td className="px-2 py-2" />
              <td className="px-2 py-2">{totalSpend ? `${(totals.revenue / totalSpend).toFixed(1)}×` : "–"}</td>
            </tr>
          </tbody>
        </table>
        <div className="flex justify-between items-center mt-3 gap-4">
          <p className="text-xs text-ink/50">ROAS = revenue ÷ ad spend. With Prodigi and fees taking roughly half of each sale, aim for 2.5× or more to profit (green); under 1.5× loses money (red).</p>
          <button className="rounded-full bg-ink text-white px-4 py-2 text-sm font-bold shrink-0">Save spend</button>
        </div>
      </form>
    </main>
  );
}
