"use client";
import { useEffect, useState } from "react";
import { reportError } from "@/components/ErrorReporter";

// If the site was updated while this page was open, the browser can be left holding a mix of old
// and new code, and nothing works until the page is fully reloaded. So both buttons here do a real
// page load rather than an in-app one, which always recovers.
export default function ErrorPage({ error, reset }: { error: Error & { digest?: string }; reset: () => void }) {
  const [tried, setTried] = useState(false);
  useEffect(() => reportError(error, "render"), [error]);
  const retry = () => {
    if (!tried && !staleCode(error)) {
      setTried(true);
      reset();
    } else window.location.reload();
  };
  return (
    <main className="max-w-lg mx-auto px-6 py-20 text-center space-y-4">
      <div className="text-5xl">🧭</div>
      <h1 className="font-display text-3xl font-extrabold">We took a wrong turn</h1>
      <p className="text-ink/60">Something went wrong on this page. We&apos;ve been told about it. Your map design is saved in this browser.</p>
      <div className="flex justify-center gap-3">
        <button onClick={retry} className="rounded-full bg-coral px-5 py-2.5 font-extrabold text-white">Try again</button>
        {/* A plain link, not an in-app one: a full page load always works. */}
        {/* eslint-disable-next-line @next/next/no-html-link-for-pages -- a full page load is the point here */}
        <a href="/" className="rounded-full border-2 border-ink/15 px-5 py-2.5 font-bold">Home</a>
      </div>
    </main>
  );
}

/** Errors that mean "this page has old code after an update": only a reload fixes them. */
function staleCode(e: unknown) {
  const s = `${(e as Error)?.name ?? ""} ${(e as Error)?.message ?? e}`;
  return /ChunkLoadError|Loading (CSS )?chunk|dynamically imported module|is not a function|Cannot read properties of undefined \(reading 'call'\)|Failed to find Server Action/i.test(s);
}
