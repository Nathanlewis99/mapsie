import { notFound } from "next/navigation";
import { getDesign } from "@/lib/server/db";
import Checkout from "./Checkout";

export default async function Page({ params }: { params: Promise<{ designId: string }> }) {
  const { designId } = await params;
  const design = await getDesign(designId);
  if (!design) notFound();
  return <Checkout design={design} />;
}
