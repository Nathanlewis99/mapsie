import type { Review } from "@/lib/server/db";

/** Approved reviews customers agreed we could show. */
export function Reviews({ items, count, average }: { items: Review[]; count: number; average: number }) {
  if (count < 3 || items.length < 3) return null;
  return (
    <section className="max-w-6xl mx-auto px-6 py-16">
      <h2 className="font-display text-4xl font-extrabold text-center">What customers say</h2>
      <p className="text-center mt-2 text-ink/60 font-bold"><span className="text-amber-500">★</span> {average.toFixed(1)} from {count} reviews</p>
      <div className="mt-10 grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
        {items.slice(0, 6).map((r) => (
          <figure key={r.id} className="rounded-3xl bg-white p-5 shadow-sm space-y-3">
            {r.photo && <img src={r.photo} alt={`${r.name}'s Mapsie map print`} loading="lazy" className="rounded-2xl w-full aspect-[4/3] object-cover" />}
            <div className="text-amber-500">{"★".repeat(r.rating)}<span className="text-ink/15">{"★".repeat(5 - r.rating)}</span></div>
            {r.text && <blockquote className="text-ink/80">“{r.text}”</blockquote>}
            <figcaption className="text-sm font-bold text-ink/60">{r.name}</figcaption>
          </figure>
        ))}
      </div>
    </section>
  );
}
