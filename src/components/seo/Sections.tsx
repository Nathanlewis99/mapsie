import Link from "next/link";
import { EXAMPLES, FAQ } from "@/lib/seo";
import { OCCASIONS } from "@/lib/occasions";

/** Photos of real Mapsie prints (real images, so they show up in image search). */
export function Gallery({ only, title = "Made with Mapsie" }: { only?: string[]; title?: string }) {
  const list = only ? EXAMPLES.filter((e) => only.includes(e.slug)) : EXAMPLES;
  return (
    <section className="max-w-6xl mx-auto px-6 py-16">
      <h2 className="font-display text-4xl font-extrabold text-center">{title}</h2>
      <div className="mt-10 grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {list.map((e) => (
          <figure key={e.slug} className="rounded-3xl bg-white p-2 shadow-sm">
            <img src={`/examples/${e.slug}-600.webp`} srcSet={`/examples/${e.slug}-600.webp 600w, /examples/${e.slug}.webp 1200w`} sizes="(min-width: 1024px) 280px, (min-width: 640px) 45vw, 92vw" alt={e.alt} width={600} height={450} loading="lazy" decoding="async" className="rounded-2xl w-full h-auto" />
            <figcaption className="px-2 py-2 text-sm font-bold">{e.title}</figcaption>
          </figure>
        ))}
      </div>
    </section>
  );
}

/** Links to the trip and occasion pages. */
export function OccasionLinks({ except }: { except?: string }) {
  return (
    <section className="max-w-6xl mx-auto px-6 pb-16">
      <h2 className="font-display text-3xl font-extrabold text-center">A map for every kind of trip</h2>
      <div className="mt-8 flex flex-wrap justify-center gap-2">
        {OCCASIONS.filter((o) => o.slug !== except).map((o) => (
          <Link key={o.slug} href={`/maps/${o.slug}`} className="rounded-full bg-white border border-ink/10 px-4 py-2 text-sm font-extrabold hover:border-coral hover:text-coral-dark">
            {o.nav}
          </Link>
        ))}
      </div>
    </section>
  );
}

/** Questions people ask before buying (also sent to Google as FAQ structured data). */
export function Faq({ items = FAQ }: { items?: { q: string; a: string }[] }) {
  return (
    <section className="max-w-3xl mx-auto px-6 py-16">
      <h2 className="font-display text-4xl font-extrabold text-center">Questions</h2>
      <div className="mt-8 space-y-3">
        {items.map((f) => (
          <details key={f.q} className="group rounded-2xl bg-white p-5 shadow-sm">
            <summary className="cursor-pointer list-none font-extrabold flex justify-between gap-4">
              {f.q}
              <span className="text-coral transition group-open:rotate-45">+</span>
            </summary>
            <p className="mt-3 text-ink/70">{f.a}</p>
          </details>
        ))}
      </div>
    </section>
  );
}
