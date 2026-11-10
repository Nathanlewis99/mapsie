"use client";
import { use, useEffect, useState } from "react";
import Link from "next/link";

interface Status {
  status: string;
  renderFile?: string;
  renderInfo?: { width: number; height: number; dpi: number };
  printProviderOrderId?: string;
  totalGbp: number;
}

const STEPS = [
  { key: "paid", label: "Payment received" },
  { key: "rendering", label: "Creating your high-resolution print file" },
  { key: "submitted", label: "Sent to our print studio" },
];
const rank = (s: string) => ({ pending_payment: 0, paid: 1, rendering: 2, submitted: 3 } as Record<string, number>)[s] ?? 0;

export default function OrderPage({ params }: { params: Promise<{ orderId: string }> }) {
  const { orderId } = use(params);
  const [o, setO] = useState<Status | null>(null);
  useEffect(() => {
    let t: ReturnType<typeof setTimeout>;
    const poll = async () => {
      const r = await fetch(`/api/orders/${orderId}`);
      if (r.ok) {
        const j: Status = await r.json();
        setO(j);
        if (j.status === "submitted" || j.status === "failed") return;
      }
      t = setTimeout(poll, 2000);
    };
    poll();
    return () => clearTimeout(t);
  }, [orderId]);

  return (
    <main className="max-w-xl mx-auto px-6 py-14 space-y-8">
      <Link href="/" className="font-display text-2xl font-extrabold">Mapsie<span className="text-coral">.</span></Link>
      <div>
        <h1 className="font-display text-4xl font-extrabold">Thank you! 🎉</h1>
        <p className="text-ink/60 mt-2">Order <b>{orderId}</b>. We&apos;ll email you when it ships.</p>
      </div>
      {o?.status === "failed" ? (
        <div className="rounded-2xl bg-coral/10 p-4 font-bold text-coral-dark">Something went wrong preparing your print. We&apos;ve been notified and will sort it out.</div>
      ) : (
        <ol className="space-y-3">
          {STEPS.map((s, i) => {
            const done = o && rank(o.status) > i + (s.key === "submitted" ? 0 : 0) && (s.key !== "submitted" || o.status === "submitted");
            const active = o && !done && rank(o.status) === i + 1;
            return (
              <li key={s.key} className="flex items-center gap-3 rounded-2xl bg-white px-4 py-3 shadow-sm font-bold">
                <span className={`grid place-items-center w-7 h-7 rounded-full text-sm ${done ? "bg-sea text-white" : active ? "bg-coral/20 animate-pulse" : "bg-ink/10"}`}>{done ? "✓" : i + 1}</span>
                {s.label}
              </li>
            );
          })}
        </ol>
      )}
      {o?.renderFile && (
        <div className="space-y-2">
          <div className="text-xs font-bold uppercase tracking-wider text-ink/50">Your print file</div>
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src={`/api/renders/${o.renderFile}`} alt="Your map print" className="w-full rounded-xl shadow-lg" />
          {o.renderInfo && (
            <p className="text-xs text-ink/50">
              {o.renderInfo.width} × {o.renderInfo.height} px · {o.renderInfo.dpi} dpi
              {o.printProviderOrderId && <> · print ref {o.printProviderOrderId}</>}
            </p>
          )}
        </div>
      )}
    </main>
  );
}
