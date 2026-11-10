"use client";
import { useState } from "react";
import Link from "next/link";
import dynamic from "next/dynamic";
import type { Design } from "@/lib/types";
import { getProduct, SHIPPING, type ShippingId } from "@/lib/products";

const Poster = dynamic(() => import("@/components/Poster"), { ssr: false });

export default function Checkout({ design }: { design: Design }) {
  const product = getProduct(design.productId);
  const [shipping, setShipping] = useState<ShippingId>("standard");
  const [email, setEmail] = useState("");
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");
  const ship = SHIPPING.find((s) => s.id === shipping)!;

  const pay = async () => {
    setBusy(true);
    setErr("");
    const r = await fetch("/api/checkout", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ designId: design.id, email, shipping }) });
    const j = await r.json();
    if (!r.ok) return setErr(j.error ?? "Something went wrong"), setBusy(false);
    window.location.href = j.url;
  };

  return (
    <div className="min-h-dvh">
      <header className="px-6 py-4 flex justify-between items-center">
        <Link href="/" className="font-display text-2xl font-extrabold">Mapsie<span className="text-coral">.</span></Link>
        <Link href="/create" className="text-sm font-bold text-ink/60 hover:text-ink">← Back to editing</Link>
      </header>
      <main className="max-w-5xl mx-auto px-6 pb-16 grid md:grid-cols-2 gap-10 items-start">
        <div className="grid place-items-center rounded-3xl bg-sand/70 p-8">
          <div className="shadow-[0_30px_60px_-15px_rgba(31,36,48,0.35)]">
            <Poster design={design} width={Math.min(380, design.view.refWidth)} />
          </div>
        </div>
        <div className="space-y-6">
          <div>
            <h1 className="font-display text-4xl font-extrabold">Nearly yours!</h1>
            <p className="text-ink/60 mt-2">Printed on thick museum-quality matte paper and shipped flat-packed in a sturdy tube.</p>
          </div>
          <div className="rounded-3xl bg-white p-5 shadow-sm space-y-1">
            <div className="flex justify-between font-bold"><span>{design.title}</span><span>£{product.priceGbp.toFixed(2)}</span></div>
            <div className="text-sm text-ink/50">{product.label} · {design.orientation} · {design.stops.length} stops</div>
          </div>
          <div className="space-y-2">
            <div className="text-xs font-bold uppercase tracking-wider text-ink/50">Delivery</div>
            {SHIPPING.map((s) => (
              <button key={s.id} onClick={() => setShipping(s.id)} className={`w-full flex justify-between items-center rounded-2xl border-2 bg-white px-4 py-3 ${shipping === s.id ? "border-coral" : "border-ink/10"}`}>
                <span className="text-left"><span className="font-bold block">{s.label}</span><span className="text-sm text-ink/50">{s.detail}</span></span>
                <span className="font-extrabold">{s.priceGbp ? `£${s.priceGbp.toFixed(2)}` : "Free"}</span>
              </button>
            ))}
          </div>
          <div>
            <div className="text-xs font-bold uppercase tracking-wider text-ink/50 mb-2">Email for updates</div>
            <input value={email} onChange={(e) => setEmail(e.target.value)} type="email" placeholder="you@example.com" className="w-full rounded-2xl border-2 border-ink/10 bg-white px-4 py-3 font-semibold outline-none focus:border-coral" />
          </div>
          {err && <div className="text-coral-dark font-bold">{err}</div>}
          <button onClick={pay} disabled={busy} className="w-full rounded-full bg-coral py-4 text-lg font-extrabold text-white shadow-lg shadow-coral/30 hover:bg-coral-dark disabled:opacity-50">
            {busy ? "One moment…" : `Pay £${(product.priceGbp + ship.priceGbp).toFixed(2)}`}
          </button>
          <p className="text-xs text-center text-ink/40">Secure payment by Stripe. UK delivery only for now.</p>
        </div>
      </main>
    </div>
  );
}
