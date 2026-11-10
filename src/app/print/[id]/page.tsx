import { notFound } from "next/navigation";
import { getDesign } from "@/lib/server/db";
import PrintView from "./PrintView";

// Bare page the renderer screenshots. It lays the poster out at the same CSS
// width the customer designed at; the renderer raises the pixel density.
export default async function PrintPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const design = await getDesign(id);
  if (!design) notFound();
  return <PrintView design={design} />;
}
