"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";

export default function DeleteDesignButton({ id, title }: { id: string; title: string }) {
  const [confirming, setConfirming] = useState(false);
  const router = useRouter();
  if (!confirming) return <button onClick={() => setConfirming(true)} className="font-bold text-ink/40 hover:text-ink">Delete</button>;
  return (
    <span className="flex gap-2">
      <button
        onClick={async () => {
          await fetch(`/api/me/designs/${id}`, { method: "DELETE" });
          router.refresh();
        }}
        className="font-extrabold text-coral-dark"
        aria-label={`Confirm delete ${title}`}
      >
        Delete it
      </button>
      <button onClick={() => setConfirming(false)} className="font-bold text-ink/40">Keep</button>
    </span>
  );
}
