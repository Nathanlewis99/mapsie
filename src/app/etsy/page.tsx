import Link from "next/link";
import Logo from "@/components/Logo";
import LookupForm from "./LookupForm";

export const metadata = { title: "Design your Etsy map · Mapsie" };

export default function EtsyStart() {
  return (
    <main className="min-h-dvh grid place-items-center px-4 py-12">
      <div className="w-full max-w-md space-y-6">
        <Link href="/" className="font-display text-3xl font-extrabold block text-center"><Logo /></Link>
        <div className="rounded-3xl bg-white p-7 shadow-sm space-y-5">
          <div>
            <h1 className="font-display text-3xl font-extrabold">Bought your map on Etsy?</h1>
            <p className="text-ink/60 mt-2 text-sm">
              Thank you! Find your order and design your map: add the places you went, pick a style and add stickers. You&apos;ll see exactly how it
              looks before it&apos;s printed, and there&apos;s nothing more to pay.
            </p>
          </div>
          <LookupForm />
          <p className="text-xs text-ink/50">
            Your order number is in your Etsy purchase email and under Purchases on Etsy. If we have your email, we&apos;ve also sent you a link.
          </p>
        </div>
      </div>
    </main>
  );
}
