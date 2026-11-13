import Link from "next/link";
import Logo from "@/components/Logo";
import { ForgotForm } from "../PasswordForms";

export const metadata = { title: "Reset your password · Mapsie" };

export default function Forgot() {
  return (
    <main className="min-h-dvh grid place-items-center px-4 py-12">
      <div className="w-full max-w-sm space-y-6">
        <Link href="/" className="font-display text-3xl font-extrabold block text-center"><Logo /></Link>
        <div className="rounded-3xl bg-white p-7 shadow-sm space-y-5">
          <div>
            <h1 className="font-display text-3xl font-extrabold">Forgot your password?</h1>
            <p className="text-ink/60 mt-2 text-sm">Enter your email and we&apos;ll send you a link to choose a new one. This also works if you usually sign in with Google and want a password too.</p>
          </div>
          <ForgotForm />
        </div>
        <p className="text-center text-sm text-ink/50">
          <Link href="/signin" className="underline">Back to sign in</Link>
        </p>
      </div>
    </main>
  );
}
