"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { createPortal } from "react-dom";

/** A bin icon that asks for confirmation in a dialog before deleting a saved map. */
export default function DeleteDesignButton({ id, title }: { id: string; title: string }) {
  const [open, setOpen] = useState(false);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");
  const router = useRouter();

  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && setOpen(false);
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open]);

  const remove = async () => {
    setBusy(true);
    setErr("");
    const r = await fetch(`/api/me/designs/${id}`, { method: "DELETE" }).catch(() => null);
    setBusy(false);
    if (!r?.ok) return setErr("Couldn't delete it. Please try again.");
    setOpen(false);
    router.refresh();
  };

  return (
    <>
      <button
        onClick={(e) => {
          e.preventDefault();
          e.stopPropagation();
          setOpen(true);
        }}
        title="Delete this map"
        aria-label={`Delete ${title}`}
        className="relative z-10 grid place-items-center w-9 h-9 rounded-full text-ink/40 hover:text-coral-dark hover:bg-coral/10 transition"
      >
        <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
          <path d="M3 6h18M8 6V4a1 1 0 0 1 1-1h6a1 1 0 0 1 1 1v2M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6M10 11v6M14 11v6" />
        </svg>
      </button>
      {open &&
        createPortal(
        <div className="fixed inset-0 z-50 grid place-items-center bg-ink/40 p-4" onClick={() => !busy && setOpen(false)} role="presentation">
          <div role="alertdialog" aria-modal="true" aria-labelledby={`del-${id}`} className="w-full max-w-sm rounded-3xl bg-white p-6 shadow-2xl space-y-3" onClick={(e) => e.stopPropagation()}>
            <div className="text-3xl">🗑️</div>
            <h3 id={`del-${id}`} className="font-display text-2xl font-extrabold">Delete “{title}”?</h3>
            <p className="text-sm text-ink/60">This removes the map from your account for good. It can&apos;t be undone. Orders you&apos;ve already placed aren&apos;t affected.</p>
            {err && <p className="text-sm font-bold text-coral-dark">{err}</p>}
            <div className="flex justify-end gap-2 pt-2">
              <button autoFocus onClick={() => setOpen(false)} disabled={busy} className="rounded-full border-2 border-ink/15 px-5 py-2.5 font-bold">
                Keep it
              </button>
              <button onClick={remove} disabled={busy} className="rounded-full bg-coral-dark px-5 py-2.5 font-extrabold text-white disabled:opacity-50">
                {busy ? "Deleting…" : "Delete"}
              </button>
            </div>
          </div>
        </div>,
          document.body,
        )}
    </>
  );
}
