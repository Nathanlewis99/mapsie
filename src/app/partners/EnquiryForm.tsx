"use client";
import { useState } from "react";
import { PARTNER_KINDS } from "@/lib/partners";

const field = "mt-1 w-full rounded-xl border border-ink/15 bg-white px-3 py-2.5";

export default function EnquiryForm() {
  const [state, setState] = useState<"idle" | "sending" | "sent" | "error">("idle");
  const [err, setErr] = useState("");
  const submit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setState("sending");
    const body = Object.fromEntries(new FormData(e.currentTarget));
    const r = await fetch("/api/partners/enquire", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(body) }).catch(() => null);
    if (r?.ok) return setState("sent");
    setErr((await r?.json().catch(() => null))?.error ?? "Sorry, that didn't send. Please email us instead.");
    setState("error");
  };
  if (state === "sent") return <p className="mt-6 rounded-2xl bg-sand px-5 py-4 font-bold">Thank you! We&apos;ll be in touch soon.</p>;
  return (
    <form onSubmit={submit} className="mt-6 grid sm:grid-cols-2 gap-4">
      <label className="font-bold text-sm">Your name<input name="name" required maxLength={80} className={field} /></label>
      <label className="font-bold text-sm">Email<input name="email" type="email" required maxLength={120} className={field} /></label>
      <label className="font-bold text-sm">Organisation<input name="org" required maxLength={120} className={field} /></label>
      <label className="font-bold text-sm">Website<input name="website" maxLength={200} placeholder="https://" className={field} /></label>
      <label className="font-bold text-sm sm:col-span-2">What you do
        <select name="kind" className={field} defaultValue="travel">{PARTNER_KINDS.map((k) => <option key={k.id} value={k.id}>{k.label}</option>)}<option value="other">Something else</option></select>
      </label>
      <label className="font-bold text-sm sm:col-span-2">Tell us about your routes or customers (optional)
        <textarea name="message" rows={4} maxLength={2000} className={field} placeholder="e.g. We run 12 self-drive Scotland tours and send around 800 guests a year" />
      </label>
      {/* Left empty by people; bots fill it in. */}
      <input name="company_url" tabIndex={-1} autoComplete="off" className="hidden" aria-hidden />
      <div className="sm:col-span-2 flex items-center gap-4">
        <button disabled={state === "sending"} className="rounded-full bg-coral px-7 py-3.5 font-extrabold text-white shadow-lg shadow-coral/30 hover:bg-coral-dark disabled:opacity-60">{state === "sending" ? "Sending…" : "Send"}</button>
        {state === "error" && <span className="text-sm font-bold text-coral-dark">{err}</span>}
      </div>
    </form>
  );
}
