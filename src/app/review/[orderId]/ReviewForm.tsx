"use client";
import { useState } from "react";
import { COMPANY } from "@/lib/company";

/** Shrink a photo in the browser before upload (max 1200 px, JPEG). */
async function shrink(file: File): Promise<string> {
  const img = await createImageBitmap(file);
  const scale = Math.min(1, 1200 / Math.max(img.width, img.height));
  const c = document.createElement("canvas");
  c.width = Math.round(img.width * scale);
  c.height = Math.round(img.height * scale);
  c.getContext("2d")!.drawImage(img, 0, 0, c.width, c.height);
  return c.toDataURL("image/jpeg", 0.82);
}

export default function ReviewForm({ orderId, k, defaultName }: { orderId: string; k: string; defaultName: string }) {
  const [rating, setRating] = useState(0);
  const [hover, setHover] = useState(0);
  const [text, setText] = useState("");
  const [name, setName] = useState(defaultName);
  const [photo, setPhoto] = useState<string>("");
  const [publish, setPublish] = useState(true);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");
  const [done, setDone] = useState<number | null>(null);

  const send = async () => {
    if (!rating) return setErr("Please choose a star rating.");
    setBusy(true);
    setErr("");
    const r = await fetch("/api/reviews", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ orderId, k, rating, text, name, photo: photo || undefined, publish }) });
    const j = await r.json().catch(() => ({}));
    setBusy(false);
    if (!r.ok) return setErr(j.error ?? "Something went wrong. Please try again.");
    setDone(rating);
  };

  if (done !== null)
    return done >= 4 ? (
      <p className="text-center text-lg font-bold">Thank you so much! 💛 It means a lot to a small business like ours.</p>
    ) : (
      <div className="text-center space-y-2">
        <p className="text-lg font-bold">Thank you for telling us, and we&apos;re sorry it wasn&apos;t perfect.</p>
        <p className="text-ink/70">We&apos;ll email you shortly to put it right. You can also reach us at <a className="underline" href={`mailto:${COMPANY.supportEmail}`}>{COMPANY.supportEmail}</a> or on our <a className="underline" href="/support">help page</a>.</p>
      </div>
    );

  return (
    <form onSubmit={(e) => (e.preventDefault(), send())} className="space-y-4">
      <div className="flex justify-center gap-1" onMouseLeave={() => setHover(0)}>
        {[1, 2, 3, 4, 5].map((n) => (
          <button type="button" key={n} aria-label={`${n} star${n > 1 ? "s" : ""}`} onMouseEnter={() => setHover(n)} onClick={() => setRating(n)} className={`text-4xl transition ${(hover || rating) >= n ? "text-amber-400" : "text-ink/15"}`}>★</button>
        ))}
      </div>
      <textarea value={text} onChange={(e) => setText(e.target.value)} maxLength={1500} rows={4} placeholder="What did you think? Which trip is it, and where did it end up?" className="w-full rounded-2xl border-2 border-ink/10 px-4 py-3 outline-none focus:border-coral resize-none" />
      <label className="block">
        <span className="text-sm font-bold">A photo of it on your wall (optional)</span>
        <input type="file" accept="image/*" onChange={async (e) => { const f = e.target.files?.[0]; if (f) setPhoto(await shrink(f).catch(() => "")); }} className="mt-1 block w-full text-sm" />
      </label>
      {photo && <img src={photo} alt="Your photo" className="rounded-2xl max-h-56 mx-auto" />}
      <input value={name} onChange={(e) => setName(e.target.value)} maxLength={50} placeholder="Your name as you'd like it shown, e.g. Sarah, Bristol" className="w-full rounded-2xl border-2 border-ink/10 px-4 py-3 outline-none focus:border-coral" />
      <label className="flex items-start gap-2 text-sm text-ink/70">
        <input type="checkbox" checked={publish} onChange={(e) => setPublish(e.target.checked)} className="mt-1 accent-coral" />
        <span>Mapsie may show my review, first name and photo on its website and social media.</span>
      </label>
      {err && <div className="text-sm font-bold text-coral-dark">{err}</div>}
      <button disabled={busy} className="w-full rounded-full bg-coral py-3 font-extrabold text-white disabled:opacity-50">{busy ? "Sending…" : "Send my review"}</button>
    </form>
  );
}
