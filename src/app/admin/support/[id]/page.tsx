import Link from "next/link";
import { notFound } from "next/navigation";
import Logo from "@/components/Logo";
import { getDesign, getOrder, getTicket } from "@/lib/server/db";
import { describeOptions, money } from "@/lib/products";
import { normalizeDesign } from "@/lib/types";
import { reasonFor } from "@/lib/support";
import ConfirmButton from "../ConfirmButton";

export const dynamic = "force-dynamic";
export const metadata = { title: "Support ticket · Mapsie admin" };

export default async function TicketAdmin({ params, searchParams }: { params: Promise<{ id: string }>; searchParams: Promise<Record<string, string | undefined>> }) {
  const { id } = await params;
  const q = await searchParams;
  const t = await getTicket(id);
  if (!t) notFound();
  const o = t.orderId ? await getOrder(t.orderId) : null;
  const raw = o?.designId ? await getDesign(o.designId) : null;
  const d = raw ? normalizeDesign(raw) : null;
  const btn = "rounded-full px-4 py-2 text-sm font-extrabold";
  return (
    <main className="max-w-5xl mx-auto px-6 py-10 space-y-6">
      <div>
        <Link href="/" className="font-display text-2xl font-extrabold"><Logo /></Link>
        <div className="flex flex-wrap items-baseline gap-4 mt-2">
          <h1 className="text-3xl font-extrabold">{reasonFor(t.reason).label}</h1>
          <Link href="/admin/support" className="text-sm font-bold text-coral-dark">← Support inbox</Link>
        </div>
        <p className="text-sm text-ink/60 mt-1">
          {t.id} · {t.name ? `${t.name} · ` : ""}<a className="underline" href={`mailto:${t.email}?subject=${encodeURIComponent(`Your Mapsie support request (${t.id})`)}`}>{t.email}</a> · {t.status}
        </p>
      </div>

      {q.error && <p className="rounded-2xl bg-coral/10 px-4 py-3 text-sm font-bold text-coral-dark">{q.error}</p>}
      {q.sent !== undefined && <p className="rounded-2xl bg-sea/10 px-4 py-3 text-sm font-bold text-sea">Reply sent to {t.email}.</p>}
      {q.reprint && <p className="rounded-2xl bg-sea/10 px-4 py-3 text-sm font-bold text-sea">Free reprint {q.reprint} created: it&apos;s now being prepared and goes to Prodigi automatically. Let the customer know below.</p>}
      {q.refunded !== undefined && <p className="rounded-2xl bg-sea/10 px-4 py-3 text-sm font-bold text-sea">Refunded through Stripe. Let the customer know below.</p>}

      <div className="grid gap-6 md:grid-cols-[1fr_320px] items-start">
        <div className="space-y-4">
          <ol className="space-y-3">
            {t.messages.map((m, i) => (
              <li key={i} className={`rounded-2xl px-4 py-3 ${m.from === "mapsie" ? "bg-sea/10 ml-10" : "bg-white shadow-sm mr-10"}`}>
                <div className="text-xs font-bold text-ink/50 mb-1">{m.from === "mapsie" ? "Mapsie" : t.name ?? "Customer"} · {new Date(m.at).toLocaleString("en-GB", { dateStyle: "medium", timeStyle: "short" })}</div>
                <p className="whitespace-pre-wrap text-sm">{m.text}</p>
                {!!m.files?.length && (
                  <div className="flex flex-wrap gap-2 mt-2">
                    {m.files.map((f) => (
                      <a key={f} href={`/api/support/files/${f}`} target="_blank" rel="noreferrer">
                        {/* eslint-disable-next-line @next/next/no-img-element */}
                        <img src={`/api/support/files/${f}`} alt="" className="w-28 h-28 rounded-xl object-cover" />
                      </a>
                    ))}
                  </div>
                )}
              </li>
            ))}
          </ol>
          <form action={`/api/admin/support/${t.id}`} method="post" className="rounded-3xl bg-white p-5 shadow-sm space-y-3">
            <input type="hidden" name="action" value="reply" />
            <div className="font-bold">Reply (emailed to the customer)</div>
            <textarea name="text" rows={6} required className="w-full rounded-2xl border-2 border-ink/10 px-4 py-3 outline-none focus:border-coral" />
            <div className="flex flex-wrap items-center gap-3 text-sm">
              <label>
                Then mark as{" "}
                <select name="status" defaultValue="waiting" className="rounded-full border border-ink/15 px-2 py-1">
                  <option value="waiting">waiting for customer</option>
                  <option value="resolved">resolved</option>
                  <option value="open">still open</option>
                </select>
              </label>
              <button className={`${btn} bg-coral text-white`}>Send reply</button>
            </div>
          </form>
        </div>

        <aside className="space-y-4">
          <section className="rounded-3xl bg-white p-5 shadow-sm space-y-2 text-sm">
            <div className="font-bold">Order</div>
            {o ? (
              <>
                <div className="font-mono text-xs">{o.id}{o.etsy && <span className="font-sans font-bold text-[#f1641e]"> · Etsy {o.etsy.receiptId}</span>}</div>
                {d && <div><Link className="font-bold underline" href={`/d/${o.designId}`} target="_blank">{d.title}</Link><div className="text-ink/60">{describeOptions(d)}</div></div>}
                <div>{money(o.region, o.total)} · {o.status}{o.refunded ? " · refunded" : ""}</div>
                <div className="text-ink/60">{[o.address?.name, o.address?.line1, o.address?.city, o.address?.postcode, o.address?.country].filter(Boolean).join(", ")}</div>
                {o.printProviderOrderId && <div className="text-ink/60">Prodigi {o.printProviderOrderId}{o.printStage ? ` · ${o.printStage}` : ""}</div>}
                {o.shipments?.map((s, i) => (
                  <div key={i}>{s.carrier} {s.trackingNumber} {s.trackingUrl && <a className="underline" href={s.trackingUrl} target="_blank" rel="noreferrer">track</a>}</div>
                ))}
                <div className="flex gap-3">
                  <Link className="font-bold text-coral-dark underline" href={`/order/${o.id}`} target="_blank">Order page</Link>
                  {o.renderFile && <a className="font-bold text-coral-dark underline" href={`/api/renders/${o.renderFile}`} target="_blank">Print file</a>}
                </div>
              </>
            ) : (
              <p className="text-ink/60">{t.orderRef ? <>They wrote “{t.orderRef}”, which doesn&apos;t match an order placed with {t.email}. Check with them before acting.</> : "No order given."}</p>
            )}
          </section>

          {o && (
            <section className="rounded-3xl bg-white p-5 shadow-sm space-y-3 text-sm">
              <div className="font-bold">Put it right</div>
              <form action={`/api/admin/support/${t.id}`} method="post">
                <input type="hidden" name="action" value="reprint" />
                <ConfirmButton message="Send a free reprint of this order to Prodigi?" className={`${btn} w-full bg-ink text-white`} disabled={!o.designId || !o.address}>Free reprint</ConfirmButton>
                <p className="text-xs text-ink/50 mt-1">Same design and address, sent to Prodigi as a new order at no charge.</p>
              </form>
              {o.etsy ? (
                <p className="text-xs text-ink/60">Refunds for Etsy orders are made on Etsy: <a className="underline" href={`https://www.etsy.com/your/orders/sold?order_id=${o.etsy.receiptId}`} target="_blank" rel="noreferrer">open it in Shop Manager</a>.</p>
              ) : (
                <form action={`/api/admin/support/${t.id}`} method="post">
                  <input type="hidden" name="action" value="refund" />
                  <ConfirmButton message={`Refund ${money(o.region, o.total)} to the customer's card?`} className={`${btn} w-full border-2 border-coral-dark text-coral-dark`} disabled={!!o.refunded}>{o.refunded ? "Already refunded" : `Full refund (${money(o.region, o.total)})`}</ConfirmButton>
                  <p className="text-xs text-ink/50 mt-1">Refunds the card through Stripe straight away.</p>
                </form>
              )}
            </section>
          )}

          <section className="rounded-3xl bg-white p-5 shadow-sm space-y-2 text-sm">
            <div className="font-bold">Status</div>
            <div className="flex flex-wrap gap-2">
              {(["open", "waiting", "resolved"] as const).map((s) => (
                <form key={s} action={`/api/admin/support/${t.id}`} method="post">
                  <input type="hidden" name="action" value="status" />
                  <input type="hidden" name="status" value={s} />
                  <button className={`${btn} ${t.status === s ? "bg-ink text-white" : "border-2 border-ink/15"}`}>{s}</button>
                </form>
              ))}
            </div>
            {!!t.actions?.length && (
              <ul className="text-xs text-ink/60 space-y-1 pt-2">
                {t.actions.map((a, i) => <li key={i}>{a}</li>)}
              </ul>
            )}
          </section>
        </aside>
      </div>
    </main>
  );
}
