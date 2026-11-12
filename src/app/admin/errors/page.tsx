import Link from "next/link";
import Logo from "@/components/Logo";
import { listErrors } from "@/lib/server/db";
import ResolveButton from "./ResolveButton";

export const dynamic = "force-dynamic";

const ago = (iso: string) => {
  const m = Math.round((Date.now() - new Date(iso).getTime()) / 60000);
  return m < 60 ? `${m}m ago` : m < 1440 ? `${Math.round(m / 60)}h ago` : `${Math.round(m / 1440)}d ago`;
};

export default async function Errors({ searchParams }: { searchParams: Promise<{ all?: string }> }) {
  const all = (await searchParams).all === "1";
  const errors = await listErrors(all);
  return (
    <main className="max-w-6xl mx-auto px-6 py-10 space-y-6">
      <div>
        <Link href="/" className="font-display text-2xl font-extrabold"><Logo /></Link>
        <h1 className="text-3xl font-extrabold mt-2">Errors</h1>
        <p className="text-sm text-ink/60 mt-1">
          From the servers and customers&apos; browsers, grouped. Resolving hides a group until it happens again. Full logs: Render dashboard → service → Logs.
        </p>
        <div className="flex gap-4 text-sm font-bold mt-1">
          <Link href="/admin" className="text-coral-dark">← Orders</Link>
          <Link href={all ? "/admin/errors" : "/admin/errors?all=1"} className="text-coral-dark">{all ? "Hide resolved" : "Show resolved"}</Link>
        </div>
      </div>
      {errors.length === 0 && <div className="rounded-2xl bg-sea/10 p-6 font-bold">✅ No open errors.</div>}
      <div className="space-y-3">
        {errors.map((e) => (
          <details key={e.fingerprint} className="rounded-2xl bg-white shadow-sm p-4">
            <summary className="flex flex-wrap items-center gap-3 cursor-pointer">
              <span className={`rounded-full px-2 py-0.5 text-xs font-extrabold ${e.source === "client" ? "bg-amber-100 text-amber-800" : "bg-coral/15 text-coral-dark"}`}>
                {e.source === "client" ? "browser" : "server"}
              </span>
              <span className="text-xs font-bold text-ink/50">{e.scope}</span>
              <span className="font-bold flex-1 min-w-0 truncate">{e.message}</span>
              <span className="text-sm font-extrabold">×{e.count}</span>
              <span className="text-xs text-ink/50">{ago(e.lastSeen)}</span>
              {!e.resolved && <ResolveButton fingerprint={e.fingerprint} />}
            </summary>
            <div className="mt-3 space-y-2 text-xs">
              <div className="text-ink/50">First seen {new Date(e.firstSeen).toLocaleString("en-GB")} · last {new Date(e.lastSeen).toLocaleString("en-GB")}</div>
              {e.context && <pre className="whitespace-pre-wrap break-all rounded-xl bg-sand/60 p-3">{e.context}</pre>}
              {e.stack && <pre className="whitespace-pre-wrap break-all rounded-xl bg-ink text-white/80 p-3 max-h-72 overflow-auto">{e.stack}</pre>}
            </div>
          </details>
        ))}
      </div>
    </main>
  );
}
