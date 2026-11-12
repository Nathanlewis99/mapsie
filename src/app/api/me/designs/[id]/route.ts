import { NextResponse } from "next/server";
import { currentUser } from "@/lib/server/auth";
import { deleteSavedDesign, getSavedDesign } from "@/lib/server/db";

export async function GET(_: Request, { params }: { params: Promise<{ id: string }> }) {
  const user = await currentUser();
  if (!user) return NextResponse.json({ error: "Sign in first" }, { status: 401 });
  const d = await getSavedDesign(user.id, (await params).id);
  return d ? NextResponse.json(d) : NextResponse.json({ error: "Not found" }, { status: 404 });
}

export async function DELETE(_: Request, { params }: { params: Promise<{ id: string }> }) {
  const user = await currentUser();
  if (!user) return NextResponse.json({ error: "Sign in first" }, { status: 401 });
  await deleteSavedDesign(user.id, (await params).id);
  return NextResponse.json({ ok: true });
}
