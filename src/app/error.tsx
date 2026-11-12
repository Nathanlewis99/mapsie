"use client";
import { useEffect } from "react";
import Link from "next/link";
import { reportError } from "@/components/ErrorReporter";

export default function ErrorPage({ error, reset }: { error: Error & { digest?: string }; reset: () => void }) {
  useEffect(() => reportError(error, "render"), [error]);
  return (
    <main className="max-w-lg mx-auto px-6 py-20 text-center space-y-4">
      <div className="text-5xl">🧭</div>
      <h1 className="font-display text-3xl font-extrabold">We took a wrong turn</h1>
      <p className="text-ink/60">Something went wrong on this page. We&apos;ve been told about it. Your map design is saved in this browser.</p>
      <div className="flex justify-center gap-3">
        <button onClick={reset} className="rounded-full bg-coral px-5 py-2.5 font-extrabold text-white">Try again</button>
        <Link href="/" className="rounded-full border-2 border-ink/15 px-5 py-2.5 font-bold">Home</Link>
      </div>
    </main>
  );
}
