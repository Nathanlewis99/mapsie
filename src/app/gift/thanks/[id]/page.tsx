import Link from "next/link";
import { notFound } from "next/navigation";
import Logo from "@/components/Logo";
import { getGiftCard } from "@/lib/server/db";
import { giftCardUrl, giftTokenValid } from "@/lib/server/giftcards";
import Refresh from "./Refresh";

export const dynamic = "force-dynamic";
export const metadata = { title: "Thank you · Mapsie gift card", robots: { index: false } };

export default async function GiftThanks({ params, searchParams }: { params: Promise<{ id: string }>; searchParams: Promise<{ k?: string }> }) {
  const { id } = await params;
  const { k } = await searchParams;
  const g = await getGiftCard(id);
  if (!g || !giftTokenValid(id, k)) notFound();
  const ready = !!g.code;
  return (
    <main className="min-h-dvh grid place-items-center px-4 py-10">
      <div className="max-w-md w-full rounded-3xl bg-white p-8 shadow-sm space-y-4 text-center">
        <Link href="/" className="font-display text-3xl font-extrabold block"><Logo /></Link>
        <h1 className="font-display text-3xl font-extrabold">Thank you! 🎁</h1>
        {ready ? (
          <>
            <p className="text-ink/70">Your gift card is ready, and we&apos;ve emailed it to {g.buyerEmail}.{g.recipientEmail ? (g.sentToRecipientAt ? ` It's on its way to ${g.recipientName || g.recipientEmail} too.` : ` We'll send it to ${g.recipientName || g.recipientEmail} on ${g.sendOn ? new Date(`${g.sendOn}T12:00:00Z`).toLocaleDateString("en-GB", { day: "numeric", month: "long" }) : "the day you chose"}.`) : ""}</p>
            <div className="rounded-2xl bg-cream px-4 py-3"><div className="text-xs font-bold text-ink/50">CODE</div><div className="font-mono text-2xl font-extrabold">{g.code}</div></div>
            <a href={giftCardUrl(g.id)} className="block rounded-full bg-coral py-3 font-extrabold text-white">See and print the card</a>
          </>
        ) : (
          <>
            <p className="text-ink/70">We&apos;re confirming your payment and making your gift card. This takes a few seconds…</p>
            <Refresh />
          </>
        )}
      </div>
    </main>
  );
}
