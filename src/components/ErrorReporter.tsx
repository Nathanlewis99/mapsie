"use client";
import { useEffect } from "react";

/** Sends uncaught browser errors to /api/errors (at most a few per page view). */
export function reportError(err: unknown, kind = "error") {
  try {
    const w = window as unknown as { __mapsieErrs?: number };
    w.__mapsieErrs = (w.__mapsieErrs ?? 0) + 1;
    if (w.__mapsieErrs > 5) return;
    const e = err instanceof Error ? err : new Error(String((err as { message?: string })?.message ?? err));
    // Noise from browser extensions and cancelled requests.
    if (/ResizeObserver loop|AbortError|chrome-extension:|moz-extension:/.test(`${e.message} ${e.stack}`)) return;
    const body = JSON.stringify({ message: e.message, stack: e.stack, url: location.pathname, kind });
    if (!navigator.sendBeacon?.("/api/errors", new Blob([body], { type: "application/json" })))
      fetch("/api/errors", { method: "POST", body, headers: { "content-type": "application/json" }, keepalive: true }).catch(() => {});
  } catch {
    // never let reporting break the page
  }
}

export default function ErrorReporter() {
  useEffect(() => {
    // After a site update, code still open in this tab can ask for files that no longer exist.
    // Reload once to pick up the new version (at most once a minute, so it can never loop).
    const maybeReload = (err: unknown) => {
      const s = `${(err as Error)?.name ?? ""} ${(err as Error)?.message ?? err}`;
      if (!/ChunkLoadError|Loading (CSS )?chunk|dynamically imported module|Failed to find Server Action/i.test(s)) return false;
      try {
        const last = Number(sessionStorage.getItem("mapsie-reloaded") ?? 0);
        if (Date.now() - last < 60_000) return false;
        sessionStorage.setItem("mapsie-reloaded", String(Date.now()));
      } catch {
        return false;
      }
      window.location.reload();
      return true;
    };
    const onError = (e: ErrorEvent) => maybeReload(e.error ?? e.message) || reportError(e.error ?? e.message);
    const onRejection = (e: PromiseRejectionEvent) => maybeReload(e.reason) || reportError(e.reason, "promise");
    window.addEventListener("error", onError);
    window.addEventListener("unhandledrejection", onRejection);
    return () => {
      window.removeEventListener("error", onError);
      window.removeEventListener("unhandledrejection", onRejection);
    };
  }, []);
  return null;
}
