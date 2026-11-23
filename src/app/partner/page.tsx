import Link from "next/link";
import { redirect } from "next/navigation";
import Logo from "@/components/Logo";
import { currentPartner } from "@/lib/server/partnerAuth";
import { partnerStats } from "@/lib/server/partners";
import { publicUrl } from "@/lib/server/urls";
import { partnerLink, tradeDiscountPct } from "@/lib/partners";
import CopyLink from "./CopyLink";

export const dynamic = "force-dynamic";
export const metadata = { title: "Partner dashboard · Mapsie", robots: { index: false } };

const sym = (c: string) => ({ gbp: "£", usd: "$", aud: "A$" })[c] ?? "";
const fmt = (n: number, c: string) => `${sym(c)}${n.toFixed(2)}`;
const field = "mt-1 w-full rounded-xl border border-ink/15 px-3 py-2.5 text-sm";
const card = "rounded-3xl bg-white p-6 shadow-sm";

export default async function PartnerDashboard({ searchParams }: { searchParams: Promise<{ p?: string; msg?: string }> }) {
  const q = await searchParams;
  const s = await currentPartner(q.p);
  if (!s) redirect("/partner/signin");
  const p = s.partner;
  const st = await partnerStats(p);
  const base = publicUrl();
  const months = new Map<string, { orders: number; byCur: Record<string, number> }>();
  for (const o of st.all) {
    const m = o.createdAt.slice(0, 7);
    const row = months.get(m) ?? { orders: 0, byCur: {} };
    row.orders++;
    row.byCur[o.currency] = (row.byCur[o.currency] ?? 0) + o.commission;
    months.set(m, row);
  }
  return (
    <main className="max-w-5xl mx-auto px-4 sm:px-6 py-8 space-y-6">
      <header className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-baseline gap-3 min-w-0">
          <Link href="/" className="font-display text-3xl font-extrabold"><Logo /></Link>
          <span className="text-ink/40 font-bold">×</span>
          <span className="font-display text-xl font-extrabold truncate">{p.name}</span>
        </div>
        <div className="flex items-center gap-3 text-sm">
          {s.all.length > 1 && (
            <form className="flex gap-2">
              <select name="p" defaultValue={p.id} className="rounded-xl border border-ink/15 px-2 py-1.5">{s.all.map((x) => <option key={x.id} value={x.id}>{x.name}</option>)}</select>
              <button className="font-bold underline">Switch</button>
            </form>
          )}
          <span className="text-ink/50 hidden sm:inline">{s.email}</span>
          <form action="/api/partner/signout" method="post"><button className="font-bold underline">Sign out</button></form>
        </div>
      </header>
      {q.msg && <p className="rounded-2xl bg-sand px-4 py-3 font-bold text-sm">{q.msg}</p>}

      <section className="grid sm:grid-cols-3 gap-4">
        <div className={card}><div className="text-sm font-bold text-ink/50">Orders from your customers</div><div className="text-3xl font-extrabold mt-1">{st.orders}</div></div>
        <div className={card}>
          <div className="text-sm font-bold text-ink/50">Commission earned</div>
          {Object.entries(st.byCurrency).map(([c, v]) => <div key={c} className="text-3xl font-extrabold mt-1">{fmt(v.commission, c)}</div>)}
          {!Object.keys(st.byCurrency).length && <div className="text-3xl font-extrabold mt-1">£0.00</div>}
          <div className="text-xs text-ink/50 mt-1">{p.commissionPct}% of what customers pay for prints, excluding delivery</div>
        </div>
        <div className={card}>
          <div className="text-sm font-bold text-ink/50">Due to you</div>
          {Object.entries(st.byCurrency).map(([c, v]) => <div key={c} className="text-3xl font-extrabold mt-1">{fmt(Math.max(0, v.commission - v.paidOut), c)}</div>)}
          {!Object.keys(st.byCurrency).length && <div className="text-3xl font-extrabold mt-1">£0.00</div>}
          <div className="text-xs text-ink/50 mt-1">Paid monthly{p.payoutDetails ? ` to your ${p.payoutDetails.summary.split(" (")[0]}` : ": add your payment details below"}</div>
        </div>
      </section>

      <section className={card}>
        <h2 className="text-xl font-extrabold">Your links</h2>
        <p className="text-sm text-ink/60 mt-1">Share these with your customers: orders from them are credited to you automatically, even if they come back and order later.</p>
        <div className="mt-4 space-y-3">
          <CopyLink label="Your page (all your routes)" url={partnerLink(base, p.id)} />
          {p.trips.map((t) => <CopyLink key={t.id} label={`${t.emoji} ${t.name}`} url={partnerLink(base, p.id, t.id)} />)}
        </div>
        {p.promoCode && <p className="mt-4 text-sm">Your customers&apos; discount code: <b className="font-mono">{p.promoCode}</b> ({p.discountPct}% off). Orders using it are credited to you too.</p>}
        <p className="mt-4 text-sm text-ink/50">Need a new route set up? Email <a className="underline" href="mailto:hello@mapsie.shop">hello@mapsie.shop</a> with the stops and we&apos;ll add it.</p>
      </section>

      {st.tradeCodes.batches.length > 0 && (
        <section className={card}>
          <h2 className="text-xl font-extrabold">Gift cards and prepaid codes</h2>
          <p className="text-sm text-ink/60 mt-1">{st.tradeCodes.redeemed} of {st.tradeCodes.issued} used so far. Each code works like a gift card for any Mapsie print.</p>
          <div className="mt-4 overflow-x-auto">
            <table className="w-full text-sm">
              <tbody>
                {st.tradeCodes.batches.map((b) => {
                  const inv = (p.invoices ?? []).find((i) => i.batch === b.batch);
                  return (
                    <tr key={b.batch} className="border-t border-ink/5">
                      <td className="py-2 pr-3 whitespace-nowrap">{new Date(b.at).toLocaleDateString("en-GB")}</td>
                      <td className="py-2 pr-3 whitespace-nowrap">{b.count} × {fmt(b.value, b.currency)}</td>
                      <td className="py-2 pr-3 whitespace-nowrap">{b.redeemed} used</td>
                      <td className="py-2 pr-3 whitespace-nowrap"><a className="font-bold underline" href={`/partner/cards?p=${p.id}&batch=${b.batch}`} target="_blank" rel="noreferrer">Printable cards</a></td>
                      <td className="py-2 pr-3 whitespace-nowrap"><a className="font-bold underline" href={`/api/partner/codes?p=${p.id}&batch=${b.batch}`}>Codes (CSV)</a></td>
                      <td className="py-2 whitespace-nowrap">{inv?.url ? <a className="font-bold underline text-coral-dark" href={inv.url} target="_blank" rel="noreferrer">Invoice {fmt(inv.total, inv.currency)}</a> : <span className="text-ink/40">invoice to follow</span>}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
          <p className="mt-3 text-xs text-ink/50">Need more? Reply to your last invoice or email hello@mapsie.shop. Trade prices: {tradeDiscountPct(1)}% off, {tradeDiscountPct(10)}% off 10+, {tradeDiscountPct(50)}% off 50+.</p>
        </section>
      )}

      <section className={card}>
        <h2 className="text-xl font-extrabold">Recent orders</h2>
        <p className="text-sm text-ink/60 mt-1">For your customers&apos; privacy we show the date, amount and your commission, not names or addresses.</p>
        <div className="mt-3 overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="text-left text-xs uppercase tracking-wider text-ink/50"><tr><th className="py-2">Date</th><th>Paid</th><th>Via</th><th>Your commission</th></tr></thead>
            <tbody>
              {st.all.slice(0, 50).map((o) => (
                <tr key={`${o.createdAt}-${o.total}`} className="border-t border-ink/5">
                  <td className="py-2">{new Date(o.createdAt).toLocaleDateString("en-GB")}</td>
                  <td>{fmt(o.total, o.currency)}</td>
                  <td className="text-ink/60">{o.via === "trade" ? "prepaid code" : o.via === "code" ? "discount code" : "your link"}</td>
                  <td className="font-bold">{o.via === "trade" ? "—" : fmt(o.commission, o.currency)}</td>
                </tr>
              ))}
              {!st.all.length && <tr><td colSpan={4} className="py-6 text-center text-ink/40">No orders yet. Share your links to get started!</td></tr>}
            </tbody>
          </table>
        </div>
        {months.size > 0 && (
          <div className="mt-5">
            <h3 className="font-extrabold">By month</h3>
            <ul className="mt-2 text-sm space-y-1">
              {[...months.entries()].map(([m, r]) => (
                <li key={m}>{new Date(`${m}-01T12:00:00Z`).toLocaleDateString("en-GB", { month: "long", year: "numeric" })}: {r.orders} orders · {Object.entries(r.byCur).map(([c, v]) => fmt(v, c)).join(" + ")} commission</li>
              ))}
            </ul>
          </div>
        )}
        {(p.payouts ?? []).length > 0 && (
          <div className="mt-5">
            <h3 className="font-extrabold">Payments to you</h3>
            <ul className="mt-2 text-sm space-y-1">
              {[...(p.payouts ?? [])].reverse().map((x) => <li key={x.at}>{new Date(x.at).toLocaleDateString("en-GB")}: {fmt(x.amount, x.currency)}{x.note ? ` · ${x.note}` : ""}</li>)}
            </ul>
          </div>
        )}
      </section>

      <section id="details" className="grid md:grid-cols-2 gap-6">
        <form action="/api/partner/details" method="post" className={`${card} space-y-3`}>
          <input type="hidden" name="do" value="billing" /><input type="hidden" name="p" value={p.id} />
          <h2 className="text-xl font-extrabold">Billing details</h2>
          <p className="text-sm text-ink/60">Shown on invoices for gift cards and prepaid codes.</p>
          <label className="block text-sm font-bold">Company name<input name="company" required defaultValue={p.billing?.company ?? p.name} className={field} /></label>
          <label className="block text-sm font-bold">Address<textarea name="address" required rows={3} defaultValue={p.billing?.address} className={field} /></label>
          <label className="block text-sm font-bold">VAT number (optional)<input name="vatNumber" defaultValue={p.billing?.vatNumber} className={field} /></label>
          <label className="block text-sm font-bold">Send invoices to (optional)<input name="invoiceEmail" type="email" defaultValue={p.billing?.invoiceEmail} placeholder="accounts@company.com" className={field} /></label>
          <button className="rounded-full bg-ink text-white px-5 py-2.5 text-sm font-extrabold">Save billing details</button>
        </form>

        <form action="/api/partner/details" method="post" className={`${card} space-y-3`}>
          <input type="hidden" name="do" value="payout" /><input type="hidden" name="p" value={p.id} />
          <h2 className="text-xl font-extrabold">How we pay you</h2>
          {p.payoutDetails ? (
            <p className="text-sm">Currently: <b>{p.payoutDetails.summary}</b>. To change it, enter the new details below.</p>
          ) : (
            <p className="text-sm text-ink/60">Where we send your commission each month. Stored encrypted; we&apos;ll email you if it&apos;s ever changed.</p>
          )}
          <PayoutFields />
          <button className="rounded-full bg-ink text-white px-5 py-2.5 text-sm font-extrabold">Save payment details</button>
        </form>
      </section>
    </main>
  );
}

function PayoutFields() {
  return (
    <div className="space-y-3 text-sm">
      <fieldset className="flex flex-wrap gap-3 font-bold">
        <label className="flex items-center gap-1.5"><input type="radio" name="method" value="uk_bank" defaultChecked /> UK bank</label>
        <label className="flex items-center gap-1.5"><input type="radio" name="method" value="iban" /> IBAN</label>
        <label className="flex items-center gap-1.5"><input type="radio" name="method" value="paypal" /> PayPal</label>
      </fieldset>
      <label className="block font-bold">Name on the account<input name="accountName" autoComplete="off" className={field} /></label>
      <div className="grid grid-cols-2 gap-3">
        <label className="block font-bold">Sort code<input name="sortCode" inputMode="numeric" autoComplete="off" placeholder="12-34-56" className={field} /></label>
        <label className="block font-bold">Account number<input name="accountNumber" inputMode="numeric" autoComplete="off" placeholder="12345678" className={field} /></label>
      </div>
      <label className="block font-bold">Or IBAN<input name="iban" autoComplete="off" className={field} /></label>
      <label className="block font-bold">BIC / SWIFT (optional)<input name="bic" autoComplete="off" className={field} /></label>
      <label className="block font-bold">Or PayPal email<input name="email" type="email" autoComplete="off" className={field} /></label>
      <p className="text-xs text-ink/50">Fill in the fields for the option you chose; the others are ignored.</p>
    </div>
  );
}
