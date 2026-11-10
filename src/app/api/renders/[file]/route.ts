import { promises as fs } from "fs";
import path from "path";
import { rendersDir } from "@/lib/server/db";

export async function GET(_: Request, { params }: { params: Promise<{ file: string }> }) {
  const { file } = await params;
  if (!/^[\w-]+\.png$/.test(file)) return new Response("not found", { status: 404 });
  try {
    const buf = await fs.readFile(path.join(await rendersDir(), file));
    return new Response(new Uint8Array(buf), { headers: { "content-type": "image/png", "cache-control": "private, max-age=3600" } });
  } catch {
    return new Response("not found", { status: 404 });
  }
}
