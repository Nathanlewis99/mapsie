"use client";
import { use, useEffect, useState } from "react";
import Link from "next/link";
import Logo from "@/components/Logo";
import { COMPANY } from "@/lib/company";

interface Status {
  status: string;
  renderFile?: string;
  renderInfo?: { width: number; height: number; dpi: number; mapDpi?: number };
  printProviderOrderId?: string;
  total: number;
  holdUntil?: string;
  canCancel?: boolean;
  refunded?: boolean;
}

const STEPS = [
  { key: "paid", label: "Payment received" },
  { key: "rendering", label: "Preparing your high-resolution print file" },
  { key: "ready", label: "Final check: you can still cancel" },
  { key: "submitted", label: "Sent to our print studio" },
];
const RANK: Record<string, number> = { pending_payment: 0, paid: 1, rendering: 2, ready: 3, submitted: 4 };
const time = (iso: string) => new Date(iso).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
const FINAL = ["submitted", "failed", "cancelled"];

export default function OrderPage({ params }: { params: Promise<{ orderId: string }> }) {
  const { orderId } = use(params);
  const [o, setO] = useState<Status | null>(null);
  const [confirming, setConfirming] = useState(false);
  const [cancelErr, setCancelErr] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    let t: ReturnType<typeof setTimeout>;
    const poll = async () => {
      let delay = 3000;
      const r = await fetch(`/api/orders/${orderId}`);
      if (r.ok) {
        const j: Status = await r.json();
        setO(j);
        if (FINAL.includes(j.status)) return;
        // Quick while the print file is being made, relaxed during the hold.
        if (j.status === "ready") delay = 20_000;
      }
      t = setTimeout(poll, delay);
    };
    poll();
    return () => clearTimeout(t);
  }, [orderId]);

  const cancel = async () => {
    setBusy(true);
    setCancelErr("");
    const r = await fetch(`/api/orders/${orderId}/cancel`, { method: "POST" });
    const j = await r.json();
    if (r.ok) setO((x) => (x ? { ...x, status: "cancelled", refunded: j.refunded, canCancel: false } : x));
    else setCancelErr(j.error ?? "Couldn't cancel. Please email us.");
    setBusy(false);
    setConfirming(false);
  };

  if (o?.status === "cancelled") {
    return (
      <main className="max-w-xl mx-auto px-6 py-14 space-y-6">
        <Link href="/" className="font-display text-2xl font-extrabold"><Logo /></Link>
        <h1 className="font-display text-4xl font-extrabold">Order cancelled</h1>
        <p className="text-ink/70">
          Order <b>{orderId}</b> won&apos;t be printed.{" "}
          {o.refunded ? "We've refunded you in full. It usually reaches your account within 5–10 working days." : "You haven't been charged for it."}
        </p>
        <Link href="/create" className="inline-block rounded-full bg-coral px-6 py-3 font-extrabold text-white">Back to your design</Link>
      </main>
    );
  }

  return (
    <main className="max-w-xl mx-auto px-6 py-14 space-y-8">
      <Link href="/" className="font-display text-2xl font-extrabold"><Logo /></Link>
      <div>
        <h1 className="font-display text-4xl font-extrabold">Thank you! 🎉</h1>
        <p className="text-ink/60 mt-2">Order <b>{orderId}</b>. We&apos;ll email you when it ships.</p>
      </div>

      {o?.status === "failed" ? (
        <div className="rounded-2xl bg-coral/10 p-4 font-bold text-coral-dark">
          Something went wrong preparing your print. We&apos;ve been notified and will sort it out. Questions? {COMPANY.supportEmail}
        </div>
      ) : (
        <ol className="space-y-3">
          {STEPS.map((s, i) => {
            const rank = o ? RANK[o.status] ?? 0 : 0;
            const done = rank > i + 1 || (s.key === "submitted" && o?.status === "submitted");
            const active = !done && rank === i + 1;
            const label = s.key === "ready" && o?.holdUntil ? `Final check: goes to print at ${time(o.holdUntil)}` : s.label;
            return (
              <li key={s.key} className="flex items-center gap-3 rounded-2xl bg-white px-4 py-3 shadow-sm font-bold">
                <span className={`grid place-items-center w-7 h-7 rounded-full text-sm shrink-0 ${done ? "bg-sea text-white" : active ? "bg-coral/20 animate-pulse" : "bg-ink/10"}`}>
                  {done ? "✓" : i + 1}
                </span>
                {label}
              </li>
            );
          })}
        </ol>
      )}

      {o?.canCancel && o.holdUntil && (
        <div className="rounded-2xl border-2 border-ink/10 p-4 space-y-3">
          <p className="text-sm text-ink/70">
            Spotted a mistake? You can cancel for a full refund until <b>{time(o.holdUntil)}</b>, when your print goes to our studio.
          </p>
          {confirming ? (
            <div className="flex flex-wrap gap-2">
              <button onClick={cancel} disabled={busy} className="rounded-full bg-coral-dark px-5 py-2.5 font-extrabold text-white disabled:opacity-50">
                {busy ? "Cancelling…" : "Yes, cancel and refund"}
              </button>
              <button onClick={() => setConfirming(false)} className="rounded-full border-2 border-ink/15 px-5 py-2.5 font-bold">Keep my order</button>
            </div>
          ) : (
            <button onClick={() => setConfirming(true)} className="rounded-full border-2 border-ink/15 px-5 py-2.5 font-bold hover:border-ink/40">Cancel order</button>
          )}
          {cancelErr && <p className="text-sm font-bold text-coral-dark">{cancelErr}</p>}
        </div>
      )}

      {o?.renderFile && (
        <div className="space-y-2">
          <div className="text-xs font-bold uppercase tracking-wider text-ink/50">Your print</div>
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src={`/api/renders/${o.renderFile}`} alt="Your map print" className="w-full max-w-sm rounded-xl shadow-lg" />
          {o.renderInfo && (
            <p className="text-xs text-ink/50">
              {o.renderInfo.width} × {o.renderInfo.height} px · {o.renderInfo.dpi} dpi
              {o.printProviderOrderId && <> · print ref {o.printProviderOrderId}</>}
            </p>
          )}
        </div>
      )}
      <p className="text-xs text-ink/40">Map data © OpenStreetMap contributors.</p>
    </main>
  );
}
