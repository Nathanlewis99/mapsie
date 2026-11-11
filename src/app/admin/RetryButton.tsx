"use client";
import { useState } from "react";

export default function RetryButton({ id }: { id: string }) {
  const [state, setState] = useState("");
  return (
    <button
      className="font-bold text-ink/60 hover:text-ink"
      onClick={async () => {
        if (!confirm("Re-render and resend this order to the printer?")) return;
        setState("…");
        const r = await fetch(`/api/admin/orders/${id}/retry`, { method: "POST" });
        setState(r.ok ? "Queued ✓" : "Failed");
      }}
    >
      {state || "Re-send"}
    </button>
  );
}
