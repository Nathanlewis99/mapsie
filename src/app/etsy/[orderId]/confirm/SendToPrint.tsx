"use client";
import dynamic from "next/dynamic";
import { useState } from "react";
import type { Design } from "@/lib/types";

const FramedPoster = dynamic(() => import("@/components/FramedPoster"), { ssr: false });

export function Preview({ design }: { design: Design }) {
  return (
    <div className="grid place-items-center rounded-3xl bg-[radial-gradient(circle_at_30%_20%,#fff_0%,#f1e8da_70%)] p-8">
      <FramedPoster design={design} width={Math.min(460, design.view.refWidth)} />
    </div>
  );
}

export default function SendToPrint({ orderId, k, designId, email: known }: { orderId: string; k: string; designId: string; email: string }) {
  const [email, setEmail] = useState(known);
  const [checked, setChecked] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const send = async () => {
    setBusy(true);
    setError("");
    const r = await fetch(`/api/etsy/orders/${orderId}/submit`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ k, designId, email }),
    });
    const j = await r.json().catch(() => ({}));
    if (r.ok) {
      try {
        sessionStorage.removeItem("mapsie-etsy");
      } catch {}
      window.location.href = j.url;
      return;
    }
    setError(j.error ?? "Something went wrong. Please try again.");
    setBusy(false);
  };
  return (
    <div className="space-y-3">
      <label className="block text-sm">
        <span className="font-bold">Email for updates {known ? "" : "(optional)"}</span>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="you@example.com"
          className="mt-1 w-full rounded-2xl border-2 border-ink/10 bg-white px-4 py-2.5 outline-none focus:border-coral"
        />
      </label>
      <label className="flex items-start gap-2 text-sm">
        <input type="checkbox" checked={checked} onChange={(e) => setChecked(e.target.checked)} className="mt-1 accent-coral" />
        <span>I&apos;ve checked my map and I&apos;m happy for it to be printed like this.</span>
      </label>
      {error && <p role="alert" className="rounded-2xl bg-coral/10 px-4 py-3 text-sm font-bold text-coral-dark">{error}</p>}
      <button
        onClick={send}
        disabled={!checked || busy}
        className="w-full rounded-full bg-coral px-5 py-3 font-extrabold text-white shadow-lg shadow-coral/30 disabled:opacity-50"
      >
        {busy ? "Sending…" : "Send to print"}
      </button>
    </div>
  );
}
