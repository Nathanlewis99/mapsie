"use client";
import { useEffect, useState } from "react";
import Logo from "@/components/Logo";
import Link from "next/link";
import dynamic from "next/dynamic";
import type { Design } from "@/lib/types";
import { describeOptions, getRegion, guessRegion, itemPrice, money, priceLines, REGIONS, SHIPPING, type PrintOptions, type RegionId, type ShippingId } from "@/lib/products";
import PrintOptionsPicker from "@/components/PrintOptionsPicker";

const FramedPoster = dynamic(() => import("@/components/FramedPoster"), { ssr: false });
const WallPreview = dynamic(() => import("@/components/WallPreview"), { ssr: false });

function storedRegion(): RegionId {
  try {
    return JSON.parse(localStorage.getItem("mapsie-design") ?? "{}").state?.region ?? guessRegion();
  } catch {
    return guessRegion();
  }
}

export default function Checkout({ design: saved }: { design: Design }) {
  // Size, frame and paper can still be changed here; the preview follows.
  const [opts, setOpts] = useState<Required<PrintOptions>>({ productId: saved.productId, frame: saved.frame, paper: saved.paper, mount: saved.mount, glaze: saved.glaze });
  const design = { ...saved, ...opts };
  const [showOptions, setShowOptions] = useState(false);
  const [region, setRegion] = useState<RegionId>("GB");
  const [shipping, setShipping] = useState<ShippingId>("standard");
  const [view, setView] = useState<"print" | "wall">("wall");
  const [email, setEmail] = useState("");
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");
  useEffect(() => setRegion(storedRegion()), []);
  // Signed-in customers: fill in their email.
  useEffect(() => {
    fetch("/api/auth/me").then((r) => r.json()).then((j) => j.user?.email && setEmail((e) => e || j.user.email)).catch(() => {});
  }, []);

  const ship = SHIPPING.find((s) => s.id === shipping)!;
  const item = itemPrice(design, region);
  const lines = priceLines(design, region);
  const total = item + ship.price[region];

  const pay = async () => {
    setBusy(true);
    setErr("");
    const r = await fetch("/api/checkout", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ designId: saved.id, email, shipping, region, options: opts }) });
    const j = await r.json();
    if (!r.ok) return setErr(j.error ?? "Something went wrong"), setBusy(false);
    window.location.href = j.url;
  };

  return (
    <div className="min-h-dvh">
      <header className="max-w-6xl mx-auto px-6 py-4 flex justify-between items-center">
        <Link href="/" className="font-display text-2xl font-extrabold"><Logo /></Link>
        <Link href="/create" className="text-sm font-bold text-ink/60 hover:text-ink">← Back to editing</Link>
      </header>
      <main className="max-w-6xl mx-auto px-6 pb-16 grid lg:grid-cols-[1.3fr_1fr] gap-10 items-start">
        <div className="space-y-3">
          <div className="flex gap-1 rounded-full bg-sand/70 p-1 w-fit">
            {(["wall", "print"] as const).map((v) => (
              <button key={v} onClick={() => setView(v)} className={`rounded-full px-4 py-1.5 text-sm font-extrabold ${view === v ? "bg-white shadow-sm" : "text-ink/50"}`}>
                {v === "wall" ? "🛋️ On the wall" : "🖼️ Close up"}
              </button>
            ))}
          </div>
          {view === "wall" ? (
            <WallPreview key={`${opts.productId}-${opts.frame}-${opts.mount}`} design={design} />
          ) : (
            <div className="grid place-items-center rounded-3xl bg-sand/70 p-8">
              <FramedPoster key={`${opts.productId}-${opts.frame}-${opts.mount}`} design={design} width={Math.min(420, design.view.refWidth)} />
            </div>
          )}
        </div>
        <div className="space-y-6">
          <div>
            <h1 className="font-display text-4xl font-extrabold">Nearly yours!</h1>
            <p className="text-ink/60 mt-2">{design.frame !== "none" ? "Framed and ready to hang." : "Printed on thick art paper and shipped in a sturdy tube."}</p>
          </div>
          <div className="rounded-3xl bg-white p-5 shadow-sm space-y-1">
            <div className="font-bold truncate">{design.title}</div>
            <div className="text-sm text-ink/50">{describeOptions(design)} · {design.stops.length} stops</div>
            <div className="pt-2 space-y-1">
              {lines.map((l) => (
                <div key={l.label} className="flex justify-between text-sm font-bold"><span>{l.label}</span><span>{money(region, l.amount)}</span></div>
              ))}
            </div>
            <button onClick={() => setShowOptions((v) => !v)} className="pt-2 text-sm font-extrabold text-coral-dark">
              {showOptions ? "Done ✓" : design.frame === "none" ? "🖼️ Add a frame, or change size or paper" : "Change size, frame or mount"}
            </button>
          </div>
          {showOptions && (
            <div className="rounded-3xl bg-cream border border-ink/5 p-4">
              <PrintOptionsPicker value={opts} onChange={(patch) => setOpts((o) => ({ ...o, ...patch }))} region={region} />
            </div>
          )}
          <div className="space-y-2">
            <div className="text-xs font-bold uppercase tracking-wider text-ink/50">Deliver to</div>
            <div className="flex flex-wrap gap-2">
              {REGIONS.map((r) => (
                <button key={r.id} onClick={() => setRegion(r.id)} className={`rounded-full px-3 py-1.5 text-sm font-bold border-2 ${region === r.id ? "border-coral bg-coral text-white" : "border-ink/10 bg-white"}`}>
                  {r.flag} {r.label}
                </button>
              ))}
            </div>
          </div>
          <div className="space-y-2">
            <div className="text-xs font-bold uppercase tracking-wider text-ink/50">Delivery</div>
            {SHIPPING.map((s) => (
              <button key={s.id} onClick={() => setShipping(s.id)} className={`w-full flex justify-between items-center rounded-2xl border-2 bg-white px-4 py-3 ${shipping === s.id ? "border-coral" : "border-ink/10"}`}>
                <span className="text-left"><span className="font-bold block">{s.label}</span><span className="text-sm text-ink/50">{s.detail}</span></span>
                <span className="font-extrabold">{s.price[region] ? money(region, s.price[region]) : "Free"}</span>
              </button>
            ))}
          </div>
          <div>
            <div className="text-xs font-bold uppercase tracking-wider text-ink/50 mb-2">Email for updates</div>
            <input value={email} onChange={(e) => setEmail(e.target.value)} type="email" placeholder="you@example.com" className="w-full rounded-2xl border-2 border-ink/10 bg-white px-4 py-3 font-semibold outline-none focus:border-coral" />
          </div>
          {err && <div className="text-coral-dark font-bold">{err}</div>}
          <button onClick={pay} disabled={busy} className="w-full rounded-full bg-coral py-4 text-lg font-extrabold text-white shadow-lg shadow-coral/30 hover:bg-coral-dark disabled:opacity-50">
            {busy ? "One moment…" : `Pay ${money(region, total)}`}
          </button>
          <p className="text-xs text-center text-ink/40">Secure payment by Stripe · Printed locally in {getRegion(region).label} · Made to order</p>
        </div>
      </main>
    </div>
  );
}
