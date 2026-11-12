import { NextResponse, type NextRequest } from "next/server";
import { readSession, adminMfaValid, SESSION_COOKIE } from "@/lib/session";

// Admin area: signed in with an admin Google account AND passed the
// authenticator-app check within the last few hours.
export async function middleware(req: NextRequest) {
  const { pathname, search } = req.nextUrl;
  const session = await readSession(req.cookies.get(SESSION_COOKIE)?.value);
  const isApi = pathname.startsWith("/api/");
  const deny = (to: string, status: number) =>
    isApi ? NextResponse.json({ error: "Not authorised" }, { status }) : NextResponse.redirect(new URL(to, req.url));

  // The 2FA page itself needs an admin session, but not a passed check.
  const twoFactor = pathname === "/admin/2fa" || pathname.startsWith("/api/admin/2fa");

  if (!session) return deny(`/signin?next=${encodeURIComponent(pathname + search)}`, 401);
  if (!session.admin) return deny("/account", 403);
  if (!twoFactor && !adminMfaValid(session)) return deny(`/admin/2fa?next=${encodeURIComponent(pathname + search)}`, 401);
  return NextResponse.next();
}

export const config = { matcher: ["/admin/:path*", "/api/admin/:path*"] };
