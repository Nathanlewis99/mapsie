"use client";
import { useRouter } from "next/navigation";

export default function ResolveButton({ fingerprint }: { fingerprint: string }) {
  const router = useRouter();
  return (
    <button
      onClick={async () => {
        await fetch("/api/admin/errors", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ fingerprint }) });
        router.refresh();
      }}
      className="rounded-full border-2 border-ink/15 px-3 py-1 text-xs font-bold hover:border-ink/40"
    >
      Resolve
    </button>
  );
}
