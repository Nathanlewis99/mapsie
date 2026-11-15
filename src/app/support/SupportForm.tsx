"use client";
import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import { MAX_PHOTOS, PHOTO_MAX_PX, REASONS, reasonFor, type SupportReason } from "@/lib/support";

type Summary = {
  id: string; status: string; title: string | null; what: string | null; placed: string; delivery: string;
  shipments: { carrier?: string; trackingNumber?: string; trackingUrl?: string; dispatchDate?: string }[];
  holdUntil: string | null; etsy: boolean;
};

const input = "w-full rounded-2xl border-2 border-ink/10 bg-white px-4 py-3 outline-none focus:border-coral transition";
const day = (iso: string) => new Date(iso).toLocaleDateString("en-GB", { day: "numeric", month: "long" });
const STATUS: Record<string, string> = {
  awaiting_design: "waiting for your design",
  paid: "being prepared",
  rendering: "being prepared",
  ready: "in its final check before printing",
  submitted: "being printed",
  shipped: "dispatched",
  cancelled: "cancelled",
  failed: "delayed (we're on it)",
  pending_payment: "not paid",
};

/** Shrink a photo in the browser (phones take huge ones) and return it as a JPEG data URL. */
async function shrink(file: File): Promise<string> {
  const url = URL.createObjectURL(file);
  try {
    const img = await new Promise<HTMLImageElement>((res, rej) => {
      const i = new Image();
      i.onload = () => res(i);
      i.onerror = rej;
      i.src = url;
    });
    const k = Math.min(1, PHOTO_MAX_PX / Math.max(img.width, img.height));
    const c = document.createElement("canvas");
    c.width = Math.round(img.width * k);
    c.height = Math.round(img.height * k);
    c.getContext("2d")!.drawImage(img, 0, 0, c.width, c.height);
    return c.toDataURL("image/jpeg", 0.85);
  } finally {
    URL.revokeObjectURL(url);
  }
}

export function PhotoPicker({ photos, setPhotos }: { photos: string[]; setPhotos: (p: string[]) => void }) {
  const ref = useRef<HTMLInputElement>(null);
  const [busy, setBusy] = useState(false);
  return (
    <div className="space-y-2">
      <div className="flex flex-wrap gap-2">
        {photos.map((p, i) => (
          <div key={i} className="relative">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src={p} alt={`Photo ${i + 1}`} className="w-20 h-20 rounded-xl object-cover" />
            <button type="button" onClick={() => setPhotos(photos.filter((_, j) => j !== i))} className="absolute -top-2 -right-2 w-6 h-6 rounded-full bg-ink text-white text-xs font-bold" aria-label="Remove photo">✕</button>
          </div>
        ))}
        {photos.length < MAX_PHOTOS && (
          <button type="button" onClick={() => ref.current?.click()} className="w-20 h-20 rounded-xl border-2 border-dashed border-ink/20 text-ink/50 text-xs font-bold hover:border-coral hover:text-coral">
            {busy ? "Adding…" : "+ Photo"}
          </button>
        )}
      </div>
      <input
        ref={ref}
        type="file"
        accept="image/*"
        multiple
        className="hidden"
        onChange={async (e) => {
          const files = [...(e.target.files ?? [])].slice(0, MAX_PHOTOS - photos.length);
          e.target.value = "";
          setBusy(true);
          const added: string[] = [];
          for (const f of files) {
            try {
              added.push(await shrink(f));
            } catch {}
          }
          setPhotos([...photos, ...added]);
          setBusy(false);
        }}
      />
    </div>
  );
}

