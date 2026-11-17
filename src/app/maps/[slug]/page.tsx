import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import Logo from "@/components/Logo";
import SiteFooter from "@/components/SiteFooter";
import JsonLd from "@/components/seo/JsonLd";
import ChristmasBanner from "@/components/ChristmasBanner";
import { Faq, Gallery, OccasionLinks } from "@/components/seo/Sections";
import { OCCASIONS, getOccasion, occasionStartUrl } from "@/lib/occasions";
import { EXAMPLES, FAQ, PRICE_RANGE, SITE, faqJsonLd } from "@/lib/seo";

export const dynamicParams = false;
export function generateStaticParams() {
  return OCCASIONS.map((o) => ({ slug: o.slug }));
}

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }): Promise<Metadata> {
  const o = getOccasion((await params).slug);
  if (!o) return {};
  const image = `/examples/${o.example}.webp`;
  return {
    title: o.metaTitle,
    description: o.description,
    alternates: { canonical: `/maps/${o.slug}` },
    openGraph: { title: o.metaTitle, description: o.description, url: `/maps/${o.slug}`, images: [{ url: image, width: 1200, height: 900 }] },
    twitter: { card: "summary_large_image", title: o.metaTitle, description: o.description, images: [image] },
  };
}

export default async function OccasionPage({ params }: { params: Promise<{ slug: string }> }) {
  const o = getOccasion((await params).slug);
  if (!o) notFound();
  const ex = EXAMPLES.find((e) => e.slug === o.example) ?? EXAMPLES[0];
  const faq = o.gift ? FAQ.filter((f) => /gift|delivery|digital|frame/i.test(f.q)) : FAQ.slice(0, 5);
  const start = occasionStartUrl(o);
  return (
    <div className="min-h-dvh overflow-x-hidden">
      <ChristmasBanner />
      <header className="max-w-6xl mx-auto px-6 py-5 flex justify-between items-center">
        <Link href="/" className="font-display text-3xl font-extrabold"><Logo /></Link>
        <Link href="/create" className="rounded-full bg-ink text-white px-5 py-2.5 font-extrabold hover:bg-ink/85">Start designing</Link>
      </header>
      <main>
        <nav aria-label="Breadcrumb" className="max-w-6xl mx-auto px-6 text-sm text-ink/50">
          <Link href="/" className="hover:text-ink">Home</Link> › <Link href="/maps" className="hover:text-ink">Map ideas</Link> › <span>{o.nav}</span>
        </nav>
        <section className="max-w-6xl mx-auto px-6 pt-6 pb-14 grid lg:grid-cols-[1fr_1.1fr] gap-10 items-center">
          <div>
            <h1 className="font-display text-4xl sm:text-5xl font-extrabold leading-tight tracking-tight">{o.h1}</h1>
            {o.intro.map((p) => (
              <p key={p.slice(0, 20)} className="mt-5 text-lg text-ink/70">{p}</p>
            ))}
            <div className="mt-8 flex flex-wrap gap-3 items-center">
              <Link href={start} className="rounded-full bg-coral px-7 py-4 text-lg font-extrabold text-white shadow-xl shadow-coral/30 hover:bg-coral-dark">{o.startLabel} →</Link>
              <span className="text-sm text-ink/50 font-semibold">Free to design · prints from £34 · free delivery</span>
            </div>
          </div>
          <img src={`/examples/${ex.slug}.webp`} alt={ex.alt} width={1200} height={900} fetchPriority="high" className="w-full h-auto rounded-3xl shadow-xl" />
        </section>
        <section className="bg-white/60 border-y border-ink/5">
          <div className="max-w-3xl mx-auto px-6 py-14">
            <h2 className="font-display text-3xl font-extrabold">{o.ideasTitle}</h2>
            <ul className="mt-6 space-y-3">
              {o.ideas.map((i) => (
                <li key={i} className="flex gap-3 text-lg"><span className="text-coral font-extrabold">✓</span><span className="text-ink/80">{i}</span></li>
              ))}
            </ul>
            <Link href={start} className="mt-8 inline-block rounded-full bg-coral px-6 py-3 font-extrabold text-white">{o.startLabel} →</Link>
          </div>
        </section>
        <Gallery title="More maps made with Mapsie" only={EXAMPLES.filter((e) => e.slug !== ex.slug).slice(0, 4).map((e) => e.slug)} />
        <Faq items={faq} />
        <OccasionLinks except={o.slug} />
      </main>
      <SiteFooter />
      <JsonLd
        data={[
          {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            itemListElement: [
              { "@type": "ListItem", position: 1, name: "Home", item: SITE },
              { "@type": "ListItem", position: 2, name: "Map ideas", item: `${SITE}/maps` },
              { "@type": "ListItem", position: 3, name: o.nav, item: `${SITE}/maps/${o.slug}` },
            ],
          },
          {
            "@context": "https://schema.org",
            "@type": "Product",
            name: o.h1,
            description: o.description,
            image: `${SITE}/examples/${ex.slug}.webp`,
            brand: { "@type": "Brand", name: "Mapsie" },
            offers: { "@type": "AggregateOffer", priceCurrency: "GBP", lowPrice: PRICE_RANGE.low, highPrice: PRICE_RANGE.high, availability: "https://schema.org/InStock", url: `${SITE}/create` },
          },
          faqJsonLd(faq),
        ]}
      />
    </div>
  );
}
