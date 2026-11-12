"use client";
import { useState } from "react";

export default function TwoFactorForm({ next }: { next: string }) {
  const [code, setCode] = useState("");
  const [err, setErr] = useState("");
  const [busy, setBusy] = useState(false);
  return (
    <form
      className="space-y-3"
      onSubmit={async (e) => {
        e.preventDefault();
        setBusy(true);
        setErr("");
        const r = await fetch("/api/admin/2fa", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ code, next }) });
        const j = await r.json();
        if (r.ok) {
          window.location.href = j.next;
        } else {
          setErr(j.error ?? "Something went wrong");
          setBusy(false);
        }
      }}
    >
      <label htmlFor="totp" className="sr-only">6-digit code</label>
      <input
        id="totp"
        value={code}
        onChange={(e) => setCode(e.target.value.replace(/[^\d]/g, "").slice(0, 6))}
        inputMode="numeric"
        autoComplete="one-time-code"
        autoFocus
        placeholder="123456"
        className="w-full rounded-2xl border-2 border-ink/10 px-4 py-3 text-center text-2xl font-extrabold tracking-[0.4em] outline-none focus:border-coral"
      />
      {err && <p className="text-sm font-bold text-coral-dark">{err}</p>}
      <button disabled={busy || code.length !== 6} className="w-full rounded-full bg-coral py-3 font-extrabold text-white disabled:opacity-40">
        {busy ? "Checking…" : "Continue"}
      </button>
    </form>
  );
}
