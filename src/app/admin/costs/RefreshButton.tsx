"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";

export default function RefreshButton() {
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");
  const router = useRouter();
  return (
    <span className="flex items-center gap-3">
      {err && <span className="text-sm font-bold text-coral-dark">{err}</span>}
      <button
        disabled={busy}
        onClick={async () => {
          setBusy(true);
          setErr("");
          const r = await fetch("/api/admin/costs", { method: "POST" });
          if (!r.ok) setErr((await r.json()).error ?? "Failed");
          setBusy(false);
          router.refresh();
        }}
        className="rounded-full bg-ink px-4 py-2 text-sm font-extrabold text-white disabled:opacity-50"
      >
        {busy ? "Downloading Prodigi prices… (~30s)" : "↻ Refresh Prodigi costs"}
      </button>
    </span>
  );
}
