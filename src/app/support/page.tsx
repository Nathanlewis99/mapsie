import Link from "next/link";
import Logo from "@/components/Logo";
import SiteFooter from "@/components/SiteFooter";
import { currentUser } from "@/lib/server/auth";
import SupportForm from "./SupportForm";

export const dynamic = "force-dynamic";
export const metadata = { title: "Help & support · Mapsie", description: "Get help with a Mapsie order: delivery, damage, print quality or anything else." };

export default async function Support({ searchParams }: { searchParams: Promise<{ order?: string }> }) {
  const { order } = await searchParams;
  const user = await currentUser();
  return (
    <div className="min-h-dvh flex flex-col">
      <header className="max-w-3xl w-full mx-auto px-4 sm:px-6 py-5">
        <Link href="/" className="font-display text-3xl font-extrabold"><Logo /></Link>
      </header>
      <main className="max-w-3xl w-full mx-auto px-4 sm:px-6 pb-16 flex-1 space-y-6">
        <div>
          <h1 className="font-display text-4xl font-extrabold">How can we help?</h1>
          <p className="text-ink/60 mt-2">
            Tell us about your order and what&apos;s wrong, and we&apos;ll get back to you within one working day. If your print arrived damaged or faulty,
            we&apos;ll put it right free (see our <Link href="/legal/refunds" className="underline">returns policy</Link>).
          </p>
        </div>
        <div className="rounded-3xl bg-white p-6 sm:p-8 shadow-sm">
          <SupportForm initialOrder={order ?? ""} initialEmail={user?.email ?? ""} />
        </div>
      </main>
      <SiteFooter />
    </div>
  );
}
