import Link from "next/link";
import Logo from "@/components/Logo";
import { listGiftCards } from "@/lib/server/db";
import { giftCardUrl } from "@/lib/server/giftcards";

export const dynamic = "force-dynamic";
export const metadata = { title: "Gift cards · Admin" };

export default async function GiftAdmin() {
  const cards = await listGiftCards();
  const sold = cards.filter((c) => c.status !== "pending_payment" && !c.parentId);
  const money = (n: number, c: string) => `${{ gbp: "£", usd: "$", aud: "A$" }[c] ?? ""}${n}`;
  return (
    <main className="max-w-5xl mx-auto px-6 py-10 space-y-6">
      <div>
        <Link href="/" className="font-display text-2xl font-extrabold"><Logo /></Link>
        <div className="flex items-baseline gap-4 mt-2">
          <h1 className="text-3xl font-extrabold">Gift cards</h1>
          <Link href="/admin" className="text-sm font-bold text-coral-dark">← All orders</Link>
        </div>
        <p className="text-sm text-ink/60 mt-1">{sold.length} sold. To cancel one (within 14 days, unused): refund the payment in Stripe and deactivate its promotion code there.</p>
      </div>
      <div className="rounded-3xl bg-white p-4 shadow-sm overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="text-left text-xs uppercase tracking-wider text-ink/50">
            <tr>{["Bought", "Amount", "Code", "From → for", "Buyer", "Status", ""].map((h) => <th key={h} className="px-2 py-2">{h}</th>)}</tr>
          </thead>
          <tbody>
            {cards.map((c) => (
              <tr key={c.id} className="border-t border-ink/5 align-top">
                <td className="px-2 py-2 whitespace-nowrap">{new Date(c.createdAt).toLocaleDateString("en-GB")}</td>
                <td className="px-2 py-2 font-bold">{money(c.amount, c.currency)}{c.parentId && <div className="text-xs text-ink/40 font-normal">balance</div>}</td>
                <td className="px-2 py-2 font-mono">{c.code ?? "—"}</td>
                <td className="px-2 py-2">{c.fromName || "?"} → {c.recipientName || "?"}{c.recipientEmail && <div className="text-xs text-ink/40">{c.recipientEmail}{c.sendOn ? ` on ${c.sendOn}` : ""}{c.sentToRecipientAt ? " · sent" : ""}</div>}</td>
                <td className="px-2 py-2">{c.buyerEmail}</td>
                <td className="px-2 py-2"><span className="rounded-full bg-sand px-2.5 py-1 text-xs font-bold">{c.status.replace("_", " ")}</span>{c.redeemedOrderId && <div className="text-xs mt-1"><Link className="underline" href={`/order/${c.redeemedOrderId}`}>order</Link></div>}</td>
                <td className="px-2 py-2">{c.code && <a className="text-xs font-bold underline" href={giftCardUrl(c.id)} target="_blank" rel="noreferrer">Card</a>}</td>
              </tr>
            ))}
            {!cards.length && <tr><td colSpan={7} className="px-2 py-8 text-center text-ink/40">No gift cards yet.</td></tr>}
          </tbody>
        </table>
      </div>
    </main>
  );
}
