import Link from "next/link";
import Logo from "@/components/Logo";
import { listTickets } from "@/lib/server/db";
import { reasonFor } from "@/lib/support";

export const dynamic = "force-dynamic";
export const metadata = { title: "Support · Mapsie admin" };

const BADGE = { open: "bg-coral/15 text-coral-dark", waiting: "bg-amber-100 text-amber-800", resolved: "bg-sea/15 text-sea" } as const;
const ago = (iso: string) => {
  const h = (Date.now() - new Date(iso).getTime()) / 3600_000;
  return h < 1 ? `${Math.max(1, Math.round(h * 60))} min ago` : h < 48 ? `${Math.round(h)} h ago` : `${Math.round(h / 24)} days ago`;
};

export default async function SupportInbox({ searchParams }: { searchParams: Promise<{ show?: string }> }) {
  const { show = "active" } = await searchParams;
  const all = await listTickets();
  const tickets = show === "all" ? all : show === "resolved" ? all.filter((t) => t.status === "resolved") : all.filter((t) => t.status !== "resolved");
  const tab = (id: string, label: string) => (
    <Link href={`/admin/support?show=${id}`} className={`rounded-full px-3 py-1 text-sm font-bold ${show === id ? "bg-ink text-white" : "bg-white"}`}>{label}</Link>
  );
  return (
    <main className="max-w-5xl mx-auto px-6 py-10 space-y-6">
      <div>
        <Link href="/" className="font-display text-2xl font-extrabold"><Logo /></Link>
        <div className="flex items-baseline gap-4 mt-2">
          <h1 className="text-3xl font-extrabold">Support</h1>
          <Link href="/admin" className="text-sm font-bold text-coral-dark">← Orders</Link>
        </div>
      </div>
      <div className="flex gap-2">
        {tab("active", `Needs attention (${all.filter((t) => t.status !== "resolved").length})`)}
        {tab("resolved", "Resolved")}
        {tab("all", "All")}
      </div>
      <div className="rounded-3xl bg-white shadow-sm divide-y divide-ink/5">
        {tickets.map((t) => (
          <Link key={t.id} href={`/admin/support/${t.id}`} className="flex flex-wrap items-center gap-x-4 gap-y-1 px-5 py-4 hover:bg-sand/40">
            <span className={`rounded-full px-2.5 py-1 text-xs font-bold ${BADGE[t.status]}`}>{t.status}</span>
            <span className="font-bold">{reasonFor(t.reason).label}</span>
            <span className="text-sm text-ink/60">{t.name ?? t.email}</span>
            {!t.orderId && t.orderRef && <span className="text-xs font-bold text-coral-dark">order not matched</span>}
            <span className="ml-auto text-xs text-ink/50">
              {t.id} · {t.messages[t.messages.length - 1].from === "customer" ? "customer replied" : "we replied"} {ago(t.updatedAt)}
            </span>
            <span className="basis-full text-sm text-ink/60 truncate">{t.messages[t.messages.length - 1].text}</span>
          </Link>
        ))}
        {!tickets.length && <p className="px-5 py-10 text-center text-ink/40">Nothing here. 🎉</p>}
      </div>
    </main>
  );
}
