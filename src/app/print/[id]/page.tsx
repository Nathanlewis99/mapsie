import { notFound } from "next/navigation";
import { getDesign } from "@/lib/server/db";
import PrintView from "./PrintView";
import { normalizeDesign } from "@/lib/types";
import { printTokenValid } from "@/lib/server/printToken";

// Bare page the renderer screenshots. It lays the poster out at the same CSS
// width the customer designed at; the renderer raises the pixel density.
export default async function PrintPage({ params, searchParams }: { params: Promise<{ id: string }>; searchParams: Promise<{ t?: string }> }) {
  const { id } = await params;
  if (!printTokenValid(id, (await searchParams).t)) notFound();
  const design = await getDesign(id);
  if (!design) notFound();
  return <PrintView design={normalizeDesign(design)} />;
}
