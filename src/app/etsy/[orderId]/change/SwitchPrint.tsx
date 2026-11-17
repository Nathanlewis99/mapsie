"use client";
import { useState } from "react";
import PrintOptionsPicker from "@/components/PrintOptionsPicker";
import { etsyFinishFor, etsyPrice } from "@/lib/etsyOptions";
import type { PrintOptions } from "@/lib/products";
import type { FrameId, MountId, PaperId } from "@/lib/types";

type Current = { format: "print" | "digital"; productId: string; frame: string; paper: PaperId; mount: MountId };
type Result = { code: string; size: string; finish: string; label: string; price: number; paid: number; currency: string; listingUrl: string };

const fmt = (amount: number, currency = "gbp") =>
  new Intl.NumberFormat("en-GB", { style: "currency", currency: currency.toUpperCase(), maximumFractionDigits: amount % 1 ? 2 : 0 }).format(amount);

export default function SwitchPrint({ orderId, k, designId, current, paid, currency, pending }: {
  orderId: string; k: string; designId?: string; current: Current; paid: number; currency: string; pending: { code: string; label: string } | null;
}) {
  const [opts, setOpts] = useState<Required<PrintOptions>>({ ...current, frame: current.frame as FrameId, glaze: "perspex" });
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");
  const [done, setDone] = useState<Result | null>(null);
  const [copied, setCopied] = useState(false);

  const framed = opts.format !== "digital" && opts.frame !== "none";
  const want = { ...opts, paper: framed ? ("ema" as PaperId) : opts.paper, mount: framed ? opts.mount : ("none" as MountId) };
  const finish = etsyFinishFor(want);
  const same = want.format === current.format && want.productId === current.productId && (want.format === "digital" || (want.frame === current.frame && want.paper === current.paper && want.mount === current.mount));
  const price = finish ? etsyPrice(want.productId, finish) : 0;

  const go = async () => {
    setBusy(true);
    setErr("");
    const r = await fetch(`/api/etsy/orders/${orderId}/swap`, { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ k, designId, to: want }) });
    const j = await r.json();
    setBusy(false);
    if (!r.ok) return setErr(j.error ?? "Something went wrong");
    setDone(j);
  };

  if (done) {
    return (
      <div className="rounded-3xl bg-white p-6 shadow-sm space-y-5">
        <div className="font-extrabold text-lg">Nearly there: three quick steps</div>
        <ol className="space-y-4 text-sm">
          <li>
            <b>1. Copy your switch code</b>
            <div className="mt-2 flex items-center gap-2">
              <code className="rounded-xl bg-sand px-4 py-2 text-lg font-extrabold tracking-wider">{done.code}</code>
              <button onClick={() => { navigator.clipboard?.writeText(done.code); setCopied(true); }} className="rounded-full border-2 border-ink/10 px-3 py-1.5 font-bold">{copied ? "Copied ✓" : "Copy"}</button>
            </div>
          </li>
          <li>
            <b>2. Buy the new print on Etsy</b>
            <div className="text-ink/70 mt-1">Choose <b>Size: {done.size}</b> and <b>Finish: {done.finish}</b> ({fmt(done.price)}), and paste the code into the personalisation box.</div>
            <a href={done.listingUrl} target="_blank" rel="noreferrer" className="mt-2 inline-block rounded-full bg-coral px-5 py-2.5 font-extrabold text-white">Open the Etsy listing ↗</a>
          </li>
          <li>
            <b>3. We refund your first order in full</b>
            <div className="text-ink/70 mt-1">
              As soon as the new order reaches us, your map moves across to it and we refund the {fmt(done.paid, done.currency)} you paid for your first order on Etsy, usually within 2 working days.
              We&apos;ll email you a link to carry on designing.
            </div>
          </li>
        </ol>
        <p className="text-xs text-ink/50">Changed your mind? Just don&apos;t buy the new print: your original order stays exactly as it is.</p>
      </div>
    );
  }

  return (
    <div className="space-y-5">
      {pending && (
        <div className="rounded-2xl bg-sea/10 px-4 py-3 text-sm">
          You started switching to <b>{pending.label}</b> (code <b>{pending.code}</b>). If you&apos;ve bought it on Etsy, it&apos;ll appear here shortly. You can also pick something else below.
        </div>
      )}
      <div className="rounded-3xl bg-cream border border-ink/5 p-4">
        <PrintOptionsPicker value={opts} onChange={(patch) => setOpts((o) => ({ ...o, ...patch }))} region="GB" />
      </div>
      <div className="rounded-3xl bg-white p-5 shadow-sm space-y-3 text-sm">
        {same ? (
          <p className="text-ink/60">That&apos;s what you already have. Pick a different size, frame or paper above.</p>
        ) : !finish ? (
          <p className="text-coral-dark font-bold">That combination isn&apos;t sold on Etsy. Please pick another.</p>
        ) : (
          <>
            <div className="flex justify-between font-bold"><span>New print on Etsy</span><span>{fmt(price)}</span></div>
            <div className="flex justify-between font-bold text-sea"><span>Refund of your first order</span><span>−{fmt(paid, currency)}</span></div>
            {currency.toLowerCase() === "gbp" && (
              <div className="flex justify-between font-extrabold border-t border-ink/10 pt-2"><span>{price >= paid ? "Overall, you pay" : "Overall, you get back"}</span><span>{fmt(Math.abs(price - paid), currency)}</span></div>
            )}
            <p className="text-xs text-ink/50">
              Etsy only lets payments go through Etsy, so a switch works like this: you buy the new print on Etsy, and we refund your first order in full. Your design carries over.
            </p>
          </>
        )}
        {err && <div className="text-coral-dark font-bold">{err}</div>}
        <button onClick={go} disabled={busy || same || !finish} className="w-full rounded-full bg-coral py-3 font-extrabold text-white disabled:opacity-40">
          {busy ? "One moment…" : "Switch to this print"}
        </button>
      </div>
    </div>
  );
}
