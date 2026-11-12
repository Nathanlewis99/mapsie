import Link from "next/link";
import Logo from "@/components/Logo";
import { listOrders, getDesign } from "@/lib/server/db";
import { getProduct, money, type RegionId, describeOptions } from "@/lib/products";
import RetryButton from "./RetryButton";

export const dynamic = "force-dynamic";

const STATUS: Record<string, string> = {
  pending_payment: "bg-ink/10 text-ink/60",
  paid: "bg-sea/20 text-sea",
  rendering: "bg-amber-100 text-amber-700",
  ready: "bg-amber-100 text-amber-700",
  submitted: "bg-emerald-100 text-emerald-700",
  shipped: "bg-emerald-200 text-emerald-800",
  cancelled: "bg-ink/10 text-ink/50",
  failed: "bg-coral/20 text-coral-dark",
};

export default async function Admin() {
  const orders = await listOrders();
  const rows = await Promise.all(orders.map(async (o) => ({ o, d: await getDesign(o.designId) })));
  const paid = orders.filter((o) => o.status !== "pending_payment");
  return (
    <main className="max-w-6xl mx-auto px-6 py-10 space-y-6">
      <div className="flex items-end justify-between">
        <div>
          <Link href="/" className="font-display text-2xl font-extrabold"><Logo /></Link>
          <h1 className="text-3xl font-extrabold mt-2">Orders</h1>
          <div className="flex flex-wrap gap-4">
            <Link href="/admin/costs" className="text-sm font-bold text-coral-dark">Costs &amp; margins →</Link>
            <a href="/api/admin/prodigi-check" className="text-sm font-bold text-coral-dark">Check our print options against Prodigi&apos;s catalogue →</a>
          </div>
        </div>
        <div className="flex gap-3 text-sm font-bold">
          <span className="rounded-2xl bg-white px-4 py-2 shadow-sm">{paid.length} paid</span>
          <span className="rounded-2xl bg-white px-4 py-2 shadow-sm">{orders.filter((o) => o.status === "failed").length} need attention</span>
        </div>
      </div>
      <div className="overflow-x-auto rounded-3xl bg-white shadow-sm">
        <table className="w-full text-sm">
          <thead className="text-left text-xs uppercase tracking-wider text-ink/50">
            <tr>{["Order", "Created", "Design", "Product", "Total", "Ship to", "Status", ""].map((h) => <th key={h} className="px-4 py-3">{h}</th>)}</tr>
          </thead>
          <tbody>
            {rows.map(({ o, d }) => (
              <tr key={o.id} className="border-t border-ink/5 align-top">
                <td className="px-4 py-3 font-mono text-xs">{o.id}<div className="text-ink/40">{o.email}</div></td>
                <td className="px-4 py-3 whitespace-nowrap">{new Date(o.createdAt).toLocaleString("en-GB", { dateStyle: "short", timeStyle: "short" })}</td>
                <td className="px-4 py-3"><Link className="font-bold underline" href={`/d/${o.designId}`}>{d?.title ?? "?"}</Link><div className="text-ink/40">{d?.stops.length} stops</div></td>
                <td className="px-4 py-3">{d ? describeOptions(d) : "?"}</td>
                <td className="px-4 py-3 font-bold">{money((o.region ?? "GB") as RegionId, o.total ?? 0)}</td>
                <td className="px-4 py-3">{o.address ? `${o.address.name}, ${o.address.city} ${o.address.postcode}, ${o.address.country}` : "—"}</td>
                <td className="px-4 py-3">
                  <span className={`rounded-full px-2.5 py-1 text-xs font-bold ${STATUS[o.status] ?? ""}`}>{o.status.replace("_", " ")}</span>
                  {o.error && <div className="text-xs text-coral-dark mt-1 max-w-[220px] break-words">{o.error.slice(0, 160)}</div>}
                  {o.printProviderOrderId && <div className="text-xs text-ink/40 mt-1">{o.printProviderOrderId}</div>}
                </td>
                <td className="px-4 py-3 whitespace-nowrap space-x-3">
                  {o.renderFile && <a className="font-bold text-coral" href={`/api/renders/${o.renderFile}`} target="_blank">Print file</a>}
                  {o.address && o.status === "failed" && <RetryButton id={o.id} />}
                </td>
              </tr>
            ))}
            {!rows.length && <tr><td colSpan={8} className="px-4 py-10 text-center text-ink/40">No orders yet.</td></tr>}
          </tbody>
        </table>
      </div>
    </main>
  );
}
