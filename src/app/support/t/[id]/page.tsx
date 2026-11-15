import Link from "next/link";
import { notFound } from "next/navigation";
import Logo from "@/components/Logo";
import { getTicket } from "@/lib/server/db";
import { ticketTokenValid } from "@/lib/server/support";
import { reasonFor } from "@/lib/support";
import TicketReply from "./TicketReply";

export const dynamic = "force-dynamic";
export const metadata = { title: "Your support request · Mapsie", robots: { index: false } };

const STATUS = { open: "We're looking into it", waiting: "Waiting for your reply", resolved: "Resolved" } as const;

export default async function TicketPage({ params, searchParams }: { params: Promise<{ id: string }>; searchParams: Promise<{ k?: string }> }) {
  const { id } = await params;
  const { k } = await searchParams;
  const t = await getTicket(id);
  if (!t || !ticketTokenValid(id, k)) notFound();
  return (
    <main className="max-w-2xl mx-auto px-4 sm:px-6 py-8 space-y-6">
      <Link href="/" className="font-display text-3xl font-extrabold"><Logo /></Link>
      <div>
        <h1 className="font-display text-3xl font-extrabold">{reasonFor(t.reason).label}</h1>
        <p className="text-sm text-ink/60 mt-1">
          {t.id} · {STATUS[t.status]}
          {t.orderId && <> · <Link className="underline" href={`/order/${t.orderId}`}>your order</Link></>}
        </p>
      </div>
      <ol className="space-y-3">
        {t.messages.map((m, i) => (
          <li key={i} className={`rounded-2xl px-4 py-3 ${m.from === "mapsie" ? "bg-sea/10 mr-8" : "bg-white shadow-sm ml-8"}`}>
            <div className="text-xs font-bold text-ink/50 mb-1">
              {m.from === "mapsie" ? "Mapsie" : "You"} · {new Date(m.at).toLocaleString("en-GB", { dateStyle: "medium", timeStyle: "short" })}
            </div>
            <p className="whitespace-pre-wrap text-sm">{m.text}</p>
            {!!m.files?.length && (
              <div className="flex flex-wrap gap-2 mt-2">
                {m.files.map((f) => (
                  <a key={f} href={`/api/support/files/${f}?k=${k}`} target="_blank" rel="noreferrer">
                    {/* eslint-disable-next-line @next/next/no-img-element */}
                    <img src={`/api/support/files/${f}?k=${k}`} alt="" className="w-20 h-20 rounded-xl object-cover" />
                  </a>
                ))}
              </div>
            )}
          </li>
        ))}
      </ol>
      <TicketReply id={t.id} k={k!} />
    </main>
  );
}
