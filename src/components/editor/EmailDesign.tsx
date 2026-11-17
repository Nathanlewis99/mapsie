"use client";
import { useState } from "react";

/**
 * "Email me my design": saves a snapshot and emails the link. The reminder is opt-in
 * (unticked by default): one email a day later if they haven't ordered.
 */
export default function EmailDesign({ save, onClose, onSent }: { save: () => Promise<string>; onClose: () => void; onSent: () => void }) {
  const [email, setEmail] = useState("");
  const [remind, setRemind] = useState(false);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");

  const send = async () => {
    setBusy(true);
    setErr("");
    try {
      const designId = await save();
      const r = await fetch("/api/designs/email", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ designId, email, remind }) });
      const j = await r.json().catch(() => ({}));
      if (!r.ok) return setErr(j.error ?? "Couldn't send it. Please try again.");
      onSent();
    } catch {
      setErr("Couldn't send it. Please try again.");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 grid place-items-center bg-ink/40 px-4" onClick={onClose}>
      <form
        onClick={(e) => e.stopPropagation()}
        onSubmit={(e) => (e.preventDefault(), send())}
        className="w-full max-w-sm rounded-3xl bg-white p-6 shadow-2xl space-y-4"
      >
        <div>
          <div className="font-display text-2xl font-extrabold">Email me my map</div>
          <p className="text-sm text-ink/60 mt-1">Get a link to this design, to finish on any device or show someone first.</p>
        </div>
        <input
          type="email"
          required
          autoFocus
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="you@example.com"
          className="w-full rounded-2xl border-2 border-ink/10 px-4 py-3 font-semibold outline-none focus:border-coral"
        />
        <label className="flex items-start gap-2 text-sm text-ink/70">
          <input type="checkbox" checked={remind} onChange={(e) => setRemind(e.target.checked)} className="mt-1 accent-coral" />
          <span>Remind me tomorrow if I haven&apos;t ordered (one email, with a little thank-you discount).</span>
        </label>
        {err && <div className="text-sm font-bold text-coral-dark">{err}</div>}
        <div className="flex gap-2">
          <button type="submit" disabled={busy} className="flex-1 rounded-full bg-coral py-3 font-extrabold text-white disabled:opacity-50">{busy ? "Sending…" : "Send it"}</button>
          <button type="button" onClick={onClose} className="rounded-full border-2 border-ink/10 px-4 font-bold">Cancel</button>
        </div>
        <p className="text-[11px] text-ink/40">We&apos;ll only use your email for this. See our <a href="/legal/privacy" className="underline">privacy policy</a>.</p>
      </form>
    </div>
  );
}
