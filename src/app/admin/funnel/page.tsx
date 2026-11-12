import Link from "next/link";
import Logo from "@/components/Logo";
import { visitSteps } from "@/lib/server/db";
import { EXTRA_EVENTS, FUNNEL } from "@/lib/funnel";

export const dynamic = "force-dynamic";

const pct = (a: number, b: number) => (b ? `${((a / b) * 100).toFixed(a / b < 0.1 ? 1 : 0)}%` : "—");

export default async function Funnel({ searchParams }: { searchParams: Promise<{ days?: string; device?: string }> }) {
  const sp = await searchParams;
  const days = [1, 7, 30, 90].includes(Number(sp.days)) ? Number(sp.days) : 7;
  const device = sp.device === "mobile" || sp.device === "desktop" ? sp.device : "";
  let visits = await visitSteps(new Date(Date.now() - days * 86400_000).toISOString());
  if (device) visits = visits.filter((v) => v.props.device === device);
  const reached = (step: string) => visits.filter((v) => v.steps.includes(step)).length;
  const counts = FUNNEL.map((f) => ({ ...f, n: reached(f.id) }));
  const top = counts[0].n || Math.max(...counts.map((c) => c.n), 0);

  // Where visits came from, and how far each source gets.
  const bySource = new Map<string, typeof visits>();
  for (const v of visits) {
    const s = String(v.props.source ?? "unknown");
    bySource.set(s, [...(bySource.get(s) ?? []), v]);
  }
  const sources = [...bySource.entries()].sort((a, b) => b[1].length - a[1].length).slice(0, 12);
  const link = (q: Record<string, string | number>) => `?${new URLSearchParams({ days: String(days), ...(device ? { device } : {}), ...Object.fromEntries(Object.entries(q).map(([k, v]) => [k, String(v)])) })}`;

  return (
    <main className="max-w-6xl mx-auto px-6 py-10 space-y-6">
      <div>
        <Link href="/" className="font-display text-2xl font-extrabold"><Logo /></Link>
        <h1 className="text-3xl font-extrabold mt-2">Funnel</h1>
        <p className="text-sm text-ink/60 mt-1">Anonymous visits (no cookies, no personal data) and how far each one got. A visit is one browser tab session.</p>
        <Link href="/admin" className="text-sm font-bold text-coral-dark">← Orders</Link>
      </div>
      <div className="flex flex-wrap gap-2 text-sm font-bold">
        {[1, 7, 30, 90].map((d) => (
          <Link key={d} href={link({ days: d })} className={`rounded-full px-4 py-1.5 border-2 ${d === days ? "border-coral bg-white" : "border-ink/10"}`}>
            {d === 1 ? "24 hours" : `${d} days`}
          </Link>
        ))}
        <span className="w-px bg-ink/10 mx-1" />
        {["", "mobile", "desktop"].map((d) => (
          <Link key={d} href={`?${new URLSearchParams({ days: String(days), ...(d ? { device: d } : {}) })}`} className={`rounded-full px-4 py-1.5 border-2 ${d === device ? "border-coral bg-white" : "border-ink/10"}`}>
            {d || "All devices"}
          </Link>
        ))}
      </div>

      <div className="rounded-2xl bg-white shadow-sm p-5 space-y-2">
        {counts.map((c, i) => {
          const prev = i ? counts[i - 1].n : c.n;
          const drop = i ? prev - c.n : 0;
          return (
            <div key={c.id} className="grid grid-cols-[14rem_1fr_5rem_8rem] items-center gap-3 text-sm">
              <span className="font-bold">{c.label}</span>
              <div className="h-7 rounded-lg bg-sand/60 overflow-hidden">
                <div className="h-full rounded-lg bg-coral/80" style={{ width: top ? `${Math.max(1, (c.n / top) * 100)}%` : 0 }} />
              </div>
              <span className="font-extrabold text-right">{c.n}</span>
              <span className="text-xs text-ink/50">
                {i ? <>{pct(c.n, prev)} of previous{drop > 0 && <span className="text-coral-dark font-bold"> · −{drop}</span>}</> : "100%"}
              </span>
            </div>
          );
        })}
        <p className="text-xs text-ink/50 pt-2">Overall: {pct(counts.at(-1)!.n, counts[0].n)} of visits paid.</p>
      </div>

      <div className="rounded-2xl bg-white shadow-sm overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="text-left text-ink/50">
            <tr>
              <th className="px-4 py-2">Source</th>
              <th className="px-3 py-2 text-right">Visits</th>
              <th className="px-3 py-2 text-right">Opened editor</th>
              <th className="px-3 py-2 text-right">Reached checkout</th>
              <th className="px-3 py-2 text-right">Paid</th>
              <th className="px-3 py-2 text-right">Conversion</th>
            </tr>
          </thead>
          <tbody>
            {sources.map(([s, vs]) => {
              const n = (step: string) => vs.filter((v) => v.steps.includes(step)).length;
              return (
                <tr key={s} className="border-t border-ink/5">
                  <td className="px-4 py-2 font-bold">{s}</td>
                  <td className="px-3 py-2 text-right">{vs.length}</td>
                  <td className="px-3 py-2 text-right">{n("editor_open")}</td>
                  <td className="px-3 py-2 text-right">{n("checkout_view")}</td>
                  <td className="px-3 py-2 text-right">{n("paid")}</td>
                  <td className="px-3 py-2 text-right font-extrabold">{pct(n("paid"), vs.length)}</td>
                </tr>
              );
            })}
            {!sources.length && (
              <tr>
                <td colSpan={6} className="px-4 py-6 text-center text-ink/50">No visits in this period yet.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      <div className="flex flex-wrap gap-3 text-sm">
        {EXTRA_EVENTS.map((e) => (
          <span key={e} className="rounded-2xl bg-white shadow-sm px-4 py-2">
            <b>{reached(e)}</b> <span className="text-ink/60">{e.replace(/_/g, " ")}</span>
          </span>
        ))}
      </div>
      <p className="text-xs text-ink/50">Tag links with ?utm_source=instagram&amp;utm_campaign=launch to see them as their own source.</p>
    </main>
  );
}
