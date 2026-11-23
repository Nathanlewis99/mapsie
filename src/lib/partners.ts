// Partner programme: tour operators, events, wedding registries and corporate gifting.
//  - A partner gets links that open the designer with their route already drawn
//    (mapsie.shop/with/<partner>), and earns commission on what their customers buy.
//  - Or they buy prepaid "trade codes" at a discount to give away (a finisher print,
//    a thank-you after a trip, a client gift); each code works like a gift card.
import type { TripTemplate } from "./templates";
import type { RegionId } from "./products";

export type PartnerKind = "travel" | "event" | "wedding" | "corporate" | "shop";
export const PARTNER_KINDS: { id: PartnerKind; label: string }[] = [
  { id: "travel", label: "Tour operator / travel agent" },
  { id: "event", label: "Event / challenge" },
  { id: "wedding", label: "Wedding / registry" },
  { id: "corporate", label: "Corporate gifting" },
  { id: "shop", label: "Gift / souvenir shop" },
];

/** Who to invoice for trade codes. Entered by the partner in their dashboard (or by us). */
export interface PartnerBilling { company: string; address: string; vatNumber?: string; invoiceEmail?: string }

/** How we pay their commission. Stored encrypted; `summary` is the safe-to-show version, e.g. "Bank ••••1234". */
export interface PartnerPayoutDetails { sealed: string; summary: string; updatedAt: string }
export type PayoutMethod =
  | { method: "uk_bank"; accountName: string; sortCode: string; accountNumber: string }
  | { method: "iban"; accountName: string; iban: string; bic?: string }
  | { method: "paypal"; email: string };

/** Check and tidy payout details typed by a partner. Returns an error message, or the cleaned details. */
export function cleanPayout(v: Record<string, string>): PayoutMethod | string {
  const t = (k: string, max = 80) => (v[k] ?? "").trim().slice(0, max);
  if (v.method === "uk_bank") {
    const sortCode = t("sortCode").replace(/\D/g, "");
    const accountNumber = t("accountNumber").replace(/\D/g, "");
    if (!t("accountName")) return "Add the name on the account";
    if (sortCode.length !== 6) return "A sort code has 6 digits";
    if (!/^\d{8}$/.test(accountNumber)) return "A UK account number has 8 digits";
    return { method: "uk_bank", accountName: t("accountName"), sortCode, accountNumber };
  }
  if (v.method === "iban") {
    const iban = t("iban", 40).replace(/\s/g, "").toUpperCase();
    if (!t("accountName")) return "Add the name on the account";
    if (!/^[A-Z]{2}\d{2}[A-Z0-9]{10,30}$/.test(iban)) return "That doesn't look like an IBAN";
    return { method: "iban", accountName: t("accountName"), iban, ...(t("bic", 11) ? { bic: t("bic", 11).toUpperCase() } : {}) };
  }
  if (v.method === "paypal") {
    if (!/^\S+@\S+\.\S+$/.test(t("email", 120))) return "Add the PayPal email address";
    return { method: "paypal", email: t("email", 120) };
  }
  return "Choose how you'd like to be paid";
}
export function payoutSummary(p: PayoutMethod) {
  if (p.method === "uk_bank") return `UK bank account ••••${p.accountNumber.slice(-4)} (${p.accountName})`;
  if (p.method === "iban") return `IBAN ${p.iban.slice(0, 2)}••••${p.iban.slice(-4)} (${p.accountName})`;
  return `PayPal ${p.email.replace(/^(.).*(@.*)$/, "$1•••$2")}`;
}

/** A route a partner's customers start from. Same shape as a quick-start trip, plus optional prompts. */
export interface PartnerTrip extends TripTemplate {
  /** Ask for these before opening the designer, and fill {name} / {detail} into the title and subtitle. */
  ask?: { name?: string; detail?: string };
}

export interface PartnerPayout { at: string; amount: number; currency: string; note?: string }

