import type { Metadata } from "next";
import Link from "next/link";
import { COMPANY } from "@/lib/company";
import { Email, LegalTitle } from "./_ui";

export const metadata: Metadata = {
  title: "Legal & policies · Mapsie",
  description: `Terms, privacy, refunds, shipping and cookie policies for Mapsie, run by ${COMPANY.legalName}.`,
};

const PAGES = [
  { href: "/legal/terms", title: "Terms & Conditions", text: "The agreement between you and us when you use Mapsie or buy a print: ordering, payment, your content, and your rights." },
  { href: "/legal/refunds", title: "Returns, Refunds & Reprints", text: "What happens if your print arrives damaged or isn't right, how to cancel, and why we can't take change-of-mind returns." },
  { href: "/legal/shipping", title: "Shipping & Delivery", text: "Where we deliver, how long it takes, what it costs, and customs." },
  { href: "/legal/privacy", title: "Privacy Policy", text: "What personal information we collect, why, who we share it with, how long we keep it, and your rights." },
  { href: "/legal/cookies", title: "Cookies & Local Storage", text: "The small amount of essential storage we use (and the tracking we don't)." },
];

export default function LegalIndex() {
  return (
    <>
      <LegalTitle
        title="Legal & policies"
        intro={
          <>
            {COMPANY.brand} is run by {COMPANY.legalName}. We&apos;ve tried to keep these pages short, clear and honest. If anything
            doesn&apos;t make sense, just ask.
          </>
        }
      />
      <ul className="mt-0! list-none! pl-0! grid gap-4">
        {PAGES.map((p) => (
          <li key={p.href} className="mt-0! pl-0!">
            <Link
              href={p.href}
              className="block rounded-3xl bg-white p-6 no-underline! shadow-sm border border-ink/5 hover:border-coral/40 hover:-translate-y-0.5 transition"
            >
              <span className="font-display text-xl font-extrabold">{p.title} →</span>
              <span className="mt-1 block font-normal text-ink/65">{p.text}</span>
            </Link>
          </li>
        ))}
      </ul>

      <h2 className="mt-12 font-display text-2xl font-extrabold">Who we are</h2>
      <address className="mt-4">
        <strong>{COMPANY.legalName}</strong> (trading as {COMPANY.brand})
        <br />
        Registered in {COMPANY.jurisdiction}, company no. {COMPANY.number}
        <br />
        Registered office: {COMPANY.address}
      </address>
      <p>
        Orders and general questions: <Email to={COMPANY.supportEmail} />
        <br />
        Privacy and data requests: <Email to={COMPANY.privacyEmail} />
      </p>
    </>
  );
}
