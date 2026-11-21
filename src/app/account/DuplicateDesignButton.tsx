"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";

/** Makes a copy of a saved map (stickers, labels and photos all in place) and opens it. */
export default function DuplicateDesignButton({ id, title }: { id: string; title: string }) {
  const [busy, setBusy] = useState(false);
  const router = useRouter();
  return (
    <button
      onClick={async (e) => {
        e.preventDefault();
        e.stopPropagation();
        setBusy(true);
        const r = await fetch(`/api/me/designs/${id}/duplicate`, { method: "POST" }).catch(() => null);
        if (!r?.ok) {
          setBusy(false);
          alert("Couldn't copy that map. Please try again.");
          return;
        }
        router.push(`/create?saved=${(await r.json()).id}&copied=1`);
      }}
      disabled={busy}
      title="Make a copy to try a different style or layout"
      aria-label={`Duplicate ${title}`}
      className="relative z-10 rounded-full px-2.5 h-9 text-sm font-bold text-ink/55 hover:text-ink hover:bg-ink/5 transition disabled:opacity-50"
    >
      {busy ? "Copying…" : "⧉ Duplicate"}
    </button>
  );
}
