import Link from "next/link";
import Logo from "@/components/Logo";
import { getCosts, marginTable } from "@/lib/server/prodigiCosts";
import { REGIONS, getRegion, type RegionId } from "@/lib/products";
import RefreshButton from "./RefreshButton";

export const dynamic = "force-dynamic";

const f = (n: number, sym: string) => `${n < 0 ? "−" : ""}${sym}${Math.abs(n).toFixed(2)}`;

export default async function Costs({ searchParams }: { searchParams: Promise<{ region?: string; vat?: string }> }) {
  const sp = await searchParams;
  const region = getRegion(sp.region).id as RegionId;
  const vat = sp.vat === "1";
  const sym = getRegion(region).symbol;
  const costs = await getCosts();
  const table = costs ? marginTable(costs.value, region) : [];
  return (
    <main className="max-w-6xl mx-auto px-6 py-10 space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <Link href="/" className="font-display text-2xl font-extrabold"><Logo /></Link>
          <h1 className="text-3xl font-extrabold mt-2">Costs &amp; margins</h1>
          <p className="text-sm text-ink/60 mt-1">
            Our price vs Prodigi&apos;s cost (product + standard shipping, ex VAT) and an estimated Stripe fee.
            {costs ? ` Prodigi prices from ${new Date(costs.updatedAt).toLocaleString("en-GB")}.` : " No Prodigi prices yet: press Refresh."}
          </p>
          <Link href="/admin" className="text-sm font-bold text-coral-dark">← Orders</Link>
        </div>
        <RefreshButton />
      </div>
      <div className="flex flex-wrap gap-2 text-sm font-bold">
        {REGIONS.map((r) => (
          <Link key={r.id} href={`?region=${r.id}${vat ? "&vat=1" : ""}`} className={`rounded-full px-4 py-1.5 border-2 ${r.id === region ? "border-coral bg-white" : "border-ink/10"}`}>
            {r.flag} {r.label}
          </Link>
        ))}
        {region === "GB" && (
          <Link href={`?region=GB${vat ? "" : "&vat=1"}`} className={`rounded-full px-4 py-1.5 border-2 ${vat ? "border-coral bg-white" : "border-ink/10"}`}>
            {vat ? "☑" : "☐"} We&apos;re VAT registered (20% of UK prices goes to HMRC)
          </Link>
        )}
      </div>
      {table.map((t) => (
        <div key={t.product} className="rounded-2xl bg-white shadow-sm overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="text-left text-ink/50">
              <tr>
                <th className="px-4 py-2 w-1/3">{t.product}</th>
                <th className="px-3 py-2 text-right">Our price</th>
                <th className="px-3 py-2 text-right">Prodigi cost</th>
                <th className="px-3 py-2 text-right">Card fee</th>
                {vat && <th className="px-3 py-2 text-right">VAT</th>}
                <th className="px-3 py-2 text-right">Profit</th>
                <th className="px-3 py-2 text-right">Margin</th>
                <th className="px-3 py-2 text-right">Markup</th>
              </tr>
            </thead>
            <tbody>
              {t.rows.map((r) => {
                const profit = r.margin === null ? null : r.margin - (vat ? r.vat : 0);
                const pct = profit === null ? null : (profit / r.price) * 100;
                return (
                  <tr key={r.label} className="border-t border-ink/5">
                    <td className="px-4 py-2 font-bold">{r.label}</td>
                    <td className="px-3 py-2 text-right">{f(r.price, sym)}</td>
                    <td className="px-3 py-2 text-right">{r.cost === null ? "not found" : f(r.cost, sym)}</td>
                    <td className="px-3 py-2 text-right">{f(r.fee, sym)}</td>
                    {vat && <td className="px-3 py-2 text-right">{f(r.vat, sym)}</td>}
                    <td className="px-3 py-2 text-right font-extrabold">{profit === null ? "—" : f(profit, sym)}</td>
                    <td className={`px-3 py-2 text-right font-extrabold ${pct === null ? "" : pct < 25 ? "text-coral-dark" : pct < 40 ? "text-amber-600" : "text-emerald-700"}`}>
                      {pct === null ? "—" : `${pct.toFixed(0)}%`}
                    </td>
                    <td className="px-3 py-2 text-right text-ink/60">{r.cost ? `×${(r.price / r.cost).toFixed(1)}` : "—"}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      ))}
      <p className="text-xs text-ink/50">
        Card fees assume Stripe UK pricing: 1.5% + 20p for UK cards; 3.25% + 30p plus 2% currency conversion for US and Australian cards.
        Prodigi costs are in the printing region&apos;s currency; your Prodigi account may bill in GBP at their exchange rate. Change prices in src/lib/products.ts.
      </p>
    </main>
  );
}
