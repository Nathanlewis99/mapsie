import Link from "next/link";
import Logo from "@/components/Logo";
import type { ReactNode } from "react";
import { COMPANY } from "@/lib/company";
import SiteFooter, { LEGAL_LINKS } from "@/components/SiteFooter";

// Typography for the long-form legal text, scoped to the article only.
const PROSE = [
  "text-[1.0625rem] leading-relaxed text-ink/85",
  "[&_p]:mt-4",
  "[&_ul]:mt-4 [&_ul]:list-disc [&_ul]:pl-6 [&_ol]:mt-4 [&_ol]:list-decimal [&_ol]:pl-6",
  "[&_li]:mt-2 [&_li]:pl-1 [&_li::marker]:text-coral",
  "[&_strong]:font-extrabold [&_strong]:text-ink",
  "[&_a]:font-semibold [&_a]:text-ink [&_a]:underline [&_a]:decoration-coral [&_a]:decoration-2 [&_a]:underline-offset-[3px] [&_a:hover]:text-coral-dark",
  "[&_address]:not-italic",
].join(" ");

export default function LegalLayout({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-dvh flex flex-col bg-cream text-ink">
      <header className="max-w-6xl w-full mx-auto px-4 sm:px-6 py-5 flex justify-between items-center gap-4">
        <Link href="/" className="font-display text-3xl font-extrabold" aria-label={`${COMPANY.brand} home`}>
          <Logo />
          <span className="text-coral">.</span>
        </Link>
        <Link href="/create" className="rounded-full bg-ink text-white px-4 sm:px-5 py-2.5 text-sm sm:text-base font-extrabold hover:bg-ink/85">
          Start designing
        </Link>
      </header>

      <div className="max-w-6xl w-full mx-auto px-4 sm:px-6 pb-16 pt-4 grid gap-8 lg:grid-cols-[14rem_minmax(0,1fr)] lg:gap-14 flex-1">
        <aside className="lg:pt-3">
          <nav aria-label="Legal pages" className="lg:sticky lg:top-6">
            <Link href="/legal" className="text-xs font-extrabold uppercase tracking-wider text-coral hover:text-coral-dark">
              Legal &amp; policies
            </Link>
            <ul className="mt-3 flex flex-wrap gap-2 lg:flex-col lg:gap-1">
              {LEGAL_LINKS.map((l) => (
                <li key={l.href}>
                  <Link
                    href={l.href}
                    className="block rounded-full bg-white px-3.5 py-1.5 text-sm font-bold text-ink/75 shadow-sm hover:text-ink lg:rounded-xl lg:bg-transparent lg:px-3 lg:py-2 lg:shadow-none lg:hover:bg-white"
                  >
                    {l.label}
                  </Link>
                </li>
              ))}
            </ul>
            <p className="mt-5 text-xs text-ink/50 lg:px-3">
              Questions?{" "}
              <a href={`mailto:${COMPANY.supportEmail}`} className="font-bold text-ink/70 underline underline-offset-2 hover:text-ink">
                {COMPANY.supportEmail}
              </a>
            </p>
          </nav>
        </aside>

        <main className="min-w-0">
          <article className={`max-w-[70ch] ${PROSE}`}>
            <p className="mt-0! mb-3 text-sm font-bold text-ink/50">Last updated: {COMPANY.legalUpdated}</p>
            {children}
          </article>
        </main>
      </div>

      <SiteFooter />
    </div>
  );
}
