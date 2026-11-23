"use client";
import { useState } from "react";

export default function CopyLink({ label, url }: { label: string; url: string }) {
  const [done, setDone] = useState(false);
  return (
    <div className="flex flex-wrap items-center gap-2 rounded-2xl bg-sand/50 px-4 py-3">
      <div className="min-w-0 flex-1">
        <div className="text-sm font-bold">{label}</div>
        <a href={url} target="_blank" rel="noreferrer" className="font-mono text-xs break-all text-ink/70 underline">{url}</a>
      </div>
      <button
        type="button"
        onClick={() => navigator.clipboard.writeText(url).then(() => (setDone(true), setTimeout(() => setDone(false), 1500)))}
        className="rounded-full border-2 border-ink/15 px-4 py-1.5 text-sm font-extrabold hover:border-coral"
      >
        {done ? "Copied ✓" : "Copy"}
      </button>
    </div>
  );
}
