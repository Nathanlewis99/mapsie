import Link from "next/link";
import Logo from "@/components/Logo";
import { listReviews, reviewSummary } from "@/lib/server/db";

export const dynamic = "force-dynamic";
export const metadata = { title: "Reviews · Admin" };

export default async function ReviewsAdmin() {
  const reviews = await listReviews();
  const sum = await reviewSummary();
  return (
    <main className="max-w-5xl mx-auto px-6 py-10 space-y-6">
      <div>
        <Link href="/" className="font-display text-2xl font-extrabold"><Logo /></Link>
        <div className="flex items-baseline gap-4 mt-2">
          <h1 className="text-3xl font-extrabold">Reviews</h1>
          <Link href="/admin" className="text-sm font-bold text-coral-dark">← All orders</Link>
        </div>
        <p className="text-sm text-ink/60 mt-1">
          {sum.count} approved, average {sum.average ? sum.average.toFixed(1) : "–"}★. Approve every genuine review, good or bad: only hide spam, abuse or
          personal details (hiding honest negative reviews is against consumer law and Google&apos;s rules). Reviews show on the homepage once 3 are approved and allowed to be published.
        </p>
      </div>
      <div className="space-y-3">
        {reviews.map((r) => (
          <div key={r.id} className="rounded-3xl bg-white p-5 shadow-sm flex gap-4">
            {r.photo && <img src={r.photo} alt="" className="w-28 h-28 object-cover rounded-2xl shrink-0" />}
            <div className="flex-1 min-w-0 space-y-1 text-sm">
              <div className="flex flex-wrap items-center gap-2">
                <span className="text-amber-500 text-lg">{"★".repeat(r.rating)}<span className="text-ink/15">{"★".repeat(5 - r.rating)}</span></span>
                <b>{r.name}</b>
                <span className="text-ink/40">{new Date(r.createdAt).toLocaleDateString("en-GB")} · <Link className="underline" href={`/order/${r.orderId}`}>{r.orderId}</Link></span>
                <span className="rounded-full bg-sand px-2.5 py-0.5 text-xs font-bold">{r.status}</span>
                {!r.publish && <span className="rounded-full bg-coral/10 text-coral-dark px-2.5 py-0.5 text-xs font-bold">private (not for the website)</span>}
              </div>
              <p className="text-ink/80 whitespace-pre-line">{r.text || <i className="text-ink/40">No comment</i>}</p>
              <div className="flex gap-2 pt-1">
                {(["approved", "hidden"] as const).filter((s) => s !== r.status).map((s) => (
                  <form key={s} action="/api/admin/reviews" method="post">
                    <input type="hidden" name="id" value={r.id} />
                    <input type="hidden" name="status" value={s} />
                    <button className={`rounded-full px-3 py-1.5 text-xs font-bold ${s === "approved" ? "bg-ink text-white" : "border-2 border-ink/10"}`}>{s === "approved" ? "Approve" : "Hide"}</button>
                  </form>
                ))}
              </div>
            </div>
          </div>
        ))}
        {!reviews.length && <p className="text-ink/40 text-center py-10">No reviews yet. Requests go out a few days after each order arrives.</p>}
      </div>
    </main>
  );
}
