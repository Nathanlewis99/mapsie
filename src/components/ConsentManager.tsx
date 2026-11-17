"use client";
import { useEffect, useRef, useState } from "react";
import { usePathname } from "next/navigation";
import Link from "next/link";
import { readConsent, saveConsent, type Consent } from "@/lib/consent";

type Config = { metaPixel: string | null; ga4: string | null; googleAds: string | null; adsPurchaseLabel: string | null };

// Loads Google (Analytics and Ads, with Consent Mode) and the Meta Pixel only after
// the visitor agrees, and shows the cookie banner. With no IDs set on Render there are
// no optional cookies, so no banner either.
function loadScript(src: string) {
  if (document.querySelector(`script[src="${src}"]`)) return;
  const s = document.createElement("script");
  s.src = src;
  s.async = true;
  document.head.appendChild(s);
}

function startGoogle(cfg: Config, c: Consent) {
  const ids = [c.analytics && cfg.ga4, c.ads && cfg.googleAds].filter(Boolean) as string[];
  if (!ids.length) return;
  const w = window as unknown as { dataLayer: unknown[] };
  w.dataLayer = w.dataLayer || [];
  if (!window.gtag) {
    window.gtag = function gtag() {
      // eslint-disable-next-line prefer-rest-params
      w.dataLayer.push(arguments);
    };
    window.gtag("consent", "default", { analytics_storage: "denied", ad_storage: "denied", ad_user_data: "denied", ad_personalization: "denied" });
    window.gtag("js", new Date());
  }
  window.gtag("consent", "update", {
    analytics_storage: c.analytics ? "granted" : "denied",
    ad_storage: c.ads ? "granted" : "denied",
    ad_user_data: c.ads ? "granted" : "denied",
    ad_personalization: c.ads ? "granted" : "denied",
  });
  // Page views are sent on each navigation by the component below.
  for (const id of ids) window.gtag("config", id, { send_page_view: false });
  window.__mapsieAds = c.ads && cfg.googleAds ? { googleAds: cfg.googleAds, adsPurchaseLabel: cfg.adsPurchaseLabel ?? undefined } : undefined;
  loadScript(`https://www.googletagmanager.com/gtag/js?id=${encodeURIComponent(ids[0])}`);
}

function startMeta(pixel: string) {
  if (window.fbq) return;
  const q: unknown[] = [];
  const fbq = ((...args: unknown[]) => {
    const f = window.fbq as unknown as { callMethod?: (...a: unknown[]) => void };
    if (f.callMethod) f.callMethod(...args);
    else q.push(args);
  }) as Window["fbq"] & { queue: unknown[]; push: unknown; loaded: boolean; version: string };
  fbq.queue = q;
  fbq.push = fbq;
  fbq.loaded = true;
  fbq.version = "2.0";
  window.fbq = fbq;
  (window as unknown as { _fbq: unknown })._fbq = fbq;
  loadScript("https://connect.facebook.net/en_US/fbevents.js");
  fbq("init", pixel);
}

