// Small building blocks shared by the legal pages. Next.js only routes
// page.tsx / route.ts files, so this module never becomes a page.
import Link from "next/link";
import type { ReactNode } from "react";

export function LegalTitle({ title, intro }: { title: string; intro?: ReactNode }) {
  return (
    <header className="mb-10">
      <h1 className="font-display text-4xl sm:text-5xl font-extrabold leading-tight tracking-tight">{title}</h1>
      {intro && <div className="mt-4 text-lg text-ink/70">{intro}</div>}
    </header>
  );
}

/** A numbered section with an anchor, e.g. /legal/terms#ordering */
export function Section({ id, n, title, children }: { id: string; n?: number | string; title: string; children: ReactNode }) {
  return (
    <section id={id} className="mt-12 scroll-mt-6">
      <h2 className="font-display text-2xl sm:text-[1.7rem] font-extrabold leading-snug">
        {n !== undefined && <span className="text-coral mr-2">{n}.</span>}
        {title}
      </h2>
      {children}
    </section>
  );
}

export function Sub({ title, children }: { title: string; children: ReactNode }) {
  return (
    <>
      <h3 className="mt-7 text-lg font-extrabold text-ink">{title}</h3>
      {children}
    </>
  );
}

/** A friendly "in short" panel at the top of a page. */
export function Summary({ children }: { children: ReactNode }) {
  return (
    <div className="rounded-3xl bg-white p-6 shadow-sm border border-ink/5">
      <div className="text-xs font-extrabold uppercase tracking-wider text-coral">In short</div>
      <div className="[&>ul]:mt-3">{children}</div>
    </div>
  );
}

/** Clearly visible placeholder for something the owner must confirm before launch. */
export function Todo({ children }: { children: ReactNode }) {
  return (
    <mark className="rounded bg-yellow-200 px-1.5 py-0.5 text-ink not-italic font-semibold">
      [TODO: {children}]
    </mark>
  );
}

export function Email({ to }: { to: string }) {
  return <a href={`mailto:${to}`}>{to}</a>;
}

export function In({ href, children }: { href: string; children: ReactNode }) {
  return <Link href={href}>{children}</Link>;
}

export function Ext({ href, children }: { href: string; children: ReactNode }) {
  return (
    <a href={href} target="_blank" rel="noopener noreferrer">
      {children}
    </a>
  );
}

/** Simple responsive table: scrolls inside its own box on narrow screens. */
export function Table({ head, rows }: { head: string[]; rows: ReactNode[][] }) {
  return (
    <div className="mt-5 overflow-x-auto rounded-2xl border border-ink/10 bg-white">
      <table className="w-full text-left text-[0.95rem] leading-snug">
        <thead className="bg-sand/60">
          <tr>
            {head.map((h) => (
              <th key={h} scope="col" className="px-4 py-3 font-extrabold align-bottom">
                {h}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((r, i) => (
            <tr key={i} className="border-t border-ink/10 align-top">
              {r.map((c, j) => (
                <td key={j} className="px-4 py-3 [&_p]:mt-0">
                  {c}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
