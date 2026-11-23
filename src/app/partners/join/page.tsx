import type { Metadata } from "next";
import Link from "next/link";
import Logo from "@/components/Logo";
import ApplyForm from "./ApplyForm";

export const metadata: Metadata = { title: "Become a Mapsie partner", description: "Create a Mapsie partner account: your own page of routes, commission on every order, and gift cards at trade prices.", alternates: { canonical: "/partners/join" } };

export default async function Join({ searchParams }: { searchParams: Promise<{ sent?: string; expired?: string; error?: string }> }) {
  const q = await searchParams;
  return (
    <main className="min-h-dvh px-4 py-10">
      <div className="mx-auto max-w-2xl">
        <div className="flex justify-between items-center">
          <Link href="/" className="font-display text-3xl font-extrabold"><Logo /></Link>
          <Link href="/partner/signin" className="text-sm font-bold hover:text-coral-dark">Partner sign in</Link>
        </div>
        <div className="mt-8 rounded-3xl bg-white p-6 sm:p-8 shadow-sm">
          {q.sent ? (
            <>
              <h1 className="font-display text-3xl font-extrabold">Thanks, your application is in</h1>
              <p className="mt-3 text-ink/70">We&apos;ll check it and email you, usually within a working day. Once you&apos;re approved you can sign in to your dashboard with the same email address.</p>
            </>
          ) : (
            <>
              <h1 className="font-display text-3xl font-extrabold">Become a Mapsie partner</h1>
              <p className="mt-2 text-ink/70">Free to join. You&apos;ll get your own page of routes for your customers, 10% commission on every order, and gift cards at trade prices. <Link href="/partners" className="underline font-bold">How it works</Link></p>
              {q.expired && <p className="mt-4 rounded-2xl bg-sand px-4 py-3 text-sm font-bold">That confirmation link has expired. Please fill in the form again.</p>}
              {q.error && <p className="mt-4 rounded-2xl bg-sand px-4 py-3 text-sm font-bold">Sorry, something went wrong. Please try the link again, or email hello@mapsie.shop.</p>}
              <ApplyForm />
            </>
          )}
        </div>
      </div>
    </main>
  );
}
