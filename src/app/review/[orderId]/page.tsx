import Link from "next/link";
import { notFound } from "next/navigation";
import Logo from "@/components/Logo";
import { getOrder, getReviewForOrder } from "@/lib/server/db";
import { reviewTokenValid } from "@/lib/server/reviews";
import ReviewForm from "./ReviewForm";

export const dynamic = "force-dynamic";
export const metadata = { title: "Review your map · Mapsie", robots: { index: false } };

export default async function ReviewPage({ params, searchParams }: { params: Promise<{ orderId: string }>; searchParams: Promise<{ k?: string }> }) {
  const { orderId } = await params;
  const { k } = await searchParams;
  const o = await getOrder(orderId);
  if (!o || !reviewTokenValid(orderId, k)) notFound();
  const done = await getReviewForOrder(orderId);
  const first = o.address?.name?.split(" ")[0];
  return (
    <main className="min-h-dvh grid place-items-center px-4 py-10">
      <div className="w-full max-w-lg rounded-3xl bg-white p-7 shadow-sm space-y-5">
        <Link href="/" className="font-display text-3xl font-extrabold block text-center"><Logo /></Link>
        {done ? (
          <p className="text-center font-bold">Thank you{first ? `, ${first}` : ""}! We&apos;ve got your review.</p>
        ) : (
          <>
            <div className="text-center">
              <h1 className="font-display text-3xl font-extrabold">How&apos;s your map?</h1>
              <p className="text-ink/60 mt-1 text-sm">Order {orderId}</p>
            </div>
            <ReviewForm orderId={orderId} k={k!} defaultName={[first, o.address?.city].filter(Boolean).join(", ")} />
          </>
        )}
      </div>
    </main>
  );
}
