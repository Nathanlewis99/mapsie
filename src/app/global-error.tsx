"use client";
import { useEffect } from "react";
import { reportError } from "@/components/ErrorReporter";

// Last resort, when even the site's layout fails: a bare page with buttons that do a full reload.
export default function GlobalError({ error }: { error: Error & { digest?: string } }) {
  useEffect(() => reportError(error, "render"), [error]);
  return (
    <html lang="en">
      <body style={{ margin: 0, background: "#fbf6ee", color: "#1f2430", fontFamily: "system-ui, sans-serif" }}>
        <main style={{ maxWidth: 480, margin: "0 auto", padding: "80px 24px", textAlign: "center" }}>
          <div style={{ fontSize: 48 }}>🧭</div>
          <h1 style={{ fontFamily: "Georgia, serif" }}>We took a wrong turn</h1>
          <p style={{ opacity: 0.6 }}>Something went wrong. Your map design is saved in this browser.</p>
          <p>
            <button onClick={() => window.location.reload()} style={{ background: "#ff6b4a", color: "#fff", border: 0, borderRadius: 999, padding: "10px 20px", fontWeight: 800, cursor: "pointer" }}>Try again</button>{" "}
            {/* eslint-disable-next-line @next/next/no-html-link-for-pages -- a full page load is the point here */}
            <a href="/" style={{ color: "#1f2430", fontWeight: 700, marginLeft: 12 }}>Home</a>
          </p>
        </main>
      </body>
    </html>
  );
}
