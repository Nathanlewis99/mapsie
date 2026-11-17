import Link from "next/link";
import { notFound } from "next/navigation";
import Logo from "@/components/Logo";
import { getGiftCard } from "@/lib/server/db";
import { giftTokenValid } from "@/lib/server/giftcards";
import PrintButton from "./PrintButton";

export const dynamic = "force-dynamic";
export const metadata = { title: "Your Mapsie gift card", robots: { index: false } };

const money = (amount: number, currency: string) => `${{ gbp: "£", usd: "$", aud: "A$" }[currency] ?? ""}${Number.isInteger(amount) ? amount : amount.toFixed(2)}`;

/** The gift card itself: to show on screen, or print (A5, landscape-ish). */
export default async function GiftCardPage({ params, searchParams }: { params: Promise<{ id: string }>; searchParams: Promise<{ k?: string }> }) {
  const { id } = await params;
  const { k } = await searchParams;
  const g = await getGiftCard(id);
  if (!g || !giftTokenValid(id, k)) notFound();
  if (!g.code) {
    return (
      <main className="min-h-dvh grid place-items-center px-4 text-center">
        <div className="space-y-3"><Logo /><p className="font-bold">Your gift card is being prepared. Refresh in a moment.</p></div>
      </main>
    );
  }
  const expires = g.expiresAt ? new Date(g.expiresAt).toLocaleDateString("en-GB", { day: "numeric", month: "long", year: "numeric" }) : "";
  return (
    <main className="min-h-dvh bg-sand/40 py-10 px-4 print:bg-white print:p-0">
      <div className="mx-auto max-w-2xl space-y-6">
        <div className="flex justify-between items-center print:hidden">
          <Link href="/" className="font-display text-2xl font-extrabold"><Logo /></Link>
          <PrintButton />
        </div>
        <article className="relative overflow-hidden rounded-[2rem] bg-white shadow-2xl print:shadow-none print:rounded-none border border-ink/5" style={{ aspectRatio: "1.414 / 1" }}>
          <img src="/examples/southeast-asia.webp" alt="" className="absolute inset-y-0 right-0 h-full w-1/2 object-cover opacity-90" />
          <div className="absolute inset-y-0 right-0 w-1/2 bg-gradient-to-r from-white via-white/30 to-transparent" />
          <div className="relative h-full w-[62%] p-8 sm:p-10 flex flex-col">
            <div className="font-display text-3xl font-extrabold"><Logo /></div>
            <div className="mt-auto">
              <div className="text-sm font-extrabold uppercase tracking-[0.2em] text-coral">Gift card</div>
              <div className="font-display text-6xl font-extrabold leading-none mt-1">{money(g.amount, g.currency)}</div>
              {g.recipientName && <div className="mt-4 text-lg font-bold">For {g.recipientName}</div>}
              {g.message && <p className="mt-2 text-ink/70 italic leading-snug">“{g.message}”</p>}
              {g.fromName && <div className="mt-2 text-ink/60">With love from {g.fromName}</div>}
            </div>
            <div className="mt-6 rounded-2xl bg-cream px-4 py-3">
              <div className="text-xs text-ink/50 font-bold">YOUR CODE</div>
              <div className="font-mono text-2xl font-extrabold tracking-wider">{g.code}</div>
            </div>
            <div className="mt-3 text-xs text-ink/60">Design your map at <b>mapsie.shop</b> and enter the code at checkout.{expires && ` Valid until ${expires}.`}</div>
          </div>
        </article>
        <div className="text-center print:hidden space-y-2">
          {g.status === "redeemed" && <p className="font-bold text-coral-dark">This gift card has been used.</p>}
          <Link href="/create" className="inline-block rounded-full bg-coral px-6 py-3 font-extrabold text-white">Design my map →</Link>
        </div>
      </div>
    </main>
  );
}
