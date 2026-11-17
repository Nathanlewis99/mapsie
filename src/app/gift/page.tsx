import type { Metadata } from "next";
import Link from "next/link";
import Logo from "@/components/Logo";
import SiteFooter from "@/components/SiteFooter";
import ChristmasBanner from "@/components/ChristmasBanner";
import JsonLd from "@/components/seo/JsonLd";
import { Faq } from "@/components/seo/Sections";
import { faqJsonLd } from "@/lib/seo";
import { GIFT_VALID_YEARS } from "@/lib/giftcards";
import GiftForm from "./GiftForm";

export const metadata: Metadata = {
  title: "Travel Map Gift Card: Let Them Design Their Own | Mapsie",
  description: "A Mapsie gift card lets them turn their favourite trip into a custom map print. Emailed instantly or on the day you choose, or print it yourself.",
  alternates: { canonical: "/gift" },
};

const GIFT_FAQ = [
  { q: "How does the gift card work?", a: "You choose an amount and add a message. We email you a gift card with a code, which you can print, forward, or have us send to them on a date you choose (Christmas morning, say). They design their map whenever they like and enter the code at checkout." },
  { q: "What if their order costs less than the card?", a: "Nothing is lost: any amount left over is emailed to them as a new code for their next map." },
  { q: "How long does it last?", a: `${GIFT_VALID_YEARS} years from the day you buy it.` },
  { q: "Is it too late for Christmas?", a: "Never: the gift card arrives by email straight away (or on the day you choose), so it's the perfect last-minute present." },
];

export default function GiftPage() {
  return (
    <div className="min-h-dvh">
      <ChristmasBanner />
      <header className="max-w-6xl mx-auto px-6 py-5 flex justify-between items-center">
        <Link href="/" className="font-display text-3xl font-extrabold"><Logo /></Link>
        <Link href="/create" className="rounded-full bg-ink text-white px-5 py-2.5 font-extrabold">Design a map</Link>
      </header>
      <main>
        <section className="max-w-6xl mx-auto px-6 pt-6 pb-12 grid lg:grid-cols-[1fr_1fr] gap-10 items-start">
          <div>
            <h1 className="font-display text-4xl sm:text-5xl font-extrabold leading-tight">Give them a map of their favourite trip</h1>
            <p className="mt-5 text-lg text-ink/70">
              Not sure exactly where they went, or which style they&apos;d love? A Mapsie gift card lets them design their own map print:
              every stop, the route, stickers and their own photos. Sent by email in seconds, or on the day you choose.
            </p>
            <ul className="mt-6 space-y-2 text-ink/80">
              <li>🎁 Emailed to you or straight to them, even on Christmas morning</li>
              <li>🖨️ A printable card to put in an envelope</li>
              <li>💸 Any leftover balance is kept for their next map</li>
            </ul>
            <img src="/examples/sri-lanka.webp" alt="A framed custom travel map print of a trip to Sri Lanka" width={1200} height={900} className="mt-8 w-full h-auto rounded-3xl shadow-xl hidden lg:block" />
          </div>
          <GiftForm />
        </section>
        <Faq items={GIFT_FAQ} />
      </main>
      <SiteFooter />
      <JsonLd data={faqJsonLd(GIFT_FAQ)} />
    </div>
  );
}
