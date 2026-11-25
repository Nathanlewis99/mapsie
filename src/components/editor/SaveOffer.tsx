"use client";
import { useState } from "react";
import { rememberOffer, SAVE_OFFER, saveOfferOn, type MyOffer } from "@/lib/offers";
import { track } from "@/lib/track";

/**
 * "Save your map": shown once, after someone has shown intent in the designer. Emails them a link to
 * their design and (while the trial runs) a personal code for 15% off that lasts an hour. Easy to close.
 */
export default function SaveOffer({ save, onClose, onSaved }: { save: () => Promise<string>; onClose: () => void; onSaved: (o: MyOffer | null) => void }) {
  const [email, setEmail] = useState("");
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");
  const deal = saveOfferOn();
  const close = () => (track("save_offer_closed"), onClose());

  const send = async () => {
    setBusy(true);
    setErr("");
    try {
      const designId = await save();
      const r = await fetch("/api/offer/save", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ designId, email, remind: true }) });
      const j = await r.json().catch(() => ({}));
      if (!r.ok) return setErr(j.error ?? "Couldn't save it. Please try again.");
      track("save_offer_saved", { offer: !!j.offer });
      if (j.offer) rememberOffer(j.offer);
      onSaved(j.offer ?? null);
    } catch {
      setErr("Couldn't save it. Please try again.");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="fixed inset-x-0 bottom-0 z-50 sm:inset-auto sm:bottom-6 sm:left-6 sm:max-w-sm">
      <form
        onSubmit={(e) => (e.preventDefault(), send())}
        className="relative rounded-t-3xl sm:rounded-3xl bg-white p-5 pb-6 shadow-2xl border border-ink/10 space-y-3"
      >
        <button type="button" onClick={close} aria-label="Close" className="absolute right-3 top-3 grid h-9 w-9 place-items-center rounded-full text-xl text-ink/50 hover:bg-sand">×</button>
        <div className="pr-8">
          <div className="font-display text-xl font-extrabold">💾 Save your map</div>
          <p className="text-sm text-ink/60 mt-1">
            We&apos;ll email you a link so you can come back to it on any device.
            {deal && <> Order in the next <b className="text-coral-dark">{SAVE_OFFER.minutes} minutes</b> and get <b className="text-coral-dark">{SAVE_OFFER.pct}% off</b>.</>}
          </p>
        </div>
        <div className="flex gap-2">
          <input
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="you@example.com"
            className="min-w-0 flex-1 rounded-2xl border-2 border-ink/10 px-3 py-2.5 font-semibold outline-none focus:border-coral"
          />
          <button type="submit" disabled={busy} className="rounded-full bg-coral px-4 font-extrabold text-white disabled:opacity-50 whitespace-nowrap">{busy ? "Saving…" : deal ? `Save + ${SAVE_OFFER.pct}% off` : "Save it"}</button>
        </div>
        {err && <div className="text-sm font-bold text-coral-dark">{err}</div>}
        <p className="text-[11px] text-ink/40">One email with your link{deal ? " and code" : ""}, and one reminder tomorrow. See our <a href="/legal/privacy" className="underline">privacy policy</a>.</p>
      </form>
    </div>
  );
}
