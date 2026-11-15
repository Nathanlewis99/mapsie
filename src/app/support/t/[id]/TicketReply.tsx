"use client";
import { useState } from "react";
import { PhotoPicker } from "../../SupportForm";

export default function TicketReply({ id, k }: { id: string; k: string }) {
  const [text, setText] = useState("");
  const [photos, setPhotos] = useState<string[]>([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const send = async () => {
    setBusy(true);
    setError("");
    const r = await fetch(`/api/support/${id}/reply`, { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ k, text, photos }) }).catch(() => null);
    if (r?.ok) window.location.reload();
    else {
      setError((await r?.json().catch(() => null))?.error ?? "Couldn't send. Please try again.");
      setBusy(false);
    }
  };
  return (
    <div className="rounded-3xl bg-white p-5 shadow-sm space-y-3">
      <div className="font-bold">Add a message</div>
      <textarea value={text} onChange={(e) => setText(e.target.value)} rows={4} maxLength={5000} className="w-full rounded-2xl border-2 border-ink/10 px-4 py-3 outline-none focus:border-coral" />
      <PhotoPicker photos={photos} setPhotos={setPhotos} />
      {error && <p role="alert" className="text-sm font-bold text-coral-dark">{error}</p>}
      <button onClick={send} disabled={busy || (!text.trim() && !photos.length)} className="rounded-full bg-coral px-5 py-2.5 font-extrabold text-white disabled:opacity-50">
        {busy ? "Sending…" : "Send"}
      </button>
    </div>
  );
}
