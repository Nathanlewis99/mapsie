import Link from "next/link";
import { notFound, redirect } from "next/navigation";
import Logo from "@/components/Logo";
import { getOrder } from "@/lib/server/db";
import { etsyTokenValid } from "@/lib/server/etsy";
import { etsyPrintLabel } from "@/lib/etsyOptions";
import SwitchPrint from "./SwitchPrint";

export const dynamic = "force-dynamic";
export const metadata = { title: "Change your print · Mapsie" };

/** An Etsy buyer changes their mind about the size, frame or paper. */
export default async function Change({ params, searchParams }: { params: Promise<{ orderId: string }>; searchParams: Promise<{ k?: string; d?: string }> }) {
  const { orderId } = await params;
  const { k, d } = await searchParams;
  const o = await getOrder(orderId);
  if (!o?.etsy || !o.print || !etsyTokenValid(orderId, k)) notFound();
  if (o.status !== "awaiting_design") redirect(`/order/${orderId}`);
  return (
    <main className="max-w-xl mx-auto px-4 sm:px-6 py-8 space-y-6">
      <div className="flex items-center justify-between">
        <Link href="/" className="font-display text-2xl font-extrabold"><Logo /></Link>
        <Link href={`/create?etsy=${orderId}&k=${k}${d ? `&d=${d}` : ""}`} className="text-sm font-bold text-ink/60 hover:text-ink">← Back to my map</Link>
      </div>
      <div>
        <h1 className="font-display text-3xl font-extrabold">Change your print</h1>
        <p className="text-sm text-ink/60 mt-1">
          Etsy order {o.etsy.receiptId}: you paid for <b>{etsyPrintLabel(o.print)}</b>. Pick what you&apos;d like instead.
        </p>
      </div>
      <SwitchPrint
        orderId={orderId}
        k={k!}
        designId={d}
        current={{ format: o.print.format ?? "print", productId: o.print.productId, frame: o.print.frame, paper: o.print.paper ?? "ema", mount: o.print.mount ?? "none" }}
        paid={o.total}
        currency={o.currency}
        pending={o.etsy.swap ? { code: o.etsy.swap.code, label: etsyPrintLabel(o.etsy.swap.to) } : null}
      />
    </main>
  );
}
