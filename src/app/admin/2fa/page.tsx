import QRCode from "qrcode";
import { redirect } from "next/navigation";
import { currentUser } from "@/lib/server/auth";
import { setTotp } from "@/lib/server/db";
import { newTotpSecret, totpUri } from "@/lib/server/totp";
import TwoFactorForm from "./TwoFactorForm";

export const dynamic = "force-dynamic";
export const metadata = { title: "Admin sign-in · Mapsie" };

export default async function TwoFactorPage({ searchParams }: { searchParams: Promise<{ next?: string }> }) {
  const { next } = await searchParams;
  const user = await currentUser();
  if (!user) redirect("/signin?next=/admin");

  // First visit: create a secret and show it as a QR code to scan.
  let qr: string | null = null;
  let secret: string | null = null;
  if (!user.totpEnabled) {
    secret = user.totpSecret ?? newTotpSecret();
    if (!user.totpSecret) await setTotp(user.id, secret, false);
    qr = await QRCode.toDataURL(totpUri(secret, user.email), { margin: 1, width: 220 });
  }

  return (
    <main className="min-h-dvh grid place-items-center px-4 py-12">
      <div className="w-full max-w-sm rounded-3xl bg-white p-7 shadow-sm space-y-5">
        <div>
          <div className="text-xs font-extrabold tracking-widest text-coral uppercase">Mapsie admin</div>
          <h1 className="font-display text-3xl font-extrabold mt-1">{qr ? "Set up two-step sign-in" : "Enter your code"}</h1>
          <p className="text-sm text-ink/60 mt-2">Signed in as {user.email}</p>
        </div>
        {qr ? (
          <ol className="space-y-3 text-sm">
            <li>1. Open an authenticator app (Google Authenticator, 1Password, Authy…).</li>
            <li>2. Scan this code:</li>
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src={qr} alt="QR code for your authenticator app" width={220} height={220} className="mx-auto rounded-xl" />
            <li className="text-xs text-ink/50 break-all">
              Can&apos;t scan? Enter this key instead: <code className="font-mono text-ink">{secret}</code>
            </li>
            <li>3. Type the 6-digit code it shows:</li>
          </ol>
        ) : (
          <p className="text-sm text-ink/70">Open your authenticator app and type the 6-digit code for Mapsie.</p>
        )}
        <TwoFactorForm next={next ?? "/admin"} />
      </div>
    </main>
  );
}