export interface Partner {
  id: string; // url slug: mapsie.shop/with/<id>
  name: string;
  kind: PartnerKind;
  active: boolean;
  contactEmail?: string;
  /** Shown on their landing page, e.g. "Thanks for riding with Coast Cycles!" */
  welcome?: string;
  /** % of what their customers pay for prints (excluding delivery). */
  commissionPct: number;
  /** Optional customer discount: a Stripe promotion code (e.g. COASTCYCLES10) for this % off. */
  discountPct?: number;
  promoCode?: string;
  promoId?: string;
  couponId?: string;
  region?: RegionId;
  trips: PartnerTrip[];
  payouts?: PartnerPayout[];
  /** Email addresses that can sign in to the partner dashboard (mapsie.shop/partner). */
  logins?: string[];
  billing?: PartnerBilling;
  payoutDetails?: PartnerPayoutDetails;
  /** Maps the partner designed themselves: to order in bulk, or to sell on their page as they are. */
  designs?: PartnerDesign[];
  /** Stripe invoices sent for trade code batches. */
  invoices?: { batch: string; url?: string | null; total: number; currency: string; at: string }[];
  notes?: string;
  /** Self sign-up: pending until approved in admin. Partners we add ourselves have no status (approved). */
  status?: "pending" | "approved" | "denied";
  application?: PartnerApplication;
  createdAt: string;
}

export interface PartnerDesign { id: string; name: string; published: boolean; addedAt: string }

export interface PartnerApplication {
  contactName: string;
  email: string;
  website: string;
  message: string;
  volume?: string;
  appliedAt: string;
  checks: PartnerCheck[];
  recommendation: "approve" | "review" | "deny";
  decidedAt?: string;
  decision?: "approved" | "denied";
  /** A short reason, included in the email if denied. */
  decisionNote?: string;
}
export interface PartnerCheck { ok: boolean | null; label: string }

/** What we found out about an application (see server/partnerApply.ts). */
export interface ApplicationFacts {
  website: { reachable: boolean; title?: string; nameOnSite?: boolean; finalHost?: string };
  duplicateOf?: string;
}

const FREE_EMAIL = /^(gmail|googlemail|hotmail|outlook|live|msn|yahoo|ymail|icloud|me|mac|aol|proton|protonmail|gmx|mail|zoho|yandex|btinternet|sky|virginmedia|talktalk)\./i;
export const hostOf = (url: string) => {
  try {
    return new URL(/^https?:\/\//i.test(url) ? url : `https://${url}`).hostname.toLowerCase().replace(/^www\./, "");
  } catch {
    return "";
  }
};
/** example.co.uk from shop.example.co.uk (good enough for matching an email to a website). */
export const baseDomain = (host: string) => {
  const parts = host.toLowerCase().replace(/^www\./, "").split(".");
  const two = /^(co|org|ac|gov|com|net)\.[a-z]{2}$/.test(parts.slice(-2).join("."));
  return parts.slice(two ? -3 : -2).join(".");
};

/** Turn what we found into checks and a recommendation. Pure, so it's easy to test. */
export function assessApplication(a: { company: string; email: string; website: string }, f: ApplicationFacts): Pick<PartnerApplication, "checks" | "recommendation"> {
  const emailDomain = a.email.split("@")[1]?.toLowerCase() ?? "";
  const site = hostOf(a.website);
  const free = FREE_EMAIL.test(emailDomain);
  const sameDomain = !!site && baseDomain(emailDomain) === baseDomain(f.website.finalHost || site);
  const checks: PartnerCheck[] = [
    { ok: true, label: "Email address confirmed (they clicked the link we sent)" },
    { ok: sameDomain, label: sameDomain ? `Email is on their website's domain (${baseDomain(emailDomain)})` : free ? `Personal email (${emailDomain}), not on their website's domain` : `Email domain (${emailDomain}) differs from the website (${site || "none"})` },
    { ok: f.website.reachable, label: f.website.reachable ? `Website is live${f.website.title ? `: “${f.website.title.slice(0, 80)}”` : ""}` : `Website didn't load (${site || "none given"})` },
    { ok: f.website.reachable ? !!f.website.nameOnSite : null, label: f.website.nameOnSite ? `“${a.company}” appears on the website` : `Couldn't find “${a.company}” on the website's home page` },
    { ok: !f.duplicateOf, label: f.duplicateOf ? `Same email or domain as existing partner “${f.duplicateOf}”` : "Not a duplicate of an existing partner" },
  ];
  const recommendation = f.duplicateOf || !f.website.reachable ? (f.duplicateOf ? "deny" : "review") : sameDomain && f.website.nameOnSite ? "approve" : "review";
  return { checks, recommendation };
}

/** Public view of a partner (no commission, contacts or notes). */
export type PublicPartner = Pick<Partner, "id" | "name" | "kind" | "welcome" | "trips" | "promoCode" | "discountPct" | "region"> & { designs: { id: string; name: string }[] };
export const publicPartner = (p: Partner): PublicPartner => ({
  id: p.id,
  name: p.name,
  kind: p.kind,
  welcome: p.welcome,
  trips: p.trips,
  promoCode: p.promoCode,
  discountPct: p.discountPct,
  region: p.region,
  designs: (p.designs ?? []).filter((d) => d.published).map((d) => ({ id: d.id, name: d.name })),
});

export const PARTNER_ID = /^[a-z0-9][a-z0-9-]{1,38}[a-z0-9]$/;
export const slugify = (s: string) =>
  s.toLowerCase().normalize("NFKD").replace(/[̀-ͯ]/g, "").replace(/&/g, " and ").replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "").slice(0, 40);

