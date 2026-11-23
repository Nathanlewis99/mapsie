import Link from "next/link";
import { redirect } from "next/navigation";
import Logo from "@/components/Logo";
import { currentPartnerLogin } from "@/lib/server/partnerAuth";

export const dynamic = "force-dynamic";
export const metadata = { title: "Partner sign in · Mapsie", robots: { index: false } };

export default async function PartnerSignIn({ searchParams }: { searchParams: Promise<{ sent?: string; expired?: string; error?: string; slow?: string }> }) {
  if (await currentPartnerLogin()) redirect("/partner");
  const q = await searchParams;
  return (
    <main className="min-h-dvh grid place-items-center px-4 py-12">
      <div className="w-full max-w-md rounded-3xl bg-white p-8 shadow-sm">
        <Link href="/" className="font-display text-3xl font-extrabold"><Logo /></Link>
        <h1 className="mt-6 text-2xl font-extrabold">Partner dashboard</h1>
        {q.sent ? (
          <p className="mt-4 rounded-2xl bg-sand px-4 py-3 font-bold">If that address is registered with us, we&apos;ve emailed you a sign-in link. It works once and lasts 30 minutes.</p>
        ) : (
          <>
            <p className="mt-2 text-ink/60">Enter the email address we have for you and we&apos;ll send you a link to sign in. No password needed.</p>
            {q.expired && <p className="mt-4 rounded-2xl bg-sand px-4 py-3 text-sm font-bold">That link has expired or was already used. Ask for a new one below.</p>}
            {q.error && <p className="mt-4 rounded-2xl bg-sand px-4 py-3 text-sm font-bold">Please enter a valid email address.</p>}
            {q.slow && <p className="mt-4 rounded-2xl bg-sand px-4 py-3 text-sm font-bold">You&apos;ve asked for a few links already. Please check your inbox, or try again in an hour.</p>}
            <form action="/api/partner/signin" method="post" className="mt-5 space-y-3">
              <input name="email" type="email" required autoComplete="email" placeholder="you@company.com" className="w-full rounded-xl border border-ink/15 px-3 py-3" />
              <button className="w-full rounded-full bg-coral px-6 py-3.5 font-extrabold text-white">Email me a sign-in link</button>
            </form>
          </>
        )}
        <p className="mt-6 text-sm text-ink/50">Not a partner yet? <Link href="/partners" className="font-bold underline">See how it works</Link>.</p>
      </div>
    </main>
  );
}
