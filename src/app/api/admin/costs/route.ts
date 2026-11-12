import { NextResponse } from "next/server";
import { refreshCosts } from "@/lib/server/prodigiCosts";

export const maxDuration = 120;

/** Admin: re-download Prodigi's price sheets. */
export async function POST() {
  try {
    const t = await refreshCosts();
    return NextResponse.json({ ok: true, skus: Object.values(t).reduce((n, r) => n + Object.keys(r).length, 0) });
  } catch (e) {
    return NextResponse.json({ error: String(e) }, { status: 502 });
  }
}
