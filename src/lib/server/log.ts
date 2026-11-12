import { createHash } from "node:crypto";
import { recordError } from "./db";

// Error logging. Every error goes to the server log as one JSON line (visible in
// Render's Logs tab) and into the errors table, grouped by fingerprint so the
// admin page shows "this happened 37 times" rather than 37 rows.
// Never throws: logging must not break the thing that failed.

const clean = (m: string) => m.replace(/\b(ord|usr|sd)_[\w-]+/g, "<id>").replace(/\d+/g, "#").slice(0, 300);

export function fingerprint(source: string, scope: string, message: string, stack?: string) {
  const frame = stack?.split("\n").find((l) => /^\s*at /.test(l))?.trim().replace(/:\d+:\d+\)?$/, "") ?? "";
  return createHash("sha1").update(`${source}|${scope}|${clean(message)}|${frame}`).digest("hex").slice(0, 16);
}

export async function logError(scope: string, err: unknown, context?: Record<string, unknown>, source: "server" | "client" = "server") {
  const e = err instanceof Error ? err : new Error(typeof err === "string" ? err : JSON.stringify(err));
  const line = { level: "error", source, scope, message: e.message, context, stack: e.stack?.split("\n").slice(0, 6).join("\n") };
  console.error(JSON.stringify(line));
  try {
    await recordError({ fingerprint: fingerprint(source, scope, e.message, e.stack), source, scope, message: e.message, stack: e.stack, context });
  } catch (dbErr) {
    console.error(JSON.stringify({ level: "error", scope: "log", message: `could not store error: ${String(dbErr)}` }));
  }
}

export function logInfo(scope: string, message: string, context?: Record<string, unknown>) {
  console.log(JSON.stringify({ level: "info", scope, message, context }));
}
