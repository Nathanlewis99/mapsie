import Link from "next/link";
import Logo from "@/components/Logo";
import { listGiftCards, listOrders } from "@/lib/server/db";
import { listPartners, partnerStats } from "@/lib/server/partners";
import { publicUrl } from "@/lib/server/urls";
import { PARTNER_KINDS, partnerLink, tradeDiscountPct, tradePrice, type Partner } from "@/lib/partners";
import { PRESETS } from "@/lib/themes";
import { REGIONS } from "@/lib/products";

export const dynamic = "force-dynamic";
export const metadata = { title: "Partners · Admin" };

const sym = (c: string) => ({ gbp: "£", usd: "$", aud: "A$" })[c] ?? "";
const fmt = (n: number, c: string) => `${sym(c)}${n.toFixed(2)}`;
const input = "rounded-xl border border-ink/15 px-3 py-2 text-sm";
const btn = "rounded-full bg-ink text-white px-4 py-2 text-sm font-extrabold";

export default async function PartnersAdmin({ searchParams }: { searchParams: Promise<{ p?: string; msg?: string }> }) {
  const { p: openId, msg } = await searchParams;
  const [partners, orders, cards] = await Promise.all([listPartners(), listOrders(), listGiftCards(5000)]);
  const stats = new Map(await Promise.all(partners.map(async (p) => [p.id, await partnerStats(p, orders, cards)] as const)));
  const open = partners.find((p) => p.id === openId);
  const base = publicUrl();
  return (
    <main className="max-w-5xl mx-auto px-6 py-10 space-y-6">
      <div>
        <Link href="/" className="font-display text-2xl font-extrabold"><Logo /></Link>
        <div className="flex items-baseline gap-4 mt-2">
          <h1 className="text-3xl font-extrabold">Partners</h1>
          <Link href="/admin" className="text-sm font-bold text-coral-dark">← All orders</Link>
          <Link href="/partners" className="text-sm font-bold text-coral-dark">Public partner page →</Link>
        </div>
        <p className="text-sm text-ink/60 mt-1 max-w-3xl">
          Tour operators, events, wedding registries and corporate gifting. Each partner gets a page at {base.replace(/^https?:\/\//, "")}/with/&lt;id&gt; with their routes
          ready to personalise. Orders from it (or with their discount code) earn them commission; prepaid trade codes are bought at a discount and work like gift cards.
        </p>
        {msg && <p className="mt-3 rounded-2xl bg-sand px-4 py-3 font-bold text-sm">{msg}</p>}
      </div>

      <div className="rounded-3xl bg-white p-4 shadow-sm overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="text-left text-xs uppercase tracking-wider text-ink/50">
            <tr>{["Partner", "Type", "Orders", "Sales", "Commission owed", "Trade codes", ""].map((h) => <th key={h} className="px-2 py-2">{h}</th>)}</tr>
          </thead>
          <tbody>
            {partners.map((p) => {
              const s = stats.get(p.id)!;
              const cur = Object.entries(s.byCurrency);
              return (
                <tr key={p.id} className="border-t border-ink/5 align-top">
                  <td className="px-2 py-2 font-bold">{p.name}{!p.active && <span className="ml-2 text-xs text-ink/40">paused</span>}<div className="text-xs font-mono text-ink/40">{p.id}</div></td>
                  <td className="px-2 py-2">{PARTNER_KINDS.find((k) => k.id === p.kind)?.label}</td>
                  <td className="px-2 py-2">{s.orders}</td>
                  <td className="px-2 py-2">{cur.map(([c, v]) => <div key={c}>{fmt(v.sales, c)}</div>)}</td>
                  <td className="px-2 py-2 font-bold">{cur.map(([c, v]) => <div key={c}>{fmt(v.commission - v.paidOut, c)}</div>)}</td>
                  <td className="px-2 py-2">{s.tradeCodes.issued ? `${s.tradeCodes.redeemed}/${s.tradeCodes.issued} used` : "—"}</td>
                  <td className="px-2 py-2"><Link className="font-bold text-coral-dark" href={`/admin/partners?p=${p.id}`}>Open →</Link></td>
                </tr>
              );
            })}
            {!partners.length && <tr><td colSpan={7} className="px-2 py-8 text-center text-ink/40">No partners yet: add the first one below.</td></tr>}
          </tbody>
        </table>
      </div>

      <PartnerForm p={open} />
      {open && <PartnerDetail p={open} base={base} stats={stats.get(open.id)!} />}
    </main>
  );
}

function PartnerForm({ p }: { p?: Partner }) {
  return (
    <form action="/api/admin/partners" method="post" className="rounded-3xl bg-white p-5 shadow-sm space-y-3">
      <h2 className="text-xl font-extrabold">{p ? `Edit ${p.name}` : "Add a partner"}</h2>
      <input type="hidden" name="do" value="save" />
      {p && <input type="hidden" name="id" value={p.id} />}
      <div className="grid sm:grid-cols-2 gap-3">
        <label className="grid gap-1 text-sm font-bold">Name<input name="name" required defaultValue={p?.name} className={input} /></label>
        <label className="grid gap-1 text-sm font-bold">Type
          <select name="kind" defaultValue={p?.kind ?? "travel"} className={input}>{PARTNER_KINDS.map((k) => <option key={k.id} value={k.id}>{k.label}</option>)}</select>
        </label>
        <label className="grid gap-1 text-sm font-bold">Contact email (for invoices)<input name="contactEmail" type="email" defaultValue={p?.contactEmail} className={input} /></label>
        <label className="grid gap-1 text-sm font-bold">Commission %<input name="commissionPct" type="number" min={0} max={50} step={0.5} defaultValue={p?.commissionPct ?? 10} className={input} /></label>
        <label className="grid gap-1 text-sm font-bold">Their customers are mostly in
          <select name="region" defaultValue={p?.region ?? ""} className={input}><option value="">Detect</option>{REGIONS.map((r) => <option key={r.id} value={r.id}>{r.label}</option>)}</select>
        </label>
        <label className="grid gap-1 text-sm font-bold">Headline on their page (optional)<input name="welcome" defaultValue={p?.welcome} placeholder="Your Coast to Coast ride, as a map for your wall" className={input} /></label>
      </div>
      <label className="grid gap-1 text-sm font-bold">Notes (private)<textarea name="notes" rows={2} defaultValue={p?.notes} className={input} /></label>
      <label className="flex items-center gap-2 text-sm font-bold"><input type="checkbox" name="active" defaultChecked={p?.active ?? true} /> Live (their page and links work)</label>
      <button className={btn}>{p ? "Save" : "Add partner"}</button>
    </form>
  );
}

function PartnerDetail({ p, base, stats }: { p: Partner; base: string; stats: Awaited<ReturnType<typeof partnerStats>> }) {
  return (
    <div className="space-y-6">
      <section className="rounded-3xl bg-white p-5 shadow-sm space-y-3">
        <h2 className="text-xl font-extrabold">Links to give {p.name}</h2>
        <p className="text-sm text-ink/60">Their page: <a className="font-mono underline break-all" href={partnerLink(base, p.id)} target="_blank" rel="noreferrer">{partnerLink(base, p.id)}</a></p>
        <ul className="text-sm space-y-1">
          {p.trips.map((t) => (
            <li key={t.id} className="flex flex-wrap items-center gap-2">
              <span>{t.emoji} <b>{t.name}</b>: </span>
              <a className="font-mono underline break-all" href={partnerLink(base, p.id, t.id)} target="_blank" rel="noreferrer">{partnerLink(base, p.id, t.id)}</a>
              <form action="/api/admin/partners" method="post">
                <input type="hidden" name="do" value="removeTrip" /><input type="hidden" name="id" value={p.id} /><input type="hidden" name="trip" value={t.id} />
                <button className="text-xs font-bold text-ink/40 underline">remove</button>
              </form>
            </li>
          ))}
          {!p.trips.length && <li className="text-ink/40">No routes yet: their customers start from a blank map. Add one below.</li>}
        </ul>
      </section>

      <form action="/api/admin/partners" method="post" className="rounded-3xl bg-white p-5 shadow-sm space-y-3">
        <h2 className="text-xl font-extrabold">Add a route</h2>
        <input type="hidden" name="do" value="addTrip" /><input type="hidden" name="id" value={p.id} />
        <label className="grid gap-1 text-sm font-bold">Stops, in order, separated by ; (add how they got there in brackets: car, train, plane, boat, bus, walk)
          <textarea name="stops" rows={3} required placeholder="Land's End; Okehampton (car); Bristol (car); Ludlow (car); ... ; John o' Groats (car)" className={input} />
        </label>
        <div className="grid sm:grid-cols-3 gap-3">
          <label className="grid gap-1 text-sm font-bold">Route name<input name="tripName" placeholder="LEJOG 2027" className={input} /></label>
          <label className="grid gap-1 text-sm font-bold">Emoji<input name="emoji" placeholder="🚴" className={input} /></label>
          <label className="grid gap-1 text-sm font-bold">Map style
            <select name="preset" defaultValue="vintage" className={input}>{PRESETS.map((x) => <option key={x.id} value={x.id}>{x.name}</option>)}</select>
          </label>
          <label className="grid gap-1 text-sm font-bold">Title<input name="title" placeholder="{name}'s Land's End to John o' Groats" className={input} /></label>
          <label className="grid gap-1 text-sm font-bold sm:col-span-2">Subtitle<input name="subtitle" placeholder="874 miles · {detail}" className={input} /></label>
          <label className="grid gap-1 text-sm font-bold">Ask for a name? (label)<input name="askName" placeholder="Rider's name" className={input} /></label>
          <label className="grid gap-1 text-sm font-bold">Ask for a detail? (label)<input name="askDetail" placeholder="Finish date or time" className={input} /></label>
        </div>
        <p className="text-xs text-ink/50">{"{name}"} and {"{detail}"} in the title or subtitle are filled from those boxes. Customers can still change everything in the designer.</p>
        <button className={btn}>Add route</button>
      </form>

      <div className="grid md:grid-cols-2 gap-6">
        <form action="/api/admin/partners" method="post" className="rounded-3xl bg-white p-5 shadow-sm space-y-3">
          <h2 className="text-xl font-extrabold">Customer discount code</h2>
          <input type="hidden" name="do" value="code" /><input type="hidden" name="id" value={p.id} />
          {p.promoCode ? (
            <p className="text-sm">Code <b className="font-mono">{p.promoCode}</b> gives {p.discountPct}% off. Orders that use it are credited to {p.name}.</p>
          ) : (
            <>
              <p className="text-sm text-ink/60">Optional: a code their customers use at checkout (made in Stripe). It also credits the order to them if they didn&apos;t use the link.</p>
              <div className="flex gap-2"><input name="code" placeholder="COASTRIDE10" className={`${input} flex-1`} /><input name="pct" type="number" defaultValue={10} min={1} max={50} className={`${input} w-20`} /><span className="self-center text-sm">%</span></div>
              <button className={btn}>Create code</button>
            </>
          )}
        </form>

        <form action="/api/admin/partners" method="post" className="rounded-3xl bg-white p-5 shadow-sm space-y-3">
          <h2 className="text-xl font-extrabold">Prepaid trade codes</h2>
          <input type="hidden" name="do" value="trade" /><input type="hidden" name="id" value={p.id} />
          <p className="text-sm text-ink/60">Codes they give away (finisher prints, thank-you gifts, client gifts). Each works like a gift card. Trade price: {tradeDiscountPct(1)}% off, {tradeDiscountPct(10)}% off for 10+, {tradeDiscountPct(50)}% off for 50+ (e.g. 20 × £69 codes = {fmt(tradePrice(69, 20) * 20, "gbp")}).</p>
          <div className="flex flex-wrap gap-2">
            <input name="count" type="number" min={1} max={500} defaultValue={10} className={`${input} w-24`} />
            <span className="self-center text-sm">codes worth</span>
            <input name="value" type="number" min={5} max={500} defaultValue={69} className={`${input} w-24`} />
            <select name="region" defaultValue={p.region ?? "GB"} className={input}>{REGIONS.map((r) => <option key={r.id} value={r.id}>{r.symbol} {r.label}</option>)}</select>
          </div>
          <button className={btn}>Make codes</button>
        </form>
      </div>

      {stats.tradeCodes.batches.length > 0 && (
        <section className="rounded-3xl bg-white p-5 shadow-sm">
          <h2 className="text-xl font-extrabold mb-2">Trade code batches</h2>
          <table className="w-full text-sm">
            <tbody>
              {stats.tradeCodes.batches.map((b) => (
                <tr key={b.batch} className="border-t border-ink/5">
                  <td className="py-2">{new Date(b.at).toLocaleDateString("en-GB")}</td>
                  <td className="py-2">{b.count} × {fmt(b.value, b.currency)}</td>
                  <td className="py-2">{b.redeemed} used</td>
                  <td className="py-2">trade total {fmt(tradePrice(b.value, b.count) * b.count, b.currency)}</td>
                  <td className="py-2"><a className="font-bold underline" href={`/api/admin/partners/codes?id=${p.id}&batch=${b.batch}`}>Download CSV</a></td>
                  <td className="py-2">
                    <form action="/api/admin/partners" method="post">
                      <input type="hidden" name="do" value="invoice" /><input type="hidden" name="id" value={p.id} /><input type="hidden" name="batch" value={b.batch} />
                      <button className="text-xs font-bold underline text-coral-dark" disabled={!p.contactEmail} title={p.contactEmail ? `Stripe emails an invoice to ${p.contactEmail}` : "Add a contact email first"}>Send Stripe invoice</button>
                    </form>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      )}

      <section className="rounded-3xl bg-white p-5 shadow-sm space-y-3">
        <h2 className="text-xl font-extrabold">Commission</h2>
        {Object.entries(stats.byCurrency).map(([c, v]) => (
          <p key={c} className="text-sm">{c.toUpperCase()}: sales {fmt(v.sales, c)} · earned {fmt(v.commission, c)} · paid {fmt(v.paidOut, c)} · <b>owed {fmt(v.commission - v.paidOut, c)}</b></p>
        ))}
        {!Object.keys(stats.byCurrency).length && <p className="text-sm text-ink/40">No orders yet.</p>}
        <form action="/api/admin/partners" method="post" className="flex flex-wrap gap-2 items-center">
          <input type="hidden" name="do" value="payout" /><input type="hidden" name="id" value={p.id} />
          <span className="text-sm font-bold">Record a payment to them:</span>
          <input name="amount" type="number" step="0.01" min={0} className={`${input} w-28`} />
          <select name="currency" className={input}><option value="gbp">GBP</option><option value="usd">USD</option><option value="aud">AUD</option></select>
          <input name="note" placeholder="e.g. bank transfer, Jan 2027" className={`${input} flex-1 min-w-[10rem]`} />
          <button className={btn}>Record</button>
        </form>
        {stats.recent.length > 0 && (
          <table className="w-full text-sm mt-2">
            <tbody>
              {stats.recent.map((o) => (
                <tr key={o.id} className="border-t border-ink/5">
                  <td className="py-1.5">{new Date(o.createdAt).toLocaleDateString("en-GB")}</td>
                  <td className="py-1.5"><Link className="underline" href={`/order/${o.id}`}>{o.id}</Link></td>
                  <td className="py-1.5">{fmt(o.total, o.currency)}</td>
                  <td className="py-1.5 text-ink/50">via {o.partnerVia ?? "link"}</td>
                  <td className="py-1.5">{o.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>
    </div>
  );
}
