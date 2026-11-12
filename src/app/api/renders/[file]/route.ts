import { promises as fs } from "fs";
import path from "path";
import { rendersDir } from "@/lib/server/db";

// Print files live on the render worker's disk. A web server that doesn't have
// the file asks the worker for it over Render's private network.
export async function GET(_: Request, { params }: { params: Promise<{ file: string }> }) {
  const { file } = await params;
  if (!/^[\w-]+\.png$/.test(file)) return new Response("not found", { status: 404 });
  const headers = { "content-type": "image/png", "cache-control": "private, max-age=3600" };
  try {
    const p = path.join(await rendersDir(), file);
    const buf = await fs.readFile(p);
    return new Response(new Uint8Array(buf), { headers });
  } catch {
    const worker = process.env.RENDER_WORKER_URL;
    if (!worker) return new Response("not found", { status: 404 });
    const r = await fetch(`${worker.replace(/\/$/, "")}/api/renders/${file}`).catch(() => null);
    if (!r?.ok || !r.body) return new Response("not found", { status: 404 });
    return new Response(r.body, { headers });
  }
}
