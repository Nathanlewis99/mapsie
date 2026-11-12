import Link from "next/link";
import { COMPANY } from "@/lib/company";

export const LEGAL_LINKS = [
  { href: "/legal/terms", label: "Terms & Conditions" },
  { href: "/legal/privacy", label: "Privacy Policy" },
  { href: "/legal/refunds", label: "Returns & Refunds" },
  { href: "/legal/shipping", label: "Shipping & Delivery" },
  { href: "/legal/cookies", label: "Cookies" },
] as const;

export default function SiteFooter() {
  return (
    <footer className="border-t border-ink/10 mt-8">
      <div className="max-w-6xl mx-auto px-6 py-10 text-sm text-ink/60">
        <nav aria-label="Legal" className="flex flex-wrap gap-x-6 gap-y-2 font-bold text-ink/80">
          {LEGAL_LINKS.map((l) => (
            <Link key={l.href} href={l.href} className="hover:text-coral-dark">
              {l.label}
            </Link>
          ))}
          <a href={`mailto:${COMPANY.supportEmail}`} className="hover:text-coral-dark">
            Contact us
          </a>
        </nav>
        <p className="mt-6 max-w-3xl leading-relaxed">
          © {new Date().getFullYear()} {COMPANY.legalName}. {COMPANY.brand} is a trading name of {COMPANY.legalName}, registered in{" "}
          {COMPANY.jurisdiction}, company no. {COMPANY.number}. Registered office: {COMPANY.address}.
        </p>
        <p className="mt-3 text-xs text-ink/50 leading-relaxed">
          Map data ©{" "}
          <a href="https://www.openstreetmap.org/copyright" className="underline underline-offset-2 hover:text-ink">
            OpenStreetMap contributors
          </a>{" "}
          (ODbL) · Map tiles by{" "}
          <a href="https://openfreemap.org" className="underline underline-offset-2 hover:text-ink">
            OpenFreeMap
          </a>{" "}
          · Stickers include{" "}
          <a href="https://github.com/jdecked/twemoji" className="underline underline-offset-2 hover:text-ink">
            Twemoji
          </a>{" "}
          (CC-BY 4.0) and{" "}
          <a href="https://github.com/microsoft/fluentui-emoji" className="underline underline-offset-2 hover:text-ink">
            Microsoft Fluent Emoji
          </a>{" "}
          (MIT)
        </p>
      </div>
    </footer>
  );
}
