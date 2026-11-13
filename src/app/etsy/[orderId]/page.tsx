import Link from "next/link";
import { notFound, redirect } from "next/navigation";
import Logo from "@/components/Logo";
import { getOrder, listOrdersByEtsyReceipt } from "@/lib/server/db";
import { etsyToken, etsyTokenValid } from "@/lib/server/etsy";
import { FRAMES, getProduct } from "@/lib/products";

export const dynamic = "force-dynamic";
export const metadata = { title: "Your Etsy map · Mapsie" };

/** An Etsy buyer's order: start designing, or see where it's got to. */
export default async function EtsyOrder({ params, searchParams }: { params: Promise<{ orderId: string }>; searchParams: Promise<{ k?: string }> }) {
  const { orderId } = await params;
  const { k } = await searchParams;
  const o = await getOrder(orderId);
  if (!o?.etsy || !o.print || !etsyTokenValid(orderId, k)) notFound();
  if (o.status !== "awaiting_design") redirect(`/order/${orderId}`);
  const siblings = o.etsy.of > 1 ? await listOrdersByEtsyReceipt(o.etsy.receiptId) : [];
  const size = getProduct(o.print.productId);
  const frame = FRAMES.find((f) => f.id === o.print!.frame);
  return (
    <main className="min-h-dvh grid place-items-center px-4 py-12">
      <div className="w-full max-w-md space-y-6">
        <Link href="/" className="font-display text-3xl font-extrabold block text-center"><Logo /></Link>
        <div className="rounded-3xl bg-white p-7 shadow-sm space-y-5">
          <div>
            <h1 className="font-display text-3xl font-extrabold">Let&apos;s design your map</h1>
            <p className="text-ink/60 mt-2 text-sm">Etsy order {o.etsy.receiptId}{o.etsy.of > 1 ? ` · print ${o.etsy.unit} of ${o.etsy.of}` : ""}</p>
          </div>
          <div className="rounded-2xl bg-sand/60 px-4 py-3 text-sm">
            <div className="font-extrabold">{size.label} print · {frame && frame.id !== "none" ? `${frame.label} frame` : "unframed"}</div>
            <div className="text-ink/60">Delivered to {o.address?.name}, {o.address?.city}</div>
          </div>
          <ol className="text-sm text-ink/70 space-y-1 list-decimal pl-5">
            <li>Add the places you went, in order.</li>
            <li>Choose a map style, add stickers and your title.</li>
            <li>Press <b>Send to print</b>. You&apos;ll see a final preview first.</li>
          </ol>
          <Link
            href={`/create?new=1&etsy=${o.id}&k=${etsyToken(o.id)}`}
            className="block w-full rounded-full bg-coral px-5 py-3 text-center font-extrabold text-white shadow-lg shadow-coral/30"
          >
            Start designing
          </Link>
          {siblings.length > 1 && (
            <div className="text-sm">
              <div className="font-bold mb-1">The prints in this order</div>
              <ul className="space-y-1">
                {siblings.map((x) => (
                  <li key={x.id} className="flex justify-between">
                    <span>Print {x.etsy?.unit}</span>
                    {x.status === "awaiting_design" ? (
                      x.id === o.id ? <span className="text-ink/50">this one</span> : <Link className="font-bold underline" href={`/etsy/${x.id}?k=${etsyToken(x.id)}`}>Design it</Link>
                    ) : (
                      <span className="text-sea font-bold">Sent to print</span>
                    )}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    </main>
  );
}
