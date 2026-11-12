import { NextResponse } from "next/server";
import { dbKind } from "@/lib/server/db";

// Load balancer health check: the server is up and can reach its database.
export async function GET() {
  try {
    return NextResponse.json({ ok: true, role: process.env.MAPSIE_ROLE ?? "all", db: await dbKind() });
  } catch (e) {
    return NextResponse.json({ ok: false, error: String(e).slice(0, 200) }, { status: 503 });
  }
}
