import Link from "next/link";
import Logo from "@/components/Logo";
import { optOut } from "@/lib/server/db";
import { unsubscribeTokenValid } from "@/lib/server/email";
import { COMPANY } from "@/lib/company";

export const dynamic = "force-dynamic";
export const metadata = { title: "Unsubscribe · Mapsie", robots: { index: false } };

/** One click from a reminder email: no more reminders or offers (order emails still arrive). */
export default async function Unsubscribe({ searchParams }: { searchParams: Promise<{ e?: string; t?: string }> }) {
  const { e, t } = await searchParams;
  const ok = !!e && unsubscribeTokenValid(e, t);
  if (ok) await optOut(e!);
  return (
    <main className="min-h-dvh grid place-items-center px-4">
      <div className="max-w-md w-full rounded-3xl bg-white p-8 shadow-sm space-y-4 text-center">
        <Link href="/" className="font-display text-3xl font-extrabold block"><Logo /></Link>
        {ok ? (
          <>
            <h1 className="font-display text-2xl font-extrabold">You&apos;re unsubscribed</h1>
            <p className="text-ink/70 text-sm">We won&apos;t send {e} any more reminders or offers. You&apos;ll still get emails about orders you place.</p>
          </>
        ) : (
          <>
            <h1 className="font-display text-2xl font-extrabold">That link didn&apos;t work</h1>
            <p className="text-ink/70 text-sm">Email <a className="underline" href={`mailto:${COMPANY.supportEmail}`}>{COMPANY.supportEmail}</a> and we&apos;ll unsubscribe you straight away.</p>
          </>
        )}
      </div>
    </main>
  );
}
