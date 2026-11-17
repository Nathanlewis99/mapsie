import { NextResponse } from "next/server";
import { putKv } from "@/lib/server/db";
import { CHANNELS } from "@/lib/channels";
import { publicUrl } from "@/lib/server/urls";

// Admin only (middleware): save ad spend per channel for a reporting window.
export async function POST(req: Request) {
  const f = await req.formData();
  const days = [7, 30, 90].includes(Number(f.get("days"))) ? Number(f.get("days")) : 30;
  const spend: Record<string, number> = {};
  for (const c of CHANNELS) {
    const v = Number(String(f.get(c.id) ?? "").replace(/[^\d.]/g, ""));
    if (v > 0) spend[c.id] = Math.round(v * 100) / 100;
  }
  await putKv(`adspend:${days}`, spend);
  return NextResponse.redirect(`${publicUrl()}/admin/channels?days=${days}`, { status: 303 });
}
