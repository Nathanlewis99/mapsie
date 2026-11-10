import { NextResponse } from "next/server";
import { getOrder } from "@/lib/server/db";

export async function GET(_: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const o = await getOrder(id);
  if (!o) return NextResponse.json({ error: "not found" }, { status: 404 });
  const { status, renderFile, renderInfo, totalGbp, shipping, printProviderOrderId, designId } = o;
  return NextResponse.json({ status, renderFile, renderInfo, totalGbp, shipping, printProviderOrderId, designId });
}
