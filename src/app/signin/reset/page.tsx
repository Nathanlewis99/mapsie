import Link from "next/link";
import Logo from "@/components/Logo";
import { ResetForm } from "../PasswordForms";

export const dynamic = "force-dynamic";
export const metadata = { title: "Choose a new password · Mapsie" };

export default async function Reset({ searchParams }: { searchParams: Promise<{ token?: string }> }) {
  const { token } = await searchParams;
  return (
    <main className="min-h-dvh grid place-items-center px-4 py-12">
      <div className="w-full max-w-sm space-y-6">
        <Link href="/" className="font-display text-3xl font-extrabold block text-center"><Logo /></Link>
        <div className="rounded-3xl bg-white p-7 shadow-sm space-y-5">
          <h1 className="font-display text-3xl font-extrabold">Choose a new password</h1>
          {token ? (
            <ResetForm token={token} />
          ) : (
            <p className="text-sm text-ink/60">
              This link is incomplete. <Link href="/signin/forgot" className="underline font-bold">Ask for a new one.</Link>
            </p>
          )}
        </div>
      </div>
    </main>
  );
}
