import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { getDesign } from "@/lib/server/db";
import { normalizeDesign } from "@/lib/types";
import SharedView from "./SharedView";

export async function generateMetadata({ params }: { params: Promise<{ id: string }> }): Promise<Metadata> {
  const d = await getDesign((await params).id);
  return { title: d ? `${d.title} · Mapsie` : "Mapsie", description: d ? `${d.stops.map((s) => s.name).join(" → ")}. Made with Mapsie.` : undefined };
}

export default async function SharedPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const d = await getDesign(id);
  if (!d) notFound();
  return <SharedView design={normalizeDesign(d)} />;
}