export default function ConsentManager() {
  const [cfg, setCfg] = useState<Config | null>(null);
  const [consent, setConsent] = useState<Consent | null>(null);
  const [open, setOpen] = useState(false);
  const [choosing, setChoosing] = useState(false);
  const [analytics, setAnalytics] = useState(false);
  const [ads, setAds] = useState(false);
  const started = useRef({ google: false, meta: false });
  const pathname = usePathname();

  useEffect(() => {
    fetch("/api/site-config")
      .then((r) => r.json())
      .then((c: Config) => {
        if (!c.metaPixel && !c.ga4 && !c.googleAds) return;
        setCfg(c);
        const saved = readConsent();
        setConsent(saved);
        // Global Privacy Control means "don't track me": no banner, nothing loads, unless they open settings.
        const gpc = (navigator as unknown as { globalPrivacyControl?: boolean }).globalPrivacyControl === true;
        if (!saved && !gpc && !location.pathname.startsWith("/print/")) setOpen(true);
      })
      .catch(() => {});
    const reopen = () => {
      const c = readConsent();
      setAnalytics(!!c?.analytics);
      setAds(!!c?.ads);
      setChoosing(true);
      setOpen(true);
    };
    window.addEventListener("mapsie:consent-open", reopen);
    return () => window.removeEventListener("mapsie:consent-open", reopen);
  }, []);

  // Start whatever the visitor agreed to.
  useEffect(() => {
    if (!cfg || !consent) return;
    if ((consent.analytics && cfg.ga4) || (consent.ads && cfg.googleAds)) {
      startGoogle(cfg, consent);
      started.current.google = true;
    } else if (window.gtag) {
      window.gtag("consent", "update", { analytics_storage: "denied", ad_storage: "denied", ad_user_data: "denied", ad_personalization: "denied" });
    }
    if (consent.ads && cfg.metaPixel && !started.current.meta) {
      startMeta(cfg.metaPixel);
      started.current.meta = true;
    }
    if (!consent.ads && window.fbq) window.fbq("consent", "revoke");
    if (consent.ads && window.fbq && started.current.meta) window.fbq("consent", "grant");
  }, [cfg, consent]);

  // A page view on every navigation (the site changes pages without full reloads).
  useEffect(() => {
    if (!consent || pathname.startsWith("/print/")) return;
    const t = setTimeout(() => {
      if (consent.analytics || consent.ads) window.gtag?.("event", "page_view", { page_path: pathname, page_location: location.href });
      if (consent.ads) window.fbq?.("track", "PageView");
    }, 50);
    return () => clearTimeout(t);
  }, [pathname, consent]);

  const decide = (a: boolean, d: boolean) => {
    setConsent(saveConsent(a, d));
    setOpen(false);
    setChoosing(false);
  };

  if (!cfg || !open) return null;
  return (
    <div role="dialog" aria-label="Cookie choices" className="fixed inset-x-3 bottom-3 z-[60] mx-auto max-w-xl rounded-3xl bg-white p-5 shadow-2xl border border-ink/10 text-sm space-y-3">
      <div className="font-extrabold text-base">🍪 Cookies</div>
      <p className="text-ink/70">
        We&apos;d like to use cookies to see how people find Mapsie (Google Analytics) and to measure our ads on Instagram, Facebook
        and Google. They&apos;re optional and off unless you say yes. <Link href="/legal/cookies" className="underline font-bold">Details</Link>
      </p>
      {choosing && (
        <div className="space-y-2 rounded-2xl bg-sand/50 p-3">
          <label className="flex items-start gap-2"><input type="checkbox" checked disabled className="mt-1" /><span><b>Essential</b>: sign-in and saving your design. Always on.</span></label>
          {cfg.ga4 && <label className="flex items-start gap-2"><input type="checkbox" checked={analytics} onChange={(e) => setAnalytics(e.target.checked)} className="mt-1 accent-coral" /><span><b>Analytics</b>: Google Analytics, to see which pages help and which confuse.</span></label>}
          {(cfg.metaPixel || cfg.googleAds) && <label className="flex items-start gap-2"><input type="checkbox" checked={ads} onChange={(e) => setAds(e.target.checked)} className="mt-1 accent-coral" /><span><b>Advertising</b>: Meta and Google, to measure which ads lead to orders and show our ads to people likely to want them.</span></label>}
        </div>
      )}
      <div className="flex flex-wrap gap-2">
        <button onClick={() => decide(!!cfg.ga4, !!(cfg.metaPixel || cfg.googleAds))} className="rounded-full bg-coral px-4 py-2 font-extrabold text-white">Accept all</button>
        <button onClick={() => decide(false, false)} className="rounded-full border-2 border-ink/15 px-4 py-2 font-extrabold">Reject all</button>
        {choosing ? (
          <button onClick={() => decide(analytics && !!cfg.ga4, ads)} className="rounded-full border-2 border-ink/15 px-4 py-2 font-extrabold">Save my choices</button>
        ) : (
          <button onClick={() => { const c = readConsent(); setAnalytics(!!c?.analytics); setAds(!!c?.ads); setChoosing(true); }} className="rounded-full px-3 py-2 font-bold underline text-ink/60">Choose</button>
        )}
      </div>
    </div>
  );
}
