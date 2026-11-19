import Link from "next/link";
import Logo from "@/components/Logo";
import { getKv, listAdSpend, listGiftCards, listOrders } from "@/lib/server/db";
import { adsImportKey, pinterestTokenStatus, refreshAdSpend } from "@/lib/server/adSpend";
import { GOOGLE_ADS_SCRIPT } from "@/lib/server/googleAdsScript";
import { gadsConnection, gadsMissing, gadsRedirectUri } from "@/lib/server/googleAds";
import { CHANNELS, type ChannelId } from "@/lib/channels";

export const dynamic = "force-dynamic";
export const metadata = { title: "Sales by channel · Admin" };

// Rough conversion so all countries add up in pounds (good enough for comparing channels).
const TO_GBP: Record<string, number> = { gbp: 1, usd: 0.79, aud: 0.52 };
const PAID = new Set(["paid", "rendering", "ready", "submitted", "shipped", "delivered"]);

export default async function Channels({ searchParams }: { searchParams: Promise<{ days?: string; google?: string }> }) {
  const sp = await searchParams;
  const days = [7, 30, 90].includes(Number(sp.days)) ? Number(sp.days) : 30;
  const gads = await gadsConnection();
  const gadsNeeds = gadsMissing();
  const since = new Date(Date.now() - days * 24 * 3600_000).toISOString();
  const manual = (await getKv<Record<string, number>>(`adspend:${days}`))?.value ?? {};
  // Imported spend (Meta / Pinterest APIs, Google Ads Script) wins over typed-in numbers.
  const sync = await refreshAdSpend();
  const pin = await pinterestTokenStatus();
  const imported: Record<string, { spend: number; purchases: number; value: number; days: number }> = {};
  for (const d of await listAdSpend(since.slice(0, 10))) {
    const t = (imported[d.channel] ??= { spend: 0, purchases: 0, value: 0, days: 0 });
    t.spend += d.spend;
    t.purchases += d.platformPurchases ?? 0;
    t.value += d.platformValue ?? 0;
    t.days++;
  }
  const spend: Record<string, number> = { ...manual };
  for (const [c, t] of Object.entries(imported)) spend[c] = Math.round(t.spend * 100) / 100;
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
        {(pin.level === "soon" || pin.level === "expired") && (
          <div className={`mt-3 rounded-2xl px-4 py-3 text-sm font-bold ${pin.level === "expired" ? "bg-coral/15 text-coral-dark" : "bg-amber-100 text-amber-900"}`}>
            {pin.level === "expired"
              ? "⚠️ The Pinterest reporting token has expired, so Pinterest spend isn't importing."
              : `⏳ The Pinterest reporting token expires in ${pin.daysLeft} day${pin.daysLeft === 1 ? "" : "s"} (around ${pin.expiresOn}).`}{" "}
            <span className="font-normal">Generate a new one at developers.pinterest.com/apps (scopes ads:read and user_accounts:read) and replace PINTEREST_ADS_TOKEN on Render.</span>
          </div>
        )}
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
            <tr>{["Channel", "Orders", "Gift cards", "Revenue", "Avg order", "Ad spend (£)", "Cost per sale", "ROAS", "Platform says"].map((h) => <th key={h} className="px-2 py-2">{h}</th>)}</tr>
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
                  <td className="px-2 py-2">
                    {imported[c.id] ? (
                      <span title="Imported automatically">{gbp(s)} <span className="text-xs text-sea font-bold">auto</span></span>
                    ) : (
                      <input name={c.id} defaultValue={s || ""} inputMode="decimal" className="w-24 rounded-lg border border-ink/15 px-2 py-1" />
                    )}
                  </td>
                  <td className="px-2 py-2">{s && sales ? gbp(s / sales) : "–"}</td>
                  <td className={`px-2 py-2 font-bold ${s ? (revenue / s >= 2.5 ? "text-sea" : revenue / s < 1.5 ? "text-coral-dark" : "") : ""}`}>{s ? `${(revenue / s).toFixed(1)}×` : "–"}</td>
                  <td className="px-2 py-2 text-xs text-ink/50">{imported[c.id] ? `${Math.round(imported[c.id].purchases)} sales, ${gbp(imported[c.id].value)}` : ""}</td>
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
              <td />
            </tr>
          </tbody>
        </table>
        <div className="flex justify-between items-center mt-3 gap-4">
          <p className="text-xs text-ink/50">ROAS = revenue ÷ ad spend. With Prodigi and fees taking roughly half of each sale, aim for 2.5× or more to profit (green); under 1.5× loses money (red).</p>
          <button className="rounded-full bg-ink text-white px-4 py-2 text-sm font-bold shrink-0">Save spend</button>
        </div>
      </form>
      <section className="rounded-3xl bg-white p-5 shadow-sm text-sm space-y-2">
        <h2 className="text-lg font-extrabold">Automatic spend import</h2>
        <p className="text-ink/60">
          Last checked {sync.at ? new Date(sync.at).toLocaleString("en-GB") : "never"} (refreshes hourly when you open this page). “Platform says” is what the ad
          platform claims; the Orders column is what we saw arrive from its links. A big gap usually means the platform is counting view-throughs.
        </p>
        <ul className="list-disc pl-5 text-ink/70">
          <li>Meta: {process.env.META_ADS_TOKEN && process.env.META_AD_ACCOUNT_ID ? "connected" : "add META_ADS_TOKEN and META_AD_ACCOUNT_ID on Render"}</li>
          <li>Pinterest: {process.env.PINTEREST_ADS_TOKEN && process.env.PINTEREST_AD_ACCOUNT_ID ? `connected (token ${pin.level === "expired" ? "expired" : `good for about ${pin.daysLeft} more days`})` : "add PINTEREST_ADS_TOKEN (ads:read) on Render"}</li>
          <li>Google Ads: {imported.google_ads ? "receiving data from the script" : "install the Google Ads Script below"}</li>
        </ul>
        {sync.errors.length > 0 && <p className="text-coral-dark font-bold">{sync.errors.join(" · ")}</p>}
        <div className="rounded-2xl bg-sand/50 p-3 space-y-1">
          <div className="font-bold">Google Ads API (status checks and approved changes)</div>
          {sp.google === "connected" && <p className="text-green-700 font-bold">Connected.</p>}
          {sp.google === "failed" && <p className="text-coral-dark font-bold">Connecting didn&apos;t work. Check the client ID, secret and redirect address below, then try again.</p>}
          {sp.google === "cancelled" && <p className="text-coral-dark font-bold">Cancelled on Google&apos;s screen.</p>}
          {sp.google === "missing" && <p className="text-coral-dark font-bold">Add GOOGLE_ADS_CLIENT_ID and GOOGLE_ADS_CLIENT_SECRET on Render first.</p>}
          <p className="text-ink/70">{gads.connected ? (gads.via === "render" ? "Connected (refresh token on Render)." : `Connected${gads.email ? ` as ${gads.email}` : ""} on ${new Date(gads.at!).toLocaleDateString("en-GB")}.`) : "Not connected: add GOOGLE_ADS_REFRESH_TOKEN on Render, or connect below with a Web OAuth client."}{gadsNeeds.length > 0 && ` Still needed on Render: ${gadsNeeds.join(", ")}.`}</p>
          <p className="text-ink/60">The OAuth client&apos;s authorised redirect URI must be <code className="select-all font-mono bg-white px-1 rounded">{gadsRedirectUri()}</code></p>
          <a href="/api/admin/google-ads/connect" className="inline-block rounded-full bg-ink text-white px-4 py-2 font-bold">{gads.connected ? "Reconnect Google Ads" : "Connect Google Ads"}</a>
        </div>
        <details>
          <summary className="cursor-pointer font-bold">Google Ads Script (paste into Google Ads → Tools → Bulk actions → Scripts, run once, schedule daily)</summary>
          <p className="mt-2 text-ink/60">Your key: <code className="select-all font-mono bg-sand px-2 py-0.5 rounded">{adsImportKey()}</code> (keep it private: it lets the script report spend).</p>
          <pre className="mt-2 overflow-x-auto rounded-2xl bg-ink text-white p-4 text-xs">{GOOGLE_ADS_SCRIPT.replace("PASTE-KEY-FROM-ADMIN", adsImportKey())}</pre>
        </details>
      </section>
    </main>
  );
}
