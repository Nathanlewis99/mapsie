import Link from "next/link";
import { notFound, redirect } from "next/navigation";
import Logo from "@/components/Logo";
import { getDesign, getOrder } from "@/lib/server/db";
import { etsyToken, etsyTokenValid } from "@/lib/server/etsy";
import { FRAMES, getProduct } from "@/lib/products";
import { normalizeDesign } from "@/lib/types";
import SendToPrint, { Preview } from "./SendToPrint";

export const dynamic = "force-dynamic";
export const metadata = { title: "Send your map to print · Mapsie" };

export default async function Confirm({ params, searchParams }: { params: Promise<{ orderId: string }>; searchParams: Promise<{ k?: string; d?: string }> }) {
  const { orderId } = await params;
  const { k, d } = await searchParams;
  const o = await getOrder(orderId);
  if (!o?.etsy || !o.print || !etsyTokenValid(orderId, k)) notFound();
  if (o.status !== "awaiting_design") redirect(`/order/${orderId}`);
  const raw = d ? await getDesign(d) : null;
  if (!raw) redirect(`/create?etsy=${orderId}&k=${etsyToken(orderId)}`);
  // Show it exactly as it will be printed: with the size and frame from the Etsy order.
  const design = { ...normalizeDesign(raw), productId: o.print.productId, frame: o.print.frame, paper: "ema", mount: "none", glaze: "perspex" } as ReturnType<typeof normalizeDesign>;
  const frame = FRAMES.find((f) => f.id === o.print!.frame);
  return (
    <main className="max-w-5xl mx-auto px-4 sm:px-6 py-8 space-y-6">
      <div className="flex items-center justify-between">
        <Link href="/" className="font-display text-2xl font-extrabold"><Logo /></Link>
        <Link href={`/create?etsy=${orderId}&k=${k}`} className="text-sm font-bold text-ink/60 hover:text-ink">← Back to editing</Link>
      </div>
      <div className="grid gap-8 md:grid-cols-[1fr_380px] items-start">
        <Preview design={design} />
        <div className="rounded-3xl bg-white p-6 shadow-sm space-y-5">
          <div>
            <h1 className="font-display text-3xl font-extrabold">Ready to print?</h1>
            <p className="text-sm text-ink/60 mt-1">Etsy order {o.etsy.receiptId}{o.etsy.of > 1 ? ` · print ${o.etsy.unit} of ${o.etsy.of}` : ""}</p>
          </div>
          <dl className="text-sm space-y-2">
            <div className="flex justify-between gap-4"><dt className="text-ink/50">Print</dt><dd className="font-bold text-right">{getProduct(o.print.productId).label}, {frame && frame.id !== "none" ? `${frame.label} frame` : "unframed"}</dd></div>
            <div className="flex justify-between gap-4"><dt className="text-ink/50">Title</dt><dd className="font-bold text-right">{design.title || "—"}</dd></div>
            <div className="flex justify-between gap-4"><dt className="text-ink/50">Stops</dt><dd className="font-bold text-right">{design.stops.length}</dd></div>
            <div className="flex justify-between gap-4">
              <dt className="text-ink/50">Delivery to</dt>
              <dd className="font-bold text-right">{[o.address?.name, o.address?.city, o.address?.postcode, o.address?.country].filter(Boolean).join(", ")}</dd>
            </div>
          </dl>
          <p className="text-xs text-ink/50">
            Please check spelling, dates and stickers. Once it goes to print it can&apos;t be changed, though you&apos;ll have an hour to reopen it if you spot something.
            The delivery address is the one from Etsy; to change it, message us on Etsy.
          </p>
          <SendToPrint orderId={orderId} k={k!} designId={d!} email={o.email} />
        </div>
      </div>
    </main>
  );
}
