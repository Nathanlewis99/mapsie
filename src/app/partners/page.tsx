import type { Metadata } from "next";
import Link from "next/link";
import Logo from "@/components/Logo";
import SiteFooter from "@/components/SiteFooter";
import { Faq } from "@/components/seo/Sections";
import { tradeDiscountPct } from "@/lib/partners";
import EnquiryForm from "./EnquiryForm";

export const metadata: Metadata = {
  title: "Mapsie for Business: Map Prints for Tour Operators, Events & Gifting",
  description: "Give your customers a map print of their trip, challenge or new home. Pre-drawn routes, commission on every sale, or gift cards and prepaid codes at trade prices.",
  alternates: { canonical: "/partners" },
};

const SEGMENTS = [
  {
    id: "travel",
    title: "Tour operators & travel agents",
    lead: "The trip of a lifetime, on their wall.",
    points: [
      "Send a link after the trip: your itinerary is already drawn, on the real roads, rails and flight paths",
      "They add their photos and names, and order a print",
      "You earn commission on every order, or include a print as a thank-you at trade price",
    ],
    image: "/partners/travel.webp",
  },
  {
    id: "event",
    title: "Events & challenges",
    lead: "A finisher print for every rider, runner and walker.",
    points: [
      "Your route, drawn once, personalised with each finisher's name and time",
      "Sell it as an add-on, or bundle a code with every entry",
      "Lovely for charity challenges, sportives, ultras and multi-day treks",
    ],
    image: "/partners/event.webp",
  },
  {
    id: "wedding",
    title: "Wedding registries & planners",
    lead: "The honeymoon, the proposal, the places that matter.",
    points: [
      "Mapsie gift cards for your registry or honeymoon fund",
      "A pre-filled page for couples, with names and wedding date",
      "Paper and cotton anniversary gifts, too",
    ],
    image: "/partners/wedding.webp",
  },
  {
    id: "shop",
    title: "Gift & souvenir shops",
    lead: "The souvenir that's actually about their trip.",
    points: [
      "Mapsie gift cards for your counter: visitors buy one, then map their whole holiday at home",
      "Bought from us at trade prices; you set the shelf price",
      "Printed, ready-to-sell cards with a QR code. We post them, or you print your own",
    ],
    image: "/partners/shop.webp",
  },
  {
    id: "corporate",
    title: "Corporate & client gifts",
    lead: "A gift that's actually personal.",
    points: [
      "Leaving and retirement gifts: a map of their travels or their home town",
      "Estate agents and relocation: “your new home” prints at completion",
      "Prepaid codes in bulk, invoiced, each recipient designs their own",
    ],
    image: "/partners/corporate.webp",
  },
];

const FAQ_ITEMS = [
  { q: "How does commission work?", a: "You get your own page and links (mapsie.shop/with/your-name) and, if you like, a discount code for your customers. Every order that comes through them earns you 10% of what the customer pays for the print, paid monthly by bank transfer. There's no cost to join." },
  { q: "What are prepaid codes?", a: `You buy codes in advance at a trade price and hand them out: in a finisher pack, a thank-you email or a client gift. Each code works like a gift card for any print. Trade prices are ${tradeDiscountPct(1)}% off, ${tradeDiscountPct(10)}% off for 10 or more and ${tradeDiscountPct(50)}% off for 50 or more, and we invoice you.` },
  { q: "Can you draw our route for us?", a: "Yes. Send us your itinerary or route (a list of stops, a GPX file or a map link) and we'll set it up in the style you choose. Your customers can still change anything." },
  { q: "How do gift cards work for shops?", a: "You buy cards from us at a trade price and sell them at whatever price you like. Each card has its own code and a QR code; your customer designs their map at home, enters the code at checkout and we deliver the print. Cards are valid for 2 years, and you can see how many have been used in your partner dashboard." },
  { q: "Where do you deliver?", a: "Prints are made to order and delivered free in the UK, the US and Australia, framed or unframed. Digital files are available everywhere." },
  { q: "Does it carry our branding?", a: "Your page is co-branded with your name. The print itself is about your customer's journey, so it has no logos unless they add one." },
];

