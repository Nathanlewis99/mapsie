import Link from "next/link";
import Logo from "@/components/Logo";
import { redirect } from "next/navigation";
import GoogleButton from "@/components/GoogleButton";
import { PasswordForms } from "./PasswordForms";
import { currentUser, googleConfigured, safeNext } from "@/lib/server/auth";

export const dynamic = "force-dynamic";
export const metadata = { title: "Sign in · Mapsie" };

const ERRORS: Record<string, string> = {
  cancelled: "Sign-in was cancelled. Try again whenever you're ready.",
  expired: "That sign-in link expired. Please try again.",
  unverified: "Your Google account's email isn't verified, so we can't use it to sign in.",
  failed: "Something went wrong signing in with Google. Please try again.",
};

export default async function SignIn({ searchParams }: { searchParams: Promise<{ next?: string; error?: string; mode?: string }> }) {
  const { next, error, mode } = await searchParams;
  const dest = safeNext(next);
  if (await currentUser()) redirect(dest);
  return (
    <main className="min-h-dvh grid place-items-center px-4 py-12">
      <div className="w-full max-w-sm space-y-6">
        <Link href="/" className="font-display text-3xl font-extrabold block text-center"><Logo /></Link>
        <div className="rounded-3xl bg-white p-7 shadow-sm space-y-5">
          <div>
            <h1 className="font-display text-3xl font-extrabold">Welcome to Mapsie</h1>
            <p className="text-ink/60 mt-2 text-sm">Save your maps, come back to them on any device, and see your orders.</p>
          </div>
          {error && <p className="rounded-2xl bg-coral/10 px-4 py-3 text-sm font-bold text-coral-dark">{ERRORS[error] ?? ERRORS.failed}</p>}
          {googleConfigured() && (
            <>
              <GoogleButton next={dest} />
              <div className="flex items-center gap-3 text-xs font-bold uppercase tracking-wider text-ink/40">
                <span className="h-px flex-1 bg-ink/10" />or use your email<span className="h-px flex-1 bg-ink/10" />
              </div>
            </>
          )}
          <PasswordForms next={dest} startOn={mode === "signup" ? "signup" : "signin"} />
          <p className="text-xs text-ink/50">
            By continuing you agree to our <Link className="underline" href="/legal/terms">Terms</Link> and{" "}
            <Link className="underline" href="/legal/privacy">Privacy Policy</Link>.
          </p>
        </div>
        <p className="text-center text-sm text-ink/50">
          <Link href="/create" className="underline">Keep designing without an account</Link>
        </p>
      </div>
    </main>
  );
}
