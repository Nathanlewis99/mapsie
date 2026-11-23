"use client";
import { useState } from "react";
import { PARTNER_KINDS } from "@/lib/partners";
import { REGIONS } from "@/lib/products";

const field = "mt-1 w-full rounded-xl border border-ink/15 bg-white px-3 py-2.5";

export default function ApplyForm() {
  const [state, setState] = useState<"idle" | "sending" | "sent" | "error">("idle");
  const [err, setErr] = useState("");
  const [email, setEmail] = useState("");
  const submit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setState("sending");
    const body = Object.fromEntries(new FormData(e.currentTarget));
    const r = await fetch("/api/partners/apply", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(body) }).catch(() => null);
    if (r?.ok) return setState("sent");
    setErr((await r?.json().catch(() => null))?.error ?? "Sorry, that didn't send. Please email hello@mapsie.shop.");
    setState("error");
  };
  if (state === "sent")
    return <p className="mt-6 rounded-2xl bg-sand px-5 py-4 font-bold">Nearly done: we&apos;ve emailed a link to {email}. Click it to confirm your address and send your application.</p>;
  return (
    <form onSubmit={submit} className="mt-6 grid sm:grid-cols-2 gap-4">
      <label className="font-bold text-sm">Organisation<input name="company" required maxLength={80} className={field} /></label>
      <label className="font-bold text-sm">Website<input name="website" required maxLength={200} placeholder="yourcompany.com" className={field} /></label>
      <label className="font-bold text-sm">Your name<input name="contactName" required maxLength={80} className={field} /></label>
      <label className="font-bold text-sm">Work email<input name="email" type="email" required maxLength={120} value={email} onChange={(e) => setEmail(e.target.value)} className={field} /></label>
      <label className="font-bold text-sm">What you do
        <select name="kind" className={field} defaultValue="travel">{PARTNER_KINDS.map((k) => <option key={k.id} value={k.id}>{k.label}</option>)}</select>
      </label>
      <label className="font-bold text-sm">Your customers are mostly in
        <select name="region" className={field} defaultValue="GB">{REGIONS.map((r) => <option key={r.id} value={r.id}>{r.label}</option>)}</select>
      </label>
      <label className="font-bold text-sm sm:col-span-2">Roughly how many customers a year? (optional)<input name="volume" maxLength={120} placeholder="e.g. 800 guests, 1,200 riders, a busy shop on the Royal Mile" className={field} /></label>
      <label className="font-bold text-sm sm:col-span-2">How would you use Mapsie?
        <textarea name="message" rows={4} maxLength={1500} className={field} placeholder="e.g. A link in our welcome-home email for our 12 Scotland self-drive tours" />
      </label>
      <input name="company_url" tabIndex={-1} autoComplete="off" className="hidden" aria-hidden />
      <p className="sm:col-span-2 text-xs text-ink/50">A work email on your website&apos;s domain gets you approved fastest. We&apos;ll use these details to review your application and run your partner account (see our <a href="/legal/privacy" className="underline">privacy policy</a>).</p>
      <div className="sm:col-span-2 flex items-center gap-4">
        <button disabled={state === "sending"} className="rounded-full bg-coral px-7 py-3.5 font-extrabold text-white shadow-lg shadow-coral/30 hover:bg-coral-dark disabled:opacity-60">{state === "sending" ? "Sending…" : "Apply"}</button>
        {state === "error" && <span className="text-sm font-bold text-coral-dark">{err}</span>}
      </div>
    </form>
  );
}