export default function SupportForm({ initialOrder, initialEmail }: { initialOrder: string; initialEmail: string }) {
  const [orderRef, setOrderRef] = useState(initialOrder);
  const [email, setEmail] = useState(initialEmail);
  const [name, setName] = useState("");
  const [reason, setReason] = useState<SupportReason | "">("");
  const [message, setMessage] = useState("");
  const [photos, setPhotos] = useState<string[]>([]);
  const [order, setOrder] = useState<Summary | null>(null);
  const [checking, setChecking] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [done, setDone] = useState<{ id: string; url: string } | null>(null);

  // Check the order number and email together, a moment after typing stops.
  useEffect(() => {
    setOrder(null);
    if (orderRef.trim().length < 6 || !/\S+@\S+\.\S+/.test(email)) return;
    const t = setTimeout(async () => {
      setChecking(true);
      const r = await fetch("/api/support/lookup", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ orderRef, email }) }).catch(() => null);
      const j = r ? await r.json().catch(() => null) : null;
      setOrder(j?.found ? j.order : null);
      setChecking(false);
    }, 600);
    return () => clearTimeout(t);
  }, [orderRef, email]);

  const r = reason ? reasonFor(reason) : null;
  const canChange = order?.holdUntil && new Date(order.holdUntil).getTime() > Date.now() && ["paid", "rendering", "ready"].includes(order.status);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    if (!reason) return setError("Please choose what you need help with.");
    if (r?.photos === "required" && !photos.length) return setError("Please add at least one photo, so we can see the problem and put it right quickly.");
    setBusy(true);
    const res = await fetch("/api/support", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ orderRef, email, name, reason, message, photos }),
    }).catch(() => null);
    const j = res ? await res.json().catch(() => ({})) : {};
    if (res?.ok) setDone(j);
    else setError(j.error ?? "Something went wrong. Please try again, or email us.");
    setBusy(false);
  };

  if (done)
    return (
      <div className="space-y-4">
        <h2 className="font-display text-2xl font-extrabold">Thanks, we&apos;ve got it 💌</h2>
        <p>Your reference is <b>{done.id}</b>. We&apos;ve emailed you a copy, and we&apos;ll reply within one working day.</p>
        <Link href={done.url} className="inline-block rounded-full bg-coral px-5 py-3 font-extrabold text-white">Go to your support page</Link>
        <p className="text-sm text-ink/60">You can add more details or photos there at any time.</p>
      </div>
    );

  return (
    <form onSubmit={submit} className="space-y-6">
      <div className="grid gap-3 sm:grid-cols-2">
        <label className="block">
          <span className="text-sm font-bold">Order number</span>
          <input value={orderRef} onChange={(e) => setOrderRef(e.target.value)} placeholder="ord_… or your Etsy order number" className={`${input} mt-1`} />
          <span className="text-xs text-ink/50">It&apos;s in your order email. Leave blank if it&apos;s not about an order.</span>
        </label>
        <label className="block">
          <span className="text-sm font-bold">Email you ordered with</span>
          <input type="email" required value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@example.com" autoComplete="email" className={`${input} mt-1`} />
        </label>
      </div>

      {checking && <p className="text-sm text-ink/50">Looking up your order…</p>}
      {order && (
        <div className="rounded-2xl bg-sea/10 px-4 py-3 text-sm space-y-1">
          <div className="font-extrabold">Found your order{order.title ? `: “${order.title}”` : ""}</div>
          {order.what && <div className="text-ink/70">{order.what}</div>}
          <div>
            Status: <b>{STATUS[order.status] ?? order.status}</b>
            {order.shipments[0]?.dispatchDate && <> on {day(order.shipments[0].dispatchDate)}</>}
          </div>
          {order.shipments.map((s, i) => (
            <div key={i}>
              {s.carrier} {s.trackingNumber}
              {s.trackingUrl && (
                <>
                  {" · "}
                  <a href={s.trackingUrl} target="_blank" rel="noreferrer" className="font-bold underline">Track it</a>
                </>
              )}
            </div>
          ))}
          <Link href={`/order/${order.id}`} className="font-bold underline">Open your order page</Link>
        </div>
      )}

      <fieldset>
        <legend className="text-sm font-bold mb-2">What do you need help with?</legend>
        <div className="grid gap-2 sm:grid-cols-2">
          {REASONS.map((x) => (
            <label key={x.id} className={`flex items-center gap-3 rounded-2xl border-2 px-4 py-3 cursor-pointer transition ${reason === x.id ? "border-coral bg-coral/5" : "border-ink/10 bg-white hover:border-ink/30"}`}>
              <input type="radio" name="reason" value={x.id} checked={reason === x.id} onChange={() => setReason(x.id)} className="accent-coral" />
              <span className="font-bold text-sm">{x.label}</span>
            </label>
          ))}
        </div>
      </fieldset>

      {r && (
        <div className="rounded-2xl bg-sand/70 px-4 py-3 text-sm space-y-2">
          <p>{r.hint}</p>
          {reason === "not_arrived" && order?.status === "shipped" && order.shipments[0]?.trackingUrl && (
            <p>
              Your parcel was dispatched{order.shipments[0].dispatchDate ? ` on ${day(order.shipments[0].dispatchDate)}` : ""}.{" "}
              <a href={order.shipments[0].trackingUrl} target="_blank" rel="noreferrer" className="font-bold underline">Check the tracking</a> first. If it&apos;s stuck or says delivered but you don&apos;t have it, tell us below.
            </p>
          )}
          {reason === "not_arrived" && order && order.status !== "shipped" && (
            <p>Your order hasn&apos;t been dispatched yet: it&apos;s {STATUS[order.status] ?? order.status}. We&apos;ll email you tracking as soon as it ships.</p>
          )}
          {(reason === "change" || reason === "address") && canChange && (
            <p>
              Good news: your order is still in its 1-hour window.{" "}
              <Link href={`/order/${order!.id}`} className="font-bold underline">{order!.etsy ? "Change your design" : "Cancel it"} on your order page</Link>.
            </p>
          )}
        </div>
      )}

      <label className="block">
        <span className="text-sm font-bold">Tell us what happened</span>
        <textarea value={message} onChange={(e) => setMessage(e.target.value)} required rows={5} maxLength={5000} className={`${input} mt-1`} placeholder="The more detail, the faster we can help." />
      </label>

      {r?.photos !== "none" && (
        <div>
          <div className="text-sm font-bold mb-2">Photos {r?.photos === "required" ? "(please add at least one)" : "(optional)"}</div>
          <PhotoPicker
            photos={photos}
            setPhotos={(p) => {
              setPhotos(p);
              setError("");
            }}
          />
        </div>
      )}

      <label className="block sm:w-1/2">
        <span className="text-sm font-bold">Your name (optional)</span>
        <input value={name} onChange={(e) => setName(e.target.value)} autoComplete="name" className={`${input} mt-1`} />
      </label>

      {error && <p role="alert" className="rounded-2xl bg-coral/10 px-4 py-3 text-sm font-bold text-coral-dark">{error}</p>}
      <button disabled={busy} className="rounded-full bg-coral px-6 py-3 font-extrabold text-white shadow-lg shadow-coral/30 disabled:opacity-60">
        {busy ? "Sending…" : "Send to Mapsie support"}
      </button>
    </form>
  );
}
