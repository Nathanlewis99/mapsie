import { NextResponse } from "next/server";
import { currentUser, startSession, safeNext } from "@/lib/server/auth";
import { setTotp } from "@/lib/server/db";
import { checkTotp } from "@/lib/server/totp";

// Verify an authenticator code. On first use this also switches 2FA on.
export async function POST(req: Request) {
  const user = await currentUser();
  if (!user?.totpSecret) return NextResponse.json({ error: "Start setup again" }, { status: 400 });
  const { code, next } = (await req.json()) as { code: string; next?: string };
  if (!/^\d{6}$/.test((code ?? "").replace(/\s/g, "")) || !checkTotp(user.totpSecret, user.email, code)) {
    return NextResponse.json({ error: "That code didn't match. Check your authenticator app and try again." }, { status: 400 });
  }
  if (!user.totpEnabled) await setTotp(user.id, user.totpSecret, true);
  await startSession({ ...user, totpEnabled: true }, Math.floor(Date.now() / 1000));
  return NextResponse.json({ ok: true, next: safeNext(next ?? "/admin") });
}