/** The link a partner shares; with a trip it opens the designer straight on that route. */
export function partnerLink(base: string, partnerId: string, tripId?: string) {
  return `${base}/with/${partnerId}${tripId ? `?trip=${encodeURIComponent(tripId)}` : ""}`;
}

/** Fill a personalised name and detail (finish time, wedding date...) into a trip's title and subtitle. */
export function personaliseTrip(t: PartnerTrip, name?: string, detail?: string): PartnerTrip {
  const clean = (s?: string) => (s ?? "").replace(/[<>{}]/g, "").trim().slice(0, 60);
  const fill = (s: string) =>
    s
      .replace(/\{name\}/g, clean(name))
      .replace(/\{detail\}/g, clean(detail))
      .replace(/\s*·\s*(·\s*)+/g, " · ")
      .replace(/^\s*·\s*|\s*·\s*$/g, "")
      .trim();
  return { ...t, title: fill(t.title) || t.name, subtitle: fill(t.subtitle) };
}

/** What a partner earns on one order: commission on the price paid, less delivery. */
export function commissionFor(p: Pick<Partner, "commissionPct">, paid: number, delivery: number) {
  return Math.max(0, Math.round((paid - delivery) * p.commissionPct) / 100);
}

/** Trade price per prepaid code: the code's value less a volume discount. */
export function tradeDiscountPct(count: number) {
  return count >= 50 ? 25 : count >= 10 ? 20 : 15;
}
export function tradePrice(value: number, count: number) {
  return Math.round(value * (100 - tradeDiscountPct(count))) / 100;
}

/** "Edinburgh; Inverness (car); Skye (boat)" → names and how they arrived (for the admin trip builder). */
const MODES = ["plane", "car", "bus", "train", "boat", "walk", "tuktuk", "moped"] as const;
export function parseStopList(s: string): { name: string; mode?: (typeof MODES)[number] }[] {
  return s
    .split(/[;\n]/)
    .map((x) => x.trim())
    .filter(Boolean)
    .slice(0, 40)
    .map((x) => {
      const m = x.match(/^(.*?)\s*\((\w+)\)\s*$/);
      const mode = m && (MODES as readonly string[]).includes(m[2].toLowerCase()) ? (m[2].toLowerCase() as (typeof MODES)[number]) : undefined;
      return { name: (m && mode ? m[1] : x).slice(0, 80), ...(mode ? { mode } : {}) };
    });
}
