"use client";
import { useEffect, useState } from "react";
import { giftAmounts, GIFT_MAX, GIFT_MIN } from "@/lib/giftcards";
import { getRegion, guessRegion, REGIONS, type RegionId } from "@/lib/products";
import { attribution } from "@/lib/track";

const field = "w-full rounded-2xl border-2 border-ink/10 bg-white px-4 py-3 font-semibold outline-none focus:border-coral";

export default function GiftForm() {
  const [region, setRegion] = useState<RegionId>("GB");
  const [amount, setAmount] = useState<number | null>(null);
  const [custom, setCustom] = useState("");
  const [fromName, setFromName] = useState("");
  const [recipientName, setRecipientName] = useState("");
  const [message, setMessage] = useState("");
  const [buyerEmail, setBuyerEmail] = useState("");
  const [toThem, setToThem] = useState(false);
  const [recipientEmail, setRecipientEmail] = useState("");
  const [sendOn, setSendOn] = useState("");
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");
  useEffect(() => setRegion(guessRegion()), []);
  const options = giftAmounts(region);
  useEffect(() => setAmount(options[2].amount), [region]); // eslint-disable-line react-hooks/exhaustive-deps
  const r = getRegion(region);
  const value = custom ? Math.round(Number(custom)) : amount ?? 0;
  const today = new Date().toISOString().slice(0, 10);

  const buy = async () => {
    setBusy(true);
    setErr("");
    const res = await fetch("/api/gift/checkout", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ amount: value, region, buyerEmail, fromName, recipientName, message, ...(toThem ? { recipientEmail, sendOn } : {}), attribution: attribution() }),
    });
    const j = await res.json().catch(() => ({}));
    if (!res.ok) return setErr(j.error ?? "Something went wrong"), setBusy(false);
    window.location.href = j.url;
  };

  return (
    <form onSubmit={(e) => (e.preventDefault(), buy())} className="rounded-3xl bg-white p-6 shadow-sm space-y-5">
      <div className="flex gap-2">
        {REGIONS.map((x) => (
          <button type="button" key={x.id} onClick={() => setRegion(x.id)} className={`rounded-full px-3 py-1.5 text-sm font-bold border-2 ${region === x.id ? "border-coral bg-coral text-white" : "border-ink/10"}`}>{x.flag} {x.label}</button>
        ))}
      </div>
      <div>
        <div className="text-xs font-bold uppercase tracking-wider text-ink/50 mb-2">Amount</div>
        <div className="grid grid-cols-2 gap-2">
          {options.map((o) => (
            <button type="button" key={o.amount} onClick={() => (setAmount(o.amount), setCustom(""))} className={`rounded-2xl border-2 px-4 py-3 text-left ${!custom && amount === o.amount ? "border-coral" : "border-ink/10"}`}>
              <span className="font-extrabold text-xl block">{r.symbol}{o.amount}</span>
              <span className="text-xs text-ink/50">Covers {o.covers}</span>
            </button>
          ))}
        </div>
        <input value={custom} onChange={(e) => setCustom(e.target.value.replace(/[^\d]/g, ""))} inputMode="numeric" placeholder={`Or another amount (${r.symbol}${GIFT_MIN}–${r.symbol}${GIFT_MAX})`} className={`${field} mt-2`} />
      </div>
      <div className="grid sm:grid-cols-2 gap-2">
        <input value={recipientName} onChange={(e) => setRecipientName(e.target.value)} maxLength={60} placeholder="Who's it for? (name)" className={field} />
        <input value={fromName} onChange={(e) => setFromName(e.target.value)} maxLength={60} placeholder="From (your name)" className={field} />
      </div>
      <textarea value={message} onChange={(e) => setMessage(e.target.value)} maxLength={300} rows={3} placeholder="Your message, e.g. For all our adventures. Happy Christmas! x" className={`${field} resize-none`} />
      <input value={buyerEmail} onChange={(e) => setBuyerEmail(e.target.value)} type="email" required placeholder="Your email (we send the gift card here)" className={field} />
      <label className="flex items-start gap-2 text-sm">
        <input type="checkbox" checked={toThem} onChange={(e) => setToThem(e.target.checked)} className="mt-1 accent-coral" />
        <span>Also email it straight to them</span>
      </label>
      {toThem && (
        <div className="grid sm:grid-cols-2 gap-2">
          <input value={recipientEmail} onChange={(e) => setRecipientEmail(e.target.value)} type="email" required placeholder="Their email" className={field} />
          <label className="text-sm">
            <input value={sendOn} onChange={(e) => setSendOn(e.target.value)} type="date" min={today} className={field} />
            <span className="text-xs text-ink/50">Leave empty to send now. Dated cards arrive at 8am (UK).</span>
          </label>
        </div>
      )}
      {err && <div className="text-sm font-bold text-coral-dark">{err}</div>}
      <button type="submit" disabled={busy || value < GIFT_MIN} className="w-full rounded-full bg-coral py-4 text-lg font-extrabold text-white shadow-lg shadow-coral/30 disabled:opacity-50">
        {busy ? "One moment…" : `Buy ${r.symbol}${value || 0} gift card`}
      </button>
      <p className="text-xs text-center text-ink/40">Secure payment by Stripe · Valid for 2 years · Delivered by email</p>
    </form>
  );
}