export default function PartnersPage() {
  return (
    <div className="min-h-dvh overflow-x-hidden">
      <header className="max-w-6xl mx-auto px-6 py-5 flex justify-between items-center">
        <Link href="/" className="font-display text-3xl font-extrabold"><Logo /></Link>
        <div className="flex items-center gap-4">
          <Link href="/partner/signin" className="text-sm font-bold hover:text-coral-dark">Partner sign in</Link>
          <a href="#talk" className="rounded-full bg-ink text-white px-5 py-2.5 font-extrabold hover:bg-ink/85">Talk to us</a>
        </div>
      </header>
      <main>
        <section className="max-w-4xl mx-auto px-6 pt-6 pb-12 text-center">
          <p className="text-sm font-extrabold uppercase tracking-wider text-coral-dark">Mapsie for business</p>
          <h1 className="mt-3 font-display text-4xl sm:text-5xl font-extrabold leading-tight tracking-tight">Give your customers their journey, as a map for the wall</h1>
          <p className="mt-5 text-lg text-ink/70">
            Mapsie turns a route into a beautiful, personalised print: the real roads, rails and flight paths, their photos and their names.
            We draw your routes once. Your customers personalise and order in minutes, and you earn on every sale.
          </p>
          <div className="mt-8 flex flex-wrap justify-center gap-3">
            <a href="#talk" className="rounded-full bg-coral px-7 py-4 text-lg font-extrabold text-white shadow-xl shadow-coral/30 hover:bg-coral-dark">Become a partner →</a>
            <Link href="/create" className="rounded-full border-2 border-ink/15 px-6 py-3.5 font-extrabold hover:border-coral">Try the designer</Link>
          </div>
        </section>

        <section className="max-w-6xl mx-auto px-6 pb-8 grid sm:grid-cols-3 gap-4 text-center">
          {[
            ["1", "We set up your page", "Your routes, drawn and styled, at mapsie.shop/with/you"],
            ["2", "You share the link", "In your post-trip email, finisher pack or welcome letter"],
            ["3", "They design and order", "We print, frame and deliver. You earn commission, or use prepaid codes"],
          ].map(([n, t, d]) => (
            <div key={n} className="rounded-3xl bg-white p-6 shadow-sm">
              <div className="mx-auto grid h-10 w-10 place-items-center rounded-full bg-coral text-white font-extrabold">{n}</div>
              <div className="mt-3 font-extrabold text-lg">{t}</div>
              <div className="mt-1 text-ink/60">{d}</div>
            </div>
          ))}
        </section>

        {SEGMENTS.map((s, i) => (
          <section key={s.id} id={s.id} className="max-w-6xl mx-auto px-6 py-10 grid lg:grid-cols-2 gap-8 items-center">
            <img src={s.image} alt="" width={1000} height={750} loading="lazy" className={`w-full h-auto rounded-3xl shadow-lg ${i % 2 ? "lg:order-2" : ""}`} />
            <div>
              <h2 className="font-display text-3xl font-extrabold">{s.title}</h2>
              <p className="mt-2 text-lg text-ink/70">{s.lead}</p>
              <ul className="mt-5 space-y-3">
                {s.points.map((p) => (
                  <li key={p} className="flex gap-3"><span className="text-coral font-extrabold">✓</span><span className="text-ink/80">{p}</span></li>
                ))}
              </ul>
            </div>
          </section>
        ))}

        <section id="talk" className="bg-white/60 border-y border-ink/5">
          <div className="max-w-3xl mx-auto px-6 py-14">
            <h2 className="font-display text-3xl font-extrabold">Let&apos;s talk</h2>
            <p className="mt-2 text-ink/70">Tell us a little about what you do. We&apos;ll reply with a sample map of one of your routes.</p>
            <EnquiryForm />
          </div>
        </section>
        <Faq items={FAQ_ITEMS} />
      </main>
      <SiteFooter />
    </div>
  );
}
