import Link from "next/link";
import Logo from "@/components/Logo";
import { redirect } from "next/navigation";
import { currentUser } from "@/lib/server/auth";
import { getDesign, listOrdersForUser, listSavedDesigns } from "@/lib/server/db";
import { getProduct, money, type RegionId } from "@/lib/products";
import { normalizeDesign } from "@/lib/types";
import SiteFooter from "@/components/SiteFooter";
import DeleteDesignButton from "./DeleteDesignButton";

export const dynamic = "force-dynamic";
export const metadata = { title: "My account · Mapsie" };

const STATUS: Record<string, { label: string; cls: string }> = {
  paid: { label: "Paid", cls: "bg-sea/15 text-sea" },
  rendering: { label: "Preparing print", cls: "bg-amber-100 text-amber-800" },
  ready: { label: "Final check", cls: "bg-amber-100 text-amber-800" },
  submitted: { label: "Sent to print", cls: "bg-emerald-100 text-emerald-800" },
  cancelled: { label: "Cancelled", cls: "bg-ink/10 text-ink/60" },
  failed: { label: "Delayed: we're on it", cls: "bg-coral/15 text-coral-dark" },
};
const date = (iso: string) => new Date(iso).toLocaleDateString("en-GB", { day: "numeric", month: "short", year: "numeric" });

export default async function Account() {
  const user = await currentUser();
  if (!user) redirect("/signin?next=/account");
  const designs = listSavedDesigns(user.id);
  const orders = await Promise.all(
    (await listOrdersForUser(user)).map(async (o) => ({ o, d: await getDesign(o.designId).then((x) => (x ? normalizeDesign(x) : null)) })),
  );

  return (
    <div className="min-h-dvh flex flex-col">
      <header className="max-w-5xl w-full mx-auto px-4 sm:px-6 py-5 flex justify-between items-center gap-4">
        <Link href="/" className="font-display text-3xl font-extrabold"><Logo /></Link>
        <div className="flex items-center gap-3">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          {user.picture && <img src={user.picture} alt="" referrerPolicy="no-referrer" className="w-9 h-9 rounded-full" />}
          <form action="/api/auth/signout" method="post">
            <button className="text-sm font-bold text-ink/60 hover:text-ink">Sign out</button>
          </form>
        </div>
      </header>

      <main className="max-w-5xl w-full mx-auto px-4 sm:px-6 pb-16 space-y-12 flex-1">
        <div>
          <h1 className="font-display text-4xl font-extrabold">Hi{user.name ? `, ${user.name.split(" ")[0]}` : ""} 👋</h1>
          <p className="text-ink/60 mt-1">{user.email}</p>
        </div>

        <section className="space-y-4">
          <div className="flex items-end justify-between gap-4">
            <h2 className="font-display text-2xl font-extrabold">Your maps</h2>
            <Link href="/create?new=1" className="rounded-full bg-coral px-5 py-2.5 font-extrabold text-white shadow-lg shadow-coral/30">+ New map</Link>
          </div>
          {designs.length === 0 ? (
            <div className="rounded-3xl bg-white p-8 text-center text-ink/60">
              No saved maps yet. Design one and press <b>Save</b>, and it&apos;ll appear here.
            </div>
          ) : (
            <ul className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {designs.map((s) => {
                const d = normalizeDesign(s.design);
                const c = d.theme.colors;
                return (
                  <li key={s.id} className="rounded-3xl bg-white shadow-sm overflow-hidden flex flex-col">
                    <Link href={`/create?saved=${s.id}`} className="block h-28 relative overflow-hidden" style={{ background: c.land }} aria-label={`Open ${s.title}`}>
                      <span className="absolute -right-6 -bottom-8 w-32 h-24 rounded-full" style={{ background: c.water }} />
                      <svg className="absolute inset-0 w-full h-full" viewBox="0 0 200 90" preserveAspectRatio="none" aria-hidden>
                        <path d="M14 70 Q 70 10 120 40 T 186 22" fill="none" stroke={c.accent} strokeWidth="3" strokeDasharray="6 5" strokeLinecap="round" />
                      </svg>
                      <span className="absolute left-3 bottom-2 font-display font-extrabold text-lg" style={{ color: c.ink }}>{s.title}</span>
                    </Link>
                    <div className="p-4 flex-1 flex flex-col gap-2">
                      <p className="text-sm text-ink/60 line-clamp-2">{d.stops.map((x) => x.name).join(" → ") || "No stops yet"}</p>
                      <div className="mt-auto flex items-center justify-between text-sm">
                        <span className="text-ink/40">Edited {date(s.updatedAt)}</span>
                        <span className="flex gap-3">
                          <Link href={`/create?saved=${s.id}`} className="font-extrabold text-coral">Open</Link>
                          <DeleteDesignButton id={s.id} title={s.title} />
                        </span>
                      </div>
                    </div>
                  </li>
                );
              })}
            </ul>
          )}
        </section>

        <section className="space-y-4">
          <h2 className="font-display text-2xl font-extrabold">Your orders</h2>
          {orders.length === 0 ? (
            <div className="rounded-3xl bg-white p-8 text-center text-ink/60">No orders yet.</div>
          ) : (
            <ul className="rounded-3xl bg-white shadow-sm divide-y divide-ink/5">
              {orders.map(({ o, d }) => {
                const st = STATUS[o.status] ?? { label: o.status, cls: "bg-ink/10" };
                return (
                  <li key={o.id}>
                    <Link href={`/order/${o.id}`} className="flex flex-wrap items-center gap-x-4 gap-y-1 px-5 py-4 hover:bg-cream/60">
                      <span className="font-extrabold flex-1 min-w-[10rem]">{d?.title ?? "Map print"}</span>
                      <span className="text-sm text-ink/60">{d ? `${getProduct(d.productId).label}${d.frame !== "none" ? `, ${d.frame} frame` : ""}` : ""}</span>
                      <span className="text-sm text-ink/60">{date(o.createdAt)}</span>
                      <span className="text-sm font-bold">{money((o.region ?? "GB") as RegionId, o.total ?? 0)}</span>
                      <span className={`rounded-full px-2.5 py-1 text-xs font-extrabold ${st.cls}`}>{st.label}</span>
                    </Link>
                  </li>
                );
              })}
            </ul>
          )}
        </section>
      </main>
      <SiteFooter />
    </div>
  );
}
